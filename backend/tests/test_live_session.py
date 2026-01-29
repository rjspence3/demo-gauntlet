import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.orchestrator.session import session_manager
from backend.orchestrator.loop import orchestrator
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection_and_flow():
    # Patch the orchestrator's LLM to force an interjection decision
    with patch.object(orchestrator.llm, 'complete_structured') as mock_llm:
        # 1. Connect WS
        with client.websocket_connect("/live/ws") as websocket:
            # Check initial state
            data = websocket.receive_json()
            assert data["type"] == "state_update"
            assert data["data"]["transcript_length"] == 0
            
            # 2. Init Session
            # We need valid persona IDs. Skeptic is usually default.
            websocket.send_json({
                "type": "init_session",
                "persona_ids": ["skeptic"]
            })
            
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
