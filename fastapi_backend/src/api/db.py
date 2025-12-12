import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Load env for DATABASE_URL and fallback to postgres_database db_connection.txt defaults
load_dotenv()

def _get_default_db_url() -> str:
    """
    Build a sensible default connection string based on the provided postgres container info.
    The running DB container exposes POSTGRES_URL, but .env is empty per task; default to localhost:5000.
    """
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5000")  # db_connection.txt shows 5000, service runs at 5001 externally
    user = os.getenv("POSTGRES_USER", "appuser")
    password = os.getenv("POSTGRES_PASSWORD", "dbuser123")
    dbname = os.getenv("POSTGRES_DB", "myapp")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

DATABASE_URL = os.getenv("DATABASE_URL") or _get_default_db_url()

# SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Provide a SQLAlchemy DB session as a dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
