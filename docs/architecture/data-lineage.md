# STORMNET — Data Lineage & Provenance Architecture
**Project:** STORMNET — AI-Powered Convective Nowcasting Platform  
**Problem Statement:** SIH26084 — Convective Scale Nowcasting for Thunderstorms, Hail & Cloudbursts (0–6 hr)  
**Document Reference:** `docs/architecture/data-lineage.md`  

---

## 1. Lineage Philosophy

In weather intelligence and mission-critical disaster management, every hazard warning and nowcast prediction must be fully auditable and reproducible down to the raw physical sensor telemetry. 

STORMNET implements a 5-tier immutable provenance tracking graph for all fused grid frames:

```
[Raw Telemetry]
   |
   +---> Preprocessing Version (e.g. radar_v1.0.0, lln_v1.0.0, insat_v1.0.0)
   |        |
   |        +---> Georeferencing & Spatial Transformation (e.g. EPSG:4326, 4/3 R_E)
   |                 |
   |                 +---> Temporal Alignment & Causal Windowing (e.g. 5-min window, anchor T_0)
   |                          |
   |                          +---> Common Grid Binner (e.g. 3km_grid_v1)
   |                                   |
   v                                   v
[FusedGridFrame] <---------------- Metadata Provenance Manifest (UUID, hashes, config)
```

---

## 2. Lineage Metadata Schema

Each `FusedGridFrame` and exported Parquet partition embeds an immutable `LineageManifest`:

```json
{
  "fused_frame_id": "88888888-8888-8888-8888-888888888888",
  "pipeline_version": "1.0.0",
  "fusion_timestamp": "2026-09-26T15:45:00Z",
  "sector_id": "delhi-ncr",
  "target_grid": {
    "grid_version": "grid_3km_v1",
    "resolution_km": 3.0,
    "crs": "EPSG:4326",
    "bounding_box": [76.5, 28.0, 77.8, 29.2]
  },
  "temporal_window": {
    "window_start": "2026-09-26T15:40:00Z",
    "window_end": "2026-09-26T15:45:00Z",
    "duration_seconds": 300
  },
  "source_lineage": {
    "radar": {
      "source_id": "DWR-DEL-SAF",
      "scan_timestamp": "2026-09-26T15:45:00Z",
      "preprocessing_module": "ml.preprocessing.radar.processors:ReflectivityProcessor",
      "transformation": "column_max_composite",
      "quality_flag": "VALID"
    },
    "satellite": {
      "source_id": "INSAT-3DR-IMD",
      "frame_timestamp": "2026-09-26T15:42:00Z",
      "channel": "TIR1_10.8UM",
      "preprocessing_module": "ml.preprocessing.fusion.satellite_adapter:SatelliteAdapter",
      "quality_flag": "VALID"
    },
    "lightning": {
      "source_id": "IITM-LLN-NCR",
      "events_aggregated": 24,
      "aggregation_window_sec": 300,
      "preprocessing_module": "ml.preprocessing.fusion.lightning_aggregator:LightningAggregator",
      "quality_flag": "VALID"
    },
    "surface_aws": {
      "source_id": "IMD-AWS-NETWORK",
      "active_stations": 6,
      "interpolation_method": "nearest_neighbor",
      "quality_flag": "VALID"
    }
  },
  "sensor_availability": {
    "radar": true,
    "satellite": true,
    "lightning": true,
    "atmospheric": true,
    "completeness_score": 1.0
  }
}
```

---

## 3. Storage and Reproducibility

1. **Database Persistence:** The JSON lineage manifest is stored directly in `fused_grid_frames.metadata_payload` in PostgreSQL.
2. **Parquet Metadata Key:** When exported to scientific Parquet files, the lineage JSON is embedded in the Parquet file-level metadata table (`b"stormnet_lineage"`).
3. **Auditability:** Any anomaly in model predictions can be traced back to the specific sensor ingestion batch and transformation parameters.
