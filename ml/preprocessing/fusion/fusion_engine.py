"""Multi-Source Meteorological Data Fusion Engine: Combines Radar, Satellite, Lightning, and AWS."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from ml.preprocessing.fusion.interfaces import (
    FusedGridFrame,
    FusedGridCellFeature,
    QualityFlag,
    DataFreshnessTier,
    TemporalWindow,
    SatelliteObservation,
    LightningObservation,
    AtmosphericObservation,
)
from ml.preprocessing.fusion.temporal_aligner import TemporalAligner
from ml.preprocessing.fusion.lightning_aggregator import LightningGridAggregator
from ml.preprocessing.fusion.lineage import LineageManifest


class MultiSourceFusionEngine:
    """Combines heterogeneous meteorological observations into a unified 1–3 km spatial grid."""

    def __init__(self, grid_size_km: float = 3.0, window_duration_seconds: int = 300):
        self.grid_size_km = grid_size_km
        self.window_duration_seconds = window_duration_seconds
        self.temporal_aligner = TemporalAligner(default_window_seconds=window_duration_seconds)
        self.lightning_aggregator = LightningGridAggregator(grid_size_km=grid_size_km)

    def fuse_frame(
        self,
        anchor_timestamp: datetime,
        grid_cells: List[Dict[str, Any]],
        radar_grid_observations: Optional[List[Dict[str, Any]]] = None,
        satellite_observations: Optional[List[SatelliteObservation]] = None,
        lightning_observations: Optional[List[LightningObservation]] = None,
        atmospheric_observations: Optional[List[AtmosphericObservation]] = None,
        previous_lightning_rates: Optional[Dict[str, float]] = None,
        sector_id: str = "delhi-ncr",
        is_sample: bool = True,
    ) -> FusedGridFrame:
        """Executes multi-source fusion for an observation window [T - delta_t, T].

        Gracefully accommodates missing streams, preserving source-level quality flags.
        """
        # Ensure timezone awareness
        if anchor_timestamp.tzinfo is None:
            anchor_timestamp = anchor_timestamp.replace(tzinfo=timezone.utc)

        window = self.temporal_aligner.create_window(
            anchor_timestamp, duration_seconds=self.window_duration_seconds
        )

        # 1. Determine sensor availability
        radar_available = bool(radar_grid_observations and len(radar_grid_observations) > 0)
        satellite_available = bool(satellite_observations and len(satellite_observations) > 0)
        lightning_available = bool(lightning_observations is not None)  # Even 0 strikes is valid if feed is active
        atmospheric_available = bool(atmospheric_observations and len(atmospheric_observations) > 0)

        active_count = sum([radar_available, satellite_available, lightning_available, atmospheric_available])
        completeness_score = round(active_count / 4.0, 2)

        # 2. Causal temporal filtering
        aligned_sat: List[SatelliteObservation] = []
        if satellite_available and satellite_observations:
            # Satellites have longer latency (up to 30 min)
            nearest_sat = self.temporal_aligner.find_nearest_preceding(
                satellite_observations, anchor_timestamp, max_latency_seconds=1800
            )
            if nearest_sat:
                aligned_sat = [nearest_sat]

        aligned_lightning: List[LightningObservation] = []
        if lightning_observations:
            aligned_lightning = self.temporal_aligner.filter_and_align(
                lightning_observations, window
            )

        aligned_aws: List[AtmosphericObservation] = []
        if atmospheric_available and atmospheric_observations:
            for obs in atmospheric_observations:
                if obs.timestamp <= anchor_timestamp:
                    aligned_aws.append(obs)

        # 3. Aggregate lightning to grid
        lightning_features_by_grid: Dict[str, Dict[str, Any]] = {}
        if lightning_available:
            lightning_features_by_grid = self.lightning_aggregator.aggregate_to_grid(
                aligned_lightning, grid_cells, window, previous_lightning_rates
            )

        # Index radar observations by grid coordinates or nearest point
        radar_by_cell: Dict[str, Dict[str, Any]] = {}
        if radar_available and radar_grid_observations:
            for ro in radar_grid_observations:
                gid = ro.get("grid_id")
                if gid:
                    radar_by_cell[gid] = ro

        # Spatial indexing for nearest AWS station
        aws_by_cell: Dict[str, AtmosphericObservation] = {}
        if aligned_aws:
            for cell in grid_cells:
                clat = cell["center_lat"]
                clon = cell["center_lon"]
                # Find closest AWS station within 50 km
                closest = min(
                    aligned_aws,
                    key=lambda a: (a.latitude - clat) ** 2 + (a.longitude - clon) ** 2,
                )
                aws_by_cell[cell["grid_id"]] = closest

        # 4. Construct fused grid cell records
        fused_cells: List[FusedGridCellFeature] = []

        for cell in grid_cells:
            grid_id = cell["grid_id"]
            clat = cell["center_lat"]
            clon = cell["center_lon"]

            # Initialize feature record
            feature = FusedGridCellFeature(
                grid_id=grid_id,
                timestamp=anchor_timestamp,
                latitude=clat,
                longitude=clon,
                grid_size_km=self.grid_size_km,
            )

            # Radar features
            if radar_available and grid_id in radar_by_cell:
                r_data = radar_by_cell[grid_id]
                feature.radar_reflectivity_dbz = r_data.get("reflectivity_dbz")
                feature.radar_max_dbz = r_data.get("max_dbz", feature.radar_reflectivity_dbz)
                if feature.radar_reflectivity_dbz is not None:
                    # Marshall-Palmer proxy Z = 200 * R^1.6 => R = (10^(Z/10) / 200)^(1/1.6)
                    z_linear = 10.0 ** (feature.radar_reflectivity_dbz / 10.0)
                    feature.radar_precip_rate_mm_hr = round((z_linear / 200.0) ** (1.0 / 1.6), 2)
                    feature.radar_quality = QualityFlag.VALID
                else:
                    feature.radar_quality = QualityFlag.MISSING
            else:
                feature.radar_quality = QualityFlag.MISSING if not radar_available else QualityFlag.VALID

            # Satellite features
            if aligned_sat:
                sat = aligned_sat[0]
                feature.satellite_brightness_temp_k = sat.brightness_temp_kelvin
                feature.satellite_cloud_cooling_rate_k_hr = sat.cooling_rate_kelvin_per_hour
                feature.satellite_quality = sat.quality_flag
            else:
                feature.satellite_quality = QualityFlag.UNAVAILABLE

            # Lightning features
            if lightning_available and grid_id in lightning_features_by_grid:
                ltg = lightning_features_by_grid[grid_id]
                feature.lightning_strike_count = ltg["strike_count"]
                feature.lightning_density_per_km2 = ltg["density_per_km2"]
                feature.lightning_rate_per_min = ltg["rate_per_min"]
                feature.lightning_trend = ltg["trend"]
                feature.lightning_quality = QualityFlag.VALID
            else:
                feature.lightning_quality = QualityFlag.UNAVAILABLE

            # Atmospheric features
            if grid_id in aws_by_cell:
                aws = aws_by_cell[grid_id]
                feature.atmospheric_temp_c = aws.temperature_celsius
                feature.atmospheric_humidity_pct = aws.relative_humidity_pct
                feature.atmospheric_pressure_hpa = aws.pressure_hpa
                feature.atmospheric_wind_speed_kmh = aws.wind_speed_kmh
                feature.atmospheric_quality = aws.quality_flag
            else:
                feature.atmospheric_quality = QualityFlag.UNAVAILABLE

            # Composite cell quality assessment
            if feature.radar_quality == QualityFlag.INVALID:
                feature.composite_quality = QualityFlag.INVALID
            elif completeness_score < 0.5:
                feature.composite_quality = QualityFlag.LOW_QUALITY
            else:
                feature.composite_quality = QualityFlag.VALID

            fused_cells.append(feature)

        frame_id = uuid.uuid4()

        # 5. Build Data Lineage Manifest
        lineage = LineageManifest(
            fused_frame_id=frame_id,
            pipeline_version="1.0.0",
            created_at=datetime.now(timezone.utc),
            sector_id=sector_id,
            grid_version=f"{self.grid_size_km}km_grid_v1",
            grid_size_km=self.grid_size_km,
            crs="EPSG:4326",
            window_start=window.window_start,
            window_end=window.window_end,
            window_duration_seconds=self.window_duration_seconds,
            sources_lineage={
                "radar": {"available": radar_available, "records": len(radar_by_cell)},
                "satellite": {"available": satellite_available, "records": len(aligned_sat)},
                "lightning": {"available": lightning_available, "strikes_aligned": len(aligned_lightning)},
                "atmospheric": {"available": atmospheric_available, "stations_mapped": len(aws_by_cell)},
            },
            sensor_availability={
                "radar": radar_available,
                "satellite": satellite_available,
                "lightning": lightning_available,
                "atmospheric": atmospheric_available,
            },
            completeness_score=completeness_score,
        )

        return FusedGridFrame(
            id=frame_id,
            sector_id=sector_id,
            timestamp=anchor_timestamp,
            window_start=window.window_start,
            window_end=window.window_end,
            resolution_km=self.grid_size_km,
            bounding_box=[76.5, 28.0, 77.8, 29.2],
            data_freshness=DataFreshnessTier.SAMPLE if is_sample else DataFreshnessTier.LIVE,
            radar_available=radar_available,
            satellite_available=satellite_available,
            lightning_available=lightning_available,
            atmospheric_available=atmospheric_available,
            completeness_score=completeness_score,
            cells_count=len(fused_cells),
            cells=fused_cells,
            lineage_metadata=lineage.to_dict(),
        )
