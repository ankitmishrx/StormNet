"""Initial migration creating all 9 core STORMNET models with PostGIS geometries and spatial indexes.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-26 15:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable PostGIS Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    # 2. Storms Table
    op.create_table(
        "storms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("cell_code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("severity_level", sa.String(length=16), nullable=False),
        sa.Column("centroid", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("boundary", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("max_reflectivity_dbz", sa.Float(), nullable=True),
        sa.Column("vertically_integrated_liquid", sa.Float(), nullable=True),
        sa.Column("echo_top_height_km", sa.Float(), nullable=True),
        sa.Column("cell_speed_kmh", sa.Float(), nullable=True),
        sa.Column("cell_bearing_deg", sa.Float(), nullable=True),
        sa.Column("first_detected_at", sa.DateTime(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_storms_centroid_gist", "storms", ["centroid"], postgresql_using="gist")
    op.create_index("idx_storms_boundary_gist", "storms", ["boundary"], postgresql_using="gist")
    op.create_index("idx_storms_status_severity", "storms", ["status", "severity_level"])

    # 3. Storm Tracks Table
    op.create_table(
        "storm_tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("storm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("storms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("track_type", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("lead_time_minutes", sa.Float(), nullable=False),
        sa.Column("location", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("trajectory_segment", geoalchemy2.Geometry(geometry_type="LINESTRING", srid=4326), nullable=True),
        sa.Column("predicted_max_dbz", sa.Float(), nullable=True),
        sa.Column("uncertainty_radius_km", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_storm_tracks_location_gist", "storm_tracks", ["location"], postgresql_using="gist")
    op.create_index("idx_storm_tracks_storm_timestamp", "storm_tracks", ["storm_id", "timestamp"])
    op.create_index("idx_storm_tracks_lead_time", "storm_tracks", ["lead_time_minutes"])

    # 4. Observations Table
    op.create_table(
        "observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("station_code", sa.String(length=64), nullable=True),
        sa.Column("observation_time", sa.DateTime(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
        sa.Column("coverage_area", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("metadata_payload", postgresql.JSONB(), nullable=True),
    )
    op.create_index("idx_observations_time_source", "observations", ["observation_time", "source_type"])
    op.create_index("idx_observations_coverage_gist", "observations", ["coverage_area"], postgresql_using="gist")

    # 5. Grid Cells Table
    op.create_table(
        "grid_cells",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sector_id", sa.String(length=32), nullable=False),
        sa.Column("grid_x", sa.Integer(), nullable=False),
        sa.Column("grid_y", sa.Integer(), nullable=False),
        sa.Column("elevation_m", sa.Float(), nullable=True),
        sa.Column("geometry", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=False),
    )
    op.create_index("idx_grid_cells_geometry_gist", "grid_cells", ["geometry"], postgresql_using="gist")
    op.create_index("idx_grid_cells_sector_coords", "grid_cells", ["sector_id", "grid_x", "grid_y"], unique=True)

    # 6. Model Runs Table
    op.create_table(
        "model_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(length=64), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False),
        sa.Column("sector_id", sa.String(length=32), nullable=False),
        sa.Column("base_time", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("execution_duration_sec", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("parameters", postgresql.JSONB(), nullable=True),
        sa.Column("metrics", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
    )
    op.create_index("idx_model_runs_sector_base", "model_runs", ["sector_id", "base_time"])
    op.create_index("idx_model_runs_status", "model_runs", ["status"])

    # 7. Forecasts Table
    op.create_table(
        "forecasts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("model_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sector_id", sa.String(length=32), nullable=False),
        sa.Column("base_time", sa.DateTime(), nullable=False),
        sa.Column("forecast_time", sa.DateTime(), nullable=False),
        sa.Column("lead_time_minutes", sa.Integer(), nullable=False),
        sa.Column("extent", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("raster_tile_path", sa.String(length=512), nullable=True),
        sa.Column("domain_max_dbz", sa.Float(), nullable=True),
        sa.Column("confidence_index", sa.Float(), nullable=False),
        sa.Column("metrics_summary", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_forecasts_base_lead", "forecasts", ["base_time", "lead_time_minutes"])
    op.create_index("idx_forecasts_forecast_time", "forecasts", ["forecast_time"])
    op.create_index("idx_forecasts_extent_gist", "forecasts", ["extent"], postgresql_using="gist")

    # 8. Hazard Predictions Table
    op.create_table(
        "hazard_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("storm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("storms.id", ondelete="CASCADE"), nullable=True),
        sa.Column("forecast_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("lead_time_minutes", sa.Float(), nullable=False),
        sa.Column("cloudburst_probability", sa.Float(), nullable=False),
        sa.Column("hail_probability", sa.Float(), nullable=False),
        sa.Column("severe_wind_probability", sa.Float(), nullable=False),
        sa.Column("lightning_density_score", sa.Float(), nullable=False),
        sa.Column("max_hail_diameter_cm", sa.Float(), nullable=True),
        sa.Column("peak_wind_gust_kmh", sa.Float(), nullable=True),
        sa.Column("estimated_rainfall_rate_mmh", sa.Float(), nullable=True),
        sa.Column("impact_zone", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_hazard_predictions_storm_time", "hazard_predictions", ["storm_id", "timestamp"])
    op.create_index("idx_hazard_predictions_impact_gist", "hazard_predictions", ["impact_zone"], postgresql_using="gist")
    op.create_index("idx_hazard_predictions_cloudburst_prob", "hazard_predictions", ["cloudburst_probability"])

    # 9. Alerts Table
    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("storm_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("storms.id", ondelete="SET NULL"), nullable=True),
        sa.Column("alert_identifier", sa.String(length=64), nullable=False, unique=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("msg_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("urgency", sa.String(length=16), nullable=False),
        sa.Column("headline", sa.String(length=256), nullable=False),
        sa.Column("description", sa.String(length=2048), nullable=False),
        sa.Column("instruction", sa.String(length=2048), nullable=True),
        sa.Column("affected_jurisdictions", postgresql.JSONB(), nullable=True),
        sa.Column("polygon", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
        sa.Column("effective_from", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_alerts_polygon_gist", "alerts", ["polygon"], postgresql_using="gist")
    op.create_index("idx_alerts_severity_effective", "alerts", ["severity", "effective_from"])

    # 10. Locations Table
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("location_type", sa.String(length=32), nullable=False),
        sa.Column("state", sa.String(length=64), nullable=False),
        sa.Column("district", sa.String(length=64), nullable=True),
        sa.Column("elevation_m", sa.Float(), nullable=True),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("point", geoalchemy2.Geometry(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("boundary", geoalchemy2.Geometry(geometry_type="POLYGON", srid=4326), nullable=True),
    )
    op.create_index("idx_locations_point_gist", "locations", ["point"], postgresql_using="gist")
    op.create_index("idx_locations_boundary_gist", "locations", ["boundary"], postgresql_using="gist")
    op.create_index("idx_locations_type_state", "locations", ["location_type", "state"])


def downgrade() -> None:
    op.drop_table("locations")
    op.drop_table("alerts")
    op.drop_table("hazard_predictions")
    op.drop_table("forecasts")
    op.drop_table("model_runs")
    op.drop_table("grid_cells")
    op.drop_table("observations")
    op.drop_table("storm_tracks")
    op.drop_table("storms")
