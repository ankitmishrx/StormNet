"""Migration 003: Multi-Source Data Fusion tables and spatial indices.

Revision ID: 003
Revises: 002
Create Date: 2026-09-26 17:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create fused_grid_frames table
    op.create_table(
        "fused_grid_frames",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sector_id", sa.String(length=64), nullable=False, server_default="delhi-ncr"),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("window_end", sa.DateTime(), nullable=False),
        sa.Column("resolution_km", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("data_freshness", sa.String(length=32), nullable=False, server_default="SAMPLE"),
        sa.Column("radar_available", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("satellite_available", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lightning_available", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("atmospheric_available", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completeness_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_cells", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_flag", sa.String(length=32), nullable=False, server_default="VALID"),
        sa.Column("metadata_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_fused_frames_sector_time", "fused_grid_frames", ["sector_id", sa.text("timestamp DESC")])
    op.create_index("idx_fused_frames_timestamp", "fused_grid_frames", ["timestamp"])

    # 2. Create fused_grid_features table
    op.create_table(
        "fused_grid_features",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("frame_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fused_grid_frames.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grid_cell_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("grid_cells.id", ondelete="SET NULL"), nullable=True),
        sa.Column("grid_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=False,
        ),
        sa.Column("radar_reflectivity_dbz", sa.Float(), nullable=True),
        sa.Column("radar_max_dbz", sa.Float(), nullable=True),
        sa.Column("radar_precip_rate_mm_hr", sa.Float(), nullable=True),
        sa.Column("satellite_brightness_temp_k", sa.Float(), nullable=True),
        sa.Column("satellite_cooling_rate_k_hr", sa.Float(), nullable=True),
        sa.Column("lightning_strike_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lightning_density_per_km2", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("lightning_rate_per_min", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("lightning_trend", sa.String(length=32), nullable=False, server_default="STABLE"),
        sa.Column("atmospheric_temp_c", sa.Float(), nullable=True),
        sa.Column("atmospheric_humidity_pct", sa.Float(), nullable=True),
        sa.Column("atmospheric_pressure_hpa", sa.Float(), nullable=True),
        sa.Column("atmospheric_wind_speed_kmh", sa.Float(), nullable=True),
        sa.Column("composite_quality", sa.String(length=32), nullable=False, server_default="VALID"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_fused_features_grid_time", "fused_grid_features", ["grid_id", sa.text("timestamp DESC")])
    op.create_index("idx_fused_features_frame_id", "fused_grid_features", ["frame_id"])
    op.create_index(
        "idx_fused_features_geom_gist",
        "fused_grid_features",
        ["geom"],
        postgresql_using="gist",
    )

    # 3. Create data_source_status table
    op.create_table(
        "data_source_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(length=32), nullable=False, unique=True),
        sa.Column("provider_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ONLINE"),
        sa.Column("latency_seconds", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("last_received_at", sa.DateTime(), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("data_freshness", sa.String(length=32), nullable=False, server_default="SAMPLE"),
        sa.Column("metadata_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_data_source_status_source_type", "data_source_status", ["source_type"])


def downgrade() -> None:
    op.drop_table("data_source_status")
    op.drop_table("fused_grid_features")
    op.drop_table("fused_grid_frames")
