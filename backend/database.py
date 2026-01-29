from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from backend.config import config

# connect_args={"check_same_thread": False} is needed for SQLite
connect_args = {}
if "sqlite" in config.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(config.DATABASE_URL, echo=False, connect_args=connect_args)

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
