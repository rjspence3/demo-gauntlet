import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.orchestrator.loop import OrchestratorLoop
from backend.orchestrator.session import LiveSessionManager, AgentState, SessionState
from backend.models.core import ChallengerPersona

@pytest.mark.asyncio
async def test_orchestrator_decision_logic():
    # Setup Mocks
    mock_session_manager = MagicMock(spec=LiveSessionManager)
    # Loop calls get_state(session_id) and get_personas(session_id) — configure return values.
    session_state = SessionState(id="test", transcript=[])
    mock_session_manager.get_state.return_value = session_state
    mock_session_manager.get_personas.return_value = {
        "skeptic": ChallengerPersona(id="skeptic", name="Skeptic", role="Lead", style="Critical", focus_areas=[])
    }
    mock_session_manager.update_agent_state = AsyncMock()

    # Init Loop
    loop = OrchestratorLoop(session_manager=mock_session_manager)

    with patch.object(loop.llm, 'complete_structured') as mock_complete:
        mock_complete.return_value = {
            "interjection": True,
            "persona_id": "skeptic",
            "message": "I object!"
        }

        # Populate transcript on the state object returned by get_state().
        session_state.transcript.append("Sensitive Topic")

        await loop.process_transcript_update("test")

        # update_agent_state signature: (session_id, persona_id, status, message)
        mock_session_manager.update_agent_state.assert_called_once_with(
            session_id="test",
            persona_id="skeptic",
            status="raising_hand",
            message="I object!"
        )

@pytest.mark.asyncio
async def test_orchestrator_no_interjection():
    # Setup Mocks
    mock_session_manager = MagicMock(spec=LiveSessionManager)
    session_state = SessionState(id="test", transcript=[])
    mock_session_manager.get_state.return_value = session_state
    mock_session_manager.get_personas.return_value = {
        "skeptic": ChallengerPersona(id="skeptic", name="Skeptic", role="Lead", style="Critical", focus_areas=[])
    }
    mock_session_manager.update_agent_state = AsyncMock()

    loop = OrchestratorLoop(session_manager=mock_session_manager)

    with patch.object(loop.llm, 'complete_structured') as mock_complete:
        mock_complete.return_value = {
            "interjection": False
        }

        session_state.transcript.append("Boring Topic")

        await loop.process_transcript_update("test")

        mock_session_manager.update_agent_state.assert_not_called()
