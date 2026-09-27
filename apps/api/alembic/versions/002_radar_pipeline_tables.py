"""Migration 002: Radar pipeline tables and PostGIS spatial indices.

Revision ID: 002
Revises: 001
Create Date: 2026-09-26 16:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Update grid_cells with grid_id, grid_size_km, center_lat, center_lon
    op.add_column("grid_cells", sa.Column("grid_id", sa.String(length=64), nullable=True))
    op.add_column("grid_cells", sa.Column("grid_size_km", sa.Float(), nullable=False, server_default="3.0"))
    op.add_column("grid_cells", sa.Column("center_lat", sa.Float(), nullable=True))
    op.add_column("grid_cells", sa.Column("center_lon", sa.Float(), nullable=True))
    op.create_index("idx_grid_cells_grid_id", "grid_cells", ["grid_id"], unique=True)

    # 2. Create radar_frames table
    op.create_table(
        "radar_frames",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("radar_id", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="DEVELOPMENT_SAMPLE"),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("product_type", sa.String(length=32), nullable=False, server_default="COMPOSITE_REFLECTIVITY"),
        sa.Column("resolution_km", sa.Float(), nullable=False, server_default="3.0"),
        sa.Column("source_resolution_km", sa.Float(), nullable=True, server_default="0.5"),
        sa.Column("crs", sa.String(length=32), nullable=False, server_default="EPSG:4326"),
        sa.Column("bounding_box", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "coverage_area",
            geoalchemy2.types.Geometry(geometry_type="POLYGON", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="VALIDATED"),
        sa.Column("total_cells_processed", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("max_dbz", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_radar_frames_time_radar", "radar_frames", ["timestamp", "radar_id"])
    op.create_index(
        "idx_radar_frames_coverage_gist",
        "radar_frames",
        ["coverage_area"],
        unique=False,
        postgresql_using="gist",
    )

    # 3. Create radar_observations table
    op.create_table(
        "radar_observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("frame_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("radar_frames.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grid_cell_id", sa.String(length=64), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("reflectivity", sa.Float(), nullable=False),
        sa.Column("quality_flag", sa.String(length=32), nullable=False, server_default="VALID"),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=True,
        ),
    )
    op.create_index("idx_radar_obs_frame_id", "radar_observations", ["frame_id"])
    op.create_index("idx_radar_obs_grid_cell_id", "radar_observations", ["grid_cell_id"])
    op.create_index("idx_radar_obs_time_reflectivity", "radar_observations", ["timestamp", "reflectivity"])
    op.create_index(
        "idx_radar_obs_geometry_gist",
        "radar_observations",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
    )

    # 4. Create radar_products table
    op.create_table(
        "radar_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("frame_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("radar_frames.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_type", sa.String(length=32), nullable=False, server_default="VECTOR_CONTOURS"),
        sa.Column("min_dbz", sa.Float(), nullable=True),
        sa.Column("max_dbz", sa.Float(), nullable=True),
        sa.Column("mean_dbz", sa.Float(), nullable=True),
        sa.Column("geojson_contours", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tile_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_radar_products_frame_id", "radar_products", ["frame_id"])


def downgrade() -> None:
    op.drop_table("radar_products")
    op.drop_table("radar_observations")
    op.drop_table("radar_frames")
    op.drop_index("idx_grid_cells_grid_id", table_name="grid_cells")
    op.drop_column("grid_cells", "center_lon")
    op.drop_column("grid_cells", "center_lat")
    op.drop_column("grid_cells", "grid_size_km")
    op.drop_column("grid_cells", "grid_id")
