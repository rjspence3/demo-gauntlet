"""
Module for storing and retrieving challenger personas.
"""
from typing import List, Optional, Dict, Any
from backend.models.core import ChallengerPersona

class ChallengerStore:
    """
    Manages persistence of challenger personas using the database.
    """
    def __init__(self):
        """
        Initialize the ChallengerStore.
        """
        from backend.database import engine
        self.engine = engine

    def list_personas(self) -> List[ChallengerPersona]:
        """List all stored personas."""
        from sqlmodel import Session, select
        from backend.models.db_models import DBChallengerPersona
        
        with Session(self.engine) as db:
            statement = select(DBChallengerPersona)
            results = db.exec(statement).all()
            return [
                ChallengerPersona(
                    id=p.id,
                    name=p.name,
                    role=p.role,
                    style=p.style,
                    focus_areas=p.focus_areas,
                    avatar_paths=p.avatar_paths,
                    domain_tags=p.domain_tags,
                    agent_prompt=p.agent_prompt
                )
                for p in results
            ]

    def get_persona(self, persona_id: str) -> Optional[ChallengerPersona]:
        """Retrieve a persona by ID."""
        from sqlmodel import Session
        from backend.models.db_models import DBChallengerPersona
        
        with Session(self.engine) as db:
            p = db.get(DBChallengerPersona, persona_id)
            if p:
                return ChallengerPersona(
                    id=p.id,
                    name=p.name,
                    role=p.role,
                    style=p.style,
                    focus_areas=p.focus_areas,
                    avatar_paths=p.avatar_paths,
                    domain_tags=p.domain_tags,
                    agent_prompt=p.agent_prompt
                )
            return None

    def add_persona(self, persona: ChallengerPersona) -> None:
        """Add a new persona."""
        from sqlmodel import Session
        from backend.models.db_models import DBChallengerPersona
        
        with Session(self.engine) as db:
            # Check for duplicate ID
            if db.get(DBChallengerPersona, persona.id):
                raise ValueError(f"Persona with ID {persona.id} already exists.")
            
            db_persona = DBChallengerPersona(
                id=persona.id,
                name=persona.name,
                role=persona.role,
                style=persona.style,
                focus_areas=persona.focus_areas,
                avatar_paths=persona.avatar_paths,
                domain_tags=persona.domain_tags,
                agent_prompt=persona.agent_prompt
            )
            db.add(db_persona)
            db.commit()

    def update_persona(self, persona_id: str, updates: Dict[str, Any]) -> Optional[ChallengerPersona]:
        """Update an existing persona."""
        from sqlmodel import Session
        from backend.models.db_models import DBChallengerPersona
        
        with Session(self.engine) as db:
            p = db.get(DBChallengerPersona, persona_id)
            if not p:
                return None
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(p, key):
                    setattr(p, key, value)
            
            db.add(p)
            db.commit()
            db.refresh(p)
            
            return ChallengerPersona(
                id=p.id,
                name=p.name,
                role=p.role,
                style=p.style,
                focus_areas=p.focus_areas,
                avatar_paths=p.avatar_paths,
                domain_tags=p.domain_tags,
                agent_prompt=p.agent_prompt
            )

    def _save_personas(self, personas: List[ChallengerPersona]) -> None:
        # Deprecated, no-op
        pass
