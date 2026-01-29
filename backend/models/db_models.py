from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class GameSession(SQLModel, table=True):
    """
    Database model for a game session.
    """
    __tablename__ = "sessions"
    
    id: str = Field(primary_key=True)
    dossier: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    deck_summary: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    slides: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    status: str = Field(default="processing")
    
    challenges: List["DBChallenge"] = Relationship(back_populates="session")

class DBChallengerPersona(SQLModel, table=True):
    """
    Database model for a challenger persona.
    """
    __tablename__ = "challengers"
    
    id: str = Field(primary_key=True)
    name: str
    role: str
    style: str
    focus_areas: List[str] = Field(default=[], sa_column=Column(JSON))
    avatar_paths: Dict[str, str] = Field(default={}, sa_column=Column(JSON))
    domain_tags: List[str] = Field(default=[], sa_column=Column(JSON))
    agent_prompt: str = ""

class DBChallenge(SQLModel, table=True):
    """
    Database model for a challenge.
    """
    __tablename__ = "challenges"
    
    id: str = Field(primary_key=True)
    session_id: str = Field(foreign_key="sessions.id")
    persona_id: str
    question: str
    ideal_answer: str
    difficulty: str
    slide_index: Optional[int] = None
    evidence: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    key_points: List[str] = Field(default=[], sa_column=Column(JSON))
    tone: str = "professional"
    metadata_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    session: Optional[GameSession] = Relationship(back_populates="challenges")

class User(SQLModel, table=True):
    """
    Database model for a user.
    """
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
