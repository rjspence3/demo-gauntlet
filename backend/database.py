from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from backend.config import config

# connect_args={"check_same_thread": False} is needed for SQLite
connect_args = {}
if "sqlite" in config.DATABASE_URL:
    connect_args["check_same_thread"] = False

# pool_pre_ping validates a connection before use, and pool_recycle drops it
# after 300s — both required for serverless Postgres (Neon) which closes idle
# connections (~5 min). Without these, the first request after an idle gap hits
# a dead connection and 500s — the exact failure mode for a min=0 service.
engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)

def init_db() -> None:
    """
    Initializes the database by creating all tables.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    """
    with Session(engine) as session:
        yield session
