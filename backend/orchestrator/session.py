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
    message: Optional[str] = None # The question/objection if raising hand

@dataclass
class SessionState:
    id: str
    transcript: List[str] = field(default_factory=list)
    agent_states: Dict[str, AgentState] = field(default_factory=dict)
    is_active: bool = True

class LiveSessionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.state: SessionState = SessionState(id="default") # Single session for now
        self.personas: Dict[str, ChallengerPersona] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")
        # Send initial state
        await self.broadcast_state()

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    def set_personas(self, personas: List[ChallengerPersona]) -> None:
        """Initialize agents for the session."""
        self.personas = {p.id: p for p in personas}
        self.state.agent_states = {
            p.id: AgentState(persona_id=p.id) for p in personas
        }
        logger.info(f"Initialized {len(personas)} personas for live session.")

    async def add_transcript_chunk(self, text: str) -> None:
        """Append new text to transcript."""
        if not text.strip():
            return
        self.state.transcript.append(text)
        # In a real app, we might trim history to avoid memory bloat
        
        # Broadcast update (optional, might be too noisy to send every chunk if not displaying it)
        # await self.broadcast_state()

    async def update_agent_state(self, persona_id: str, status: str, message: Optional[str] = None) -> None:
        if persona_id in self.state.agent_states:
            self.state.agent_states[persona_id].status = status
            self.state.agent_states[persona_id].message = message
            await self.broadcast_state()

    async def broadcast_state(self) -> None:
        """Send current state to all clients."""
        if not self.active_connections:
            return

        state_payload = {
            "type": "state_update",
            "data": {
                "transcript_length": len(self.state.transcript),
                "agents": [asdict(s) for s in self.state.agent_states.values()]
            }
        }
        
        message = json.dumps(state_payload)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                # Potentially remove stale connection?
                
# Global instance for now (simplification)
session_manager = LiveSessionManager()
