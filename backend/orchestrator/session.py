import logging
import json
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
from dataclasses import dataclass, field, asdict
from backend.models.core import ChallengerPersona

logger = logging.getLogger(__name__)

@dataclass
class AgentState:
    persona_id: str
    status: str = "listening"  # listening, thinking, raising_hand, speaking
    message: Optional[str] = None

@dataclass
class SessionState:
    id: str
    transcript: List[str] = field(default_factory=list)
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    is_active: bool = True

class LiveSessionManager:
    def __init__(self) -> None:
        # Per-session connection lists, states, and personas
        self.connections: Dict[str, List[WebSocket]] = {}
        self.sessions: Dict[str, SessionState] = {}
        self.personas: Dict[str, Dict[str, ChallengerPersona]] = {}

    def register_connection(self, websocket: WebSocket, session_id: str) -> None:
        """Register an accepted WebSocket connection under a session."""
        if session_id not in self.connections:
            self.connections[session_id] = []
        self.connections[session_id].append(websocket)
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(id=session_id)
        logger.info(f"Client registered for session {session_id}. Total: {len(self.connections[session_id])}")

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        if session_id in self.connections:
            if websocket in self.connections[session_id]:
                self.connections[session_id].remove(websocket)
            if not self.connections[session_id]:
                # No more clients for this session — clean up state
                del self.connections[session_id]
                self.sessions.pop(session_id, None)
                self.personas.pop(session_id, None)
        logger.info(f"Client disconnected from session {session_id}")

    def set_personas(self, session_id: str, personas: List[ChallengerPersona]) -> None:
        """Initialize agent states for the session."""
        self.personas[session_id] = {p.id: p for p in personas}
        session = self.sessions.get(session_id)
        if not session:
            session = SessionState(id=session_id)
            self.sessions[session_id] = session
        session.agent_states = {p.id: AgentState(persona_id=p.id) for p in personas}
        logger.info(f"Initialized {len(personas)} personas for session {session_id}")

    def get_personas(self, session_id: str) -> Dict[str, ChallengerPersona]:
        return self.personas.get(session_id, {})

    def get_state(self, session_id: str) -> Optional[SessionState]:
        return self.sessions.get(session_id)

    async def add_transcript_chunk(self, session_id: str, text: str) -> None:
        """Append new text to the session transcript."""
        if not text.strip():
            return
        session = self.sessions.get(session_id)
        if not session:
            session = SessionState(id=session_id)
            self.sessions[session_id] = session
        session.transcript.append(text)

    async def update_agent_state(
        self,
        session_id: str,
        persona_id: str,
        status: str,
        message: Optional[str] = None
    ) -> None:
        session = self.sessions.get(session_id)
        if session and persona_id in session.agent_states:
            session.agent_states[persona_id].status = status
            session.agent_states[persona_id].message = message
            await self.broadcast_state(session_id)

    async def broadcast_state(self, session_id: str) -> None:
        """Send current state to all clients in the session."""
        connections = self.connections.get(session_id, [])
        if not connections:
            return
        session = self.sessions.get(session_id)
        if not session:
            return

        state_payload = {
            "type": "state_update",
            "data": {
                "transcript_length": len(session.transcript),
                "agents": [asdict(s) for s in session.agent_states.values()]
            }
        }
        message = json.dumps(state_payload)

        stale: List[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client in session {session_id}: {e}")
                stale.append(connection)

        for conn in stale:
            self.disconnect(conn, session_id)

# Global instance
session_manager = LiveSessionManager()
