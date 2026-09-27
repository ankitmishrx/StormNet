"""Database configuration and session lifecycle management."""

from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from apps.api.core.config import settings

# Engine setup
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.POSTGRES_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Optional[Session], None, None]:
    """Dependency provider yielding a scoped database session, or None if offline."""
    try:
        db = SessionLocal()
    except Exception:
        yield None
        return

    try:
        yield db
    finally:
        db.close()
