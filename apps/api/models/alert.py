"""Database model for Common Alerting Protocol (CAP) meteorological warnings."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from apps.api.core.database import Base


class Alert(Base):
    """Actionable CAP-compliant warnings dispatched to emergency management authorities."""

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storm_id = Column(UUID(as_uuid=True), ForeignKey("storms.id", ondelete="SET NULL"), nullable=True, index=True)

    alert_identifier = Column(String(64), unique=True, nullable=False, index=True)  # e.g., CAP-IN-DL-2026-084-001
    status = Column(String(32), nullable=False, default="ACTUAL")  # ACTUAL, EXERCISE, DRAFT
    msg_type = Column(String(32), nullable=False, default="ALERT")  # ALERT, UPDATE, CANCEL
    severity = Column(String(16), nullable=False)  # GREEN, YELLOW, ORANGE, RED
    urgency = Column(String(16), nullable=False, default="IMMEDIATE")  # IMMEDIATE, EXPECTED, FUTURE

    headline = Column(String(256), nullable=False)
    description = Column(String(2048), nullable=False)
    instruction = Column(String(2048), nullable=True)

    affected_jurisdictions = Column(JSONB, nullable=True)  # States, districts, taluks
    polygon = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)

    effective_from = Column(DateTime, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_alerts_polygon_gist", polygon, postgresql_using="gist"),
        Index("idx_alerts_severity_effective", severity, effective_from),
    )
