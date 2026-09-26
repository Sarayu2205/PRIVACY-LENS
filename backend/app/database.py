"""
PrivacyLens – Database session management (SQLAlchemy + MySQL).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Reconnect on stale connections
    pool_recycle=3600,        # Recycle connections every hour
    echo=False,               # Set True for SQL debug output
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency – yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables (used during startup if needed)."""
    from app.models import user, scan, finding, report  # noqa: F401
    Base.metadata.create_all(bind=engine)
