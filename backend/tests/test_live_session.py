import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.orchestrator.session import session_manager
from backend.api.routers.live import orchestrator
from backend.services.auth import create_access_token
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_websocket_connection_and_flow():
    # Generate a valid JWT for the WebSocket connection (P1-6 fix requires token)
    token = create_access_token(data={"sub": "test@demo.com"})

    # Patch the orchestrator's LLM to force an interjection decision
    with patch.object(orchestrator.llm, 'complete_structured') as mock_llm:
        # 1. Connect WS with auth token as query parameter
        with client.websocket_connect(f"/live/ws?token={token}") as websocket:
            # 2. Init Session — state broadcast happens after init, not on raw connect
            websocket.send_json({
                "type": "init_session",
                "session_id": "test-session-live",
                "persona_ids": ["skeptic"]
            })

            # Receive state broadcast triggered by init_session
            data = websocket.receive_json()
            assert data["type"] == "state_update"
            assert data["data"]["transcript_length"] == 0
            
            # 3. Send Transcript Chunk
            # Mock LLM to return an interjection
            mock_llm.return_value = {
                "interjection": True,
                "persona_id": "skeptic",
                "reason": "Test reason",
                "message": "I have an objection."
            }
            
            websocket.send_json({
                "type": "transcript_chunk",
                "text": "We are going to rewrite everything in Assembly."
            })
            
            # 4. Wait for state update (broadcast)
            # The orchestrator runs in background, but in test client it might be sync or need wait
            # Since `process_transcript_update` is awaited in the router, it should happen before next receive if we are lucky,
            # BUT the router awaits `process_transcript_update` which puts it largely effectively sync for the test flow 
            # (although it uses a lock).
            
            # The Loop code: 
            # await self._evaluate_interjection(session_id)
            #   -> await self.session_manager.update_agent_state(...)
            #      -> await self.broadcast_state()
            
            # So we should receive a state update
            data = websocket.receive_json()
            assert data["type"] == "state_update"
            agents = data["data"]["agents"]
            skeptic = next((a for a in agents if a["persona_id"] == "skeptic"), None)
            
            assert skeptic is not None
            assert skeptic["status"] == "raising_hand"
            assert skeptic["message"] == "I have an objection."
