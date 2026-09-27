"""Repository for Multi-Source Fused Frames and Grid Features with PostGIS support and offline fallback."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from apps.api.models.fused_grid_frame import FusedGridFrameModel
from apps.api.models.fused_grid_feature import FusedGridFeatureModel
from apps.api.models.data_source_status import DataSourceStatusModel
from apps.api.schemas.fusion import (
    FusedCellFeatureDTO,
    FusedFrameDetailResponse,
    FusedGridCellHistoryResponse,
    DataSourceStatusDTO,
    FusionNetworkStatusResponse,
)


class FusionRepository:
    """PostGIS queries and robust sample fallback provider for meteorological fusion."""

    def __init__(self, db: Optional[Session]):
        self.db = db

    def get_latest_frame(self, sector_id: str = "delhi-ncr") -> FusedFrameDetailResponse:
        """Retrieves the latest synchronized fused grid frame."""
        if self.db is not None:
            try:
                frame_rec = (
                    self.db.query(FusedGridFrameModel)
                    .filter(FusedGridFrameModel.sector_id == sector_id)
                    .order_by(FusedGridFrameModel.timestamp.desc())
                    .first()
                )
                if frame_rec:
                    features = (
                        self.db.query(FusedGridFeatureModel)
                        .filter(FusedGridFeatureModel.frame_id == frame_rec.id)
                        .all()
                    )
                    cells = [
                        FusedCellFeatureDTO(
                            grid_id=f.grid_id,
                            latitude=f.latitude,
                            longitude=f.longitude,
                            radar_reflectivity_dbz=f.radar_reflectivity_dbz,
                            radar_max_dbz=f.radar_max_dbz,
                            radar_precip_rate_mm_hr=f.radar_precip_rate_mm_hr,
                            satellite_brightness_temp_k=f.satellite_brightness_temp_k,
                            satellite_cooling_rate_k_hr=f.satellite_cooling_rate_k_hr,
                            lightning_strike_count=f.lightning_strike_count,
                            lightning_density_per_km2=f.lightning_density_per_km2,
                            lightning_rate_per_min=f.lightning_rate_per_min,
                            lightning_trend=f.lightning_trend,
                            atmospheric_temp_c=f.atmospheric_temp_c,
                            atmospheric_humidity_pct=f.atmospheric_humidity_pct,
                            atmospheric_pressure_hpa=f.atmospheric_pressure_hpa,
                            atmospheric_wind_speed_kmh=f.atmospheric_wind_speed_kmh,
                            composite_quality=f.composite_quality,
                        )
                        for f in features
                    ]
                    return FusedFrameDetailResponse(
                        id=frame_rec.id,
                        sector_id=frame_rec.sector_id,
                        timestamp=frame_rec.timestamp,
                        window_start=frame_rec.window_start,
                        window_end=frame_rec.window_end,
                        resolution_km=frame_rec.resolution_km,
                        data_freshness=frame_rec.data_freshness,
                        radar_available=frame_rec.radar_available,
                        satellite_available=frame_rec.satellite_available,
                        lightning_available=frame_rec.lightning_available,
                        atmospheric_available=frame_rec.atmospheric_available,
                        completeness_score=frame_rec.completeness_score,
                        total_cells=len(cells),
                        cells=cells,
                        lineage_metadata=frame_rec.metadata_payload,
                    )
            except Exception:
                pass

        return self._generate_sample_frame()

    def get_frame_by_timestamp(
        self, target_time: datetime, sector_id: str = "delhi-ncr"
    ) -> Optional[FusedFrameDetailResponse]:
        """Retrieves a specific fused frame closest to target timestamp."""
        if self.db is not None:
            try:
                frame_rec = (
                    self.db.query(FusedGridFrameModel)
                    .filter(
                        FusedGridFrameModel.sector_id == sector_id,
                        FusedGridFrameModel.timestamp <= target_time,
                    )
                    .order_by(FusedGridFrameModel.timestamp.desc())
                    .first()
                )
                if frame_rec:
                    features = (
                        self.db.query(FusedGridFeatureModel)
                        .filter(FusedGridFeatureModel.frame_id == frame_rec.id)
                        .all()
                    )
                    cells = [
                        FusedCellFeatureDTO(
                            grid_id=f.grid_id,
                            latitude=f.latitude,
                            longitude=f.longitude,
                            radar_reflectivity_dbz=f.radar_reflectivity_dbz,
                            radar_max_dbz=f.radar_max_dbz,
                            radar_precip_rate_mm_hr=f.radar_precip_rate_mm_hr,
                            satellite_brightness_temp_k=f.satellite_brightness_temp_k,
                            satellite_cooling_rate_k_hr=f.satellite_cooling_rate_k_hr,
                            lightning_strike_count=f.lightning_strike_count,
                            lightning_density_per_km2=f.lightning_density_per_km2,
                            lightning_rate_per_min=f.lightning_rate_per_min,
                            lightning_trend=f.lightning_trend,
                            atmospheric_temp_c=f.atmospheric_temp_c,
                            atmospheric_humidity_pct=f.atmospheric_humidity_pct,
                            atmospheric_pressure_hpa=f.atmospheric_pressure_hpa,
                            atmospheric_wind_speed_kmh=f.atmospheric_wind_speed_kmh,
                            composite_quality=f.composite_quality,
                        )
                        for f in features
                    ]
                    return FusedFrameDetailResponse(
                        id=frame_rec.id,
                        sector_id=frame_rec.sector_id,
                        timestamp=frame_rec.timestamp,
                        window_start=frame_rec.window_start,
                        window_end=frame_rec.window_end,
                        resolution_km=frame_rec.resolution_km,
                        data_freshness=frame_rec.data_freshness,
                        radar_available=frame_rec.radar_available,
                        satellite_available=frame_rec.satellite_available,
                        lightning_available=frame_rec.lightning_available,
                        atmospheric_available=frame_rec.atmospheric_available,
                        completeness_score=frame_rec.completeness_score,
                        total_cells=len(cells),
                        cells=cells,
                        lineage_metadata=frame_rec.metadata_payload,
                    )
            except Exception:
                pass

        sample = self._generate_sample_frame()
        sample.timestamp = target_time
        return sample

    def get_grid_cell_history(
        self, grid_id: str, limit: int = 12
    ) -> FusedGridCellHistoryResponse:
        """Retrieves chronological feature history for a single 1–3 km grid cell."""
        if self.db is not None:
            try:
                features = (
                    self.db.query(FusedGridFeatureModel)
                    .filter(FusedGridFeatureModel.grid_id == grid_id)
                    .order_by(FusedGridFeatureModel.timestamp.desc())
                    .limit(limit)
                    .all()
                )
                if features:
                    history = [
                        FusedCellFeatureDTO(
                            grid_id=f.grid_id,
                            latitude=f.latitude,
                            longitude=f.longitude,
                            radar_reflectivity_dbz=f.radar_reflectivity_dbz,
                            radar_max_dbz=f.radar_max_dbz,
                            radar_precip_rate_mm_hr=f.radar_precip_rate_mm_hr,
                            satellite_brightness_temp_k=f.satellite_brightness_temp_k,
                            satellite_cooling_rate_k_hr=f.satellite_cooling_rate_k_hr,
                            lightning_strike_count=f.lightning_strike_count,
                            lightning_density_per_km2=f.lightning_density_per_km2,
                            lightning_rate_per_min=f.lightning_rate_per_min,
                            lightning_trend=f.lightning_trend,
                            atmospheric_temp_c=f.atmospheric_temp_c,
                            atmospheric_humidity_pct=f.atmospheric_humidity_pct,
                            atmospheric_pressure_hpa=f.atmospheric_pressure_hpa,
                            atmospheric_wind_speed_kmh=f.atmospheric_wind_speed_kmh,
                            composite_quality=f.composite_quality,
                        )
                        for f in features
                    ]
                    return FusedGridCellHistoryResponse(
                        grid_id=grid_id,
                        latitude=features[0].latitude,
                        longitude=features[0].longitude,
                        history=history,
                    )
            except Exception:
                pass

        # Sample cell history
        now = datetime.now(timezone.utc)
        history = [
            FusedCellFeatureDTO(
                grid_id=grid_id,
                latitude=28.6328,
                longitude=77.2183,
                radar_reflectivity_dbz=61.5,
                radar_max_dbz=61.5,
                radar_precip_rate_mm_hr=64.2,
                satellite_brightness_temp_k=218.4,
                satellite_cooling_rate_k_hr=-14.5,
                lightning_strike_count=18,
                lightning_density_per_km2=2.0,
                lightning_rate_per_min=3.6,
                lightning_trend="INCREASING",
                atmospheric_temp_c=34.2,
                atmospheric_humidity_pct=74.5,
                atmospheric_pressure_hpa=1004.2,
                atmospheric_wind_speed_kmh=28.0,
                composite_quality="VALID",
            )
        ]
        return FusedGridCellHistoryResponse(
            grid_id=grid_id, latitude=28.6328, longitude=77.2183, history=history
        )

    def get_network_status(self, sector_id: str = "delhi-ncr") -> FusionNetworkStatusResponse:
        """Retrieves health status across all registered sensor modalities."""
        sources = self.get_sources_status()
        active_count = sum(1 for s in sources if s.is_available)
        ratio = round(active_count / len(sources), 2) if sources else 0.0

        return FusionNetworkStatusResponse(
            sector_id=sector_id,
            active_sources_count=active_count,
            total_sources_count=len(sources),
            network_completeness_ratio=ratio,
            data_freshness="SAMPLE",
            last_fusion_timestamp=datetime.now(timezone.utc),
            sources=sources,
            disclaimer="DEVELOPMENT / SAMPLE MULTI-SOURCE FEEDS ONLY (SIH26084)",
        )

    def get_sources_status(self) -> List[DataSourceStatusDTO]:
        """Returns detailed status for each individual sensor modality."""
        now = datetime.now(timezone.utc)
        return [
            DataSourceStatusDTO(
                source_type="RADAR",
                provider_name="IMD Safdarjung C-Band DWR (DWR-DEL-SAF)",
                status="ONLINE",
                latency_seconds=120.0,
                last_received_at=now,
                is_available=True,
                data_freshness="SAMPLE",
                metadata_payload={"frequency_ghz": 5.6, "product": "COMPOSITE_REFLECTIVITY"},
            ),
            DataSourceStatusDTO(
                source_type="SATELLITE",
                provider_name="ISRO/IMD INSAT-3DR Rapid Sector",
                status="ONLINE",
                latency_seconds=180.0,
                last_received_at=now - timedelta(minutes=3),
                is_available=True,
                data_freshness="SAMPLE",
                metadata_payload={"channel": "TIR1_10.8UM", "resolution_km": 4.0},
            ),
            DataSourceStatusDTO(
                source_type="LIGHTNING",
                provider_name="IITM Earth Networks LLN Delhi",
                status="ONLINE",
                latency_seconds=15.0,
                last_received_at=now,
                is_available=True,
                data_freshness="SAMPLE",
                metadata_payload={"sensors_active": 8, "event_types": ["CG", "IC"]},
            ),
            DataSourceStatusDTO(
                source_type="AWS",
                provider_name="IMD Surface Automatic Weather Station Network",
                status="ONLINE",
                latency_seconds=300.0,
                last_received_at=now - timedelta(minutes=5),
                is_available=True,
                data_freshness="SAMPLE",
                metadata_payload={"active_stations": 4, "coverage": "NCR_CORE"},
            ),
        ]

    def _generate_sample_frame(self) -> FusedFrameDetailResponse:
        """Generates validated development sample fused frame."""
        now = datetime.now(timezone.utc)
        fid = uuid.UUID("77777777-7777-7777-7777-777777777777")
        cells = [
            FusedCellFeatureDTO(
                grid_id="GRID-NCR-001",
                latitude=28.6328,
                longitude=77.2183,
                radar_reflectivity_dbz=61.5,
                radar_max_dbz=61.5,
                radar_precip_rate_mm_hr=64.2,
                satellite_brightness_temp_k=218.4,
                satellite_cooling_rate_k_hr=-14.5,
                lightning_strike_count=18,
                lightning_density_per_km2=2.0,
                lightning_rate_per_min=3.6,
                lightning_trend="INCREASING",
                atmospheric_temp_c=34.2,
                atmospheric_humidity_pct=74.5,
                atmospheric_pressure_hpa=1004.2,
                atmospheric_wind_speed_kmh=28.0,
                composite_quality="VALID",
            ),
            FusedCellFeatureDTO(
                grid_id="GRID-NCR-002",
                latitude=28.6328,
                longitude=77.1912,
                radar_reflectivity_dbz=57.0,
                radar_max_dbz=57.0,
                radar_precip_rate_mm_hr=42.1,
                satellite_brightness_temp_k=222.1,
                satellite_cooling_rate_k_hr=-11.2,
                lightning_strike_count=12,
                lightning_density_per_km2=1.33,
                lightning_rate_per_min=2.4,
                lightning_trend="INCREASING",
                atmospheric_temp_c=33.8,
                atmospheric_humidity_pct=78.0,
                atmospheric_pressure_hpa=1003.8,
                atmospheric_wind_speed_kmh=34.5,
                composite_quality="VALID",
            ),
            FusedCellFeatureDTO(
                grid_id="GRID-NCR-003",
                latitude=28.4595,
                longitude=77.0266,
                radar_reflectivity_dbz=53.2,
                radar_max_dbz=53.2,
                radar_precip_rate_mm_hr=28.6,
                satellite_brightness_temp_k=228.6,
                satellite_cooling_rate_k_hr=-8.0,
                lightning_strike_count=5,
                lightning_density_per_km2=0.55,
                lightning_rate_per_min=1.0,
                lightning_trend="STABLE",
                atmospheric_temp_c=33.2,
                atmospheric_humidity_pct=81.0,
                atmospheric_pressure_hpa=1003.5,
                atmospheric_wind_speed_kmh=42.0,
                composite_quality="VALID",
            ),
            FusedCellFeatureDTO(
                grid_id="GRID-NCR-004",
                latitude=28.9845,
                longitude=77.7064,
                radar_reflectivity_dbz=44.0,
                radar_max_dbz=44.0,
                radar_precip_rate_mm_hr=11.4,
                satellite_brightness_temp_k=242.0,
                satellite_cooling_rate_k_hr=-3.5,
                lightning_strike_count=0,
                lightning_density_per_km2=0.0,
                lightning_rate_per_min=0.0,
                lightning_trend="STABLE",
                atmospheric_temp_c=35.1,
                atmospheric_humidity_pct=69.0,
                atmospheric_pressure_hpa=1004.8,
                atmospheric_wind_speed_kmh=18.0,
                composite_quality="VALID",
            ),
        ]

        return FusedFrameDetailResponse(
            id=fid,
            sector_id="delhi-ncr",
            timestamp=now,
            window_start=now - timedelta(minutes=5),
            window_end=now,
            resolution_km=3.0,
            data_freshness="SAMPLE",
            radar_available=True,
            satellite_available=True,
            lightning_available=True,
            atmospheric_available=True,
            completeness_score=1.0,
            total_cells=len(cells),
            cells=cells,
            lineage_metadata={
                "pipeline_version": "1.0.0",
                "sector": "delhi-ncr",
                "sources_fused": ["DWR-DEL-SAF", "INSAT-3DR", "IITM_NCR_LLN", "IMD_DELHI_AWS"],
                "is_sample": True,
            },
        )
