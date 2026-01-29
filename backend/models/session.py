"""
Module for managing session data persistence.
"""
from typing import Optional, Any, Dict, List
from dataclasses import asdict
from backend.models.core import ResearchDossier, Challenge, Slide

class SessionStore:
    """
    Manages database storage for session data.
    """
    def __init__(self):
        """
        Initialize the SessionStore.
        """
        from backend.database import engine
        self.engine = engine

    def _get_or_create_session(self, db: Any, session_id: str) -> Any:
        from backend.models.db_models import GameSession
        session = db.get(GameSession, session_id)
        if not session:
            session = GameSession(id=session_id)
            db.add(session)
        return session

    def save_dossier(self, session_id: str, dossier: ResearchDossier) -> None:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = self._get_or_create_session(db, session_id)
            session.dossier = asdict(dossier)
            db.commit()

    def get_dossier(self, session_id: str) -> Optional[ResearchDossier]:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = db.get(GameSession, session_id)
            if session and session.dossier:
                return ResearchDossier(**session.dossier)
            return None

    def save_deck_summary(self, session_id: str, summary: str) -> None:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = self._get_or_create_session(db, session_id)
            session.deck_summary = summary
            db.commit()

    def get_deck_summary(self, session_id: str) -> Optional[str]:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = db.get(GameSession, session_id)
            if session:
                return session.deck_summary
            return None

    def save_interaction(self, session_id: str, interaction: Dict[str, Any]) -> None:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = self._get_or_create_session(db, session_id)
            # SQLAlchemy JSON type might not track mutations automatically if we just append
            # So we create a new list
            history = list(session.history) if session.history else []
            history.append(interaction)
            session.history = history
            db.commit()

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = db.get(GameSession, session_id)
            if session and session.history:
                return session.history
            return []

    def save_challenges(self, session_id: str, challenges: List[Challenge]) -> None:
        from sqlmodel import Session
        from backend.models.db_models import DBChallenge, GameSession
        
        with Session(self.engine) as db:
            # Ensure session exists
            self._get_or_create_session(db, session_id)
            
            for ch in challenges:
                # Check if exists
                existing = db.get(DBChallenge, ch.id)
                if existing:
                    # Update
                    existing.question = ch.question
                    existing.ideal_answer = ch.ideal_answer
                    existing.difficulty = ch.difficulty
                    existing.slide_index = ch.slide_index
                    existing.evidence = ch.evidence
                    existing.key_points = ch.key_points
                    existing.tone = ch.tone
                    existing.metadata_json = ch.metadata
                else:
                    # Create
                    db_ch = DBChallenge(
                        id=ch.id,
                        session_id=session_id,
                        persona_id=ch.persona_id,
                        question=ch.question,
                        ideal_answer=ch.ideal_answer,
                        difficulty=ch.difficulty,
                        slide_index=ch.slide_index,
                        evidence=ch.evidence,
                        key_points=ch.key_points,
                        tone=ch.tone,
                        metadata_json=ch.metadata
                    )
                    db.add(db_ch)
            db.commit()

    def get_challenge(self, session_id: str, challenge_id: str) -> Optional[Challenge]:
        from sqlmodel import Session
        from backend.models.db_models import DBChallenge
        
        with Session(self.engine) as db:
            ch = db.get(DBChallenge, challenge_id)
            if ch and ch.session_id == session_id:
                return Challenge(
                    id=ch.id,
                    session_id=ch.session_id,
                    persona_id=ch.persona_id,
                    question=ch.question,
                    ideal_answer=ch.ideal_answer,
                    difficulty=ch.difficulty,
                    slide_index=ch.slide_index,
                    evidence=ch.evidence,
                    key_points=ch.key_points,
                    tone=ch.tone,
                    metadata=ch.metadata_json
                )
            return None

    def get_challenges(self, session_id: str) -> List[Challenge]:
        from sqlmodel import Session, select
        from backend.models.db_models import DBChallenge
        
        with Session(self.engine) as db:
            statement = select(DBChallenge).where(DBChallenge.session_id == session_id)
            results = db.exec(statement).all()
            return [
                Challenge(
                    id=ch.id,
                    session_id=ch.session_id,
                    persona_id=ch.persona_id,
                    question=ch.question,
                    ideal_answer=ch.ideal_answer,
                    difficulty=ch.difficulty,
                    slide_index=ch.slide_index,
                    evidence=ch.evidence,
                    key_points=ch.key_points,
                    tone=ch.tone,
                    metadata=ch.metadata_json
                )
                for ch in results
            ]

    def save_slides(self, session_id: str, slides: List[Slide]) -> None:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = self._get_or_create_session(db, session_id)
            session.slides = [asdict(s) for s in slides]
            db.commit()

    def get_slides(self, session_id: str) -> List[Slide]:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = db.get(GameSession, session_id)
            if session and session.slides:
                return [Slide(**s) for s in session.slides]
            return []

    def update_session_status(self, session_id: str, status: str) -> None:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = self._get_or_create_session(db, session_id)
            session.status = status
            db.commit()

    def get_session_status(self, session_id: str) -> str:
        from sqlmodel import Session
        from backend.models.db_models import GameSession
        
        with Session(self.engine) as db:
            session = db.get(GameSession, session_id)
            if session:
                return session.status
            return "unknown"
