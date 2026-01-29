import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.orchestrator.loop import OrchestratorLoop
from backend.orchestrator.session import LiveSessionManager, AgentState, SessionState
from backend.models.core import ChallengerPersona

@pytest.mark.asyncio
async def test_orchestrator_decision_logic():
    # Setup Mocks
    mock_session_manager = MagicMock(spec=LiveSessionManager)
    # Mock the state object
    mock_session_manager.state = SessionState(id="test", transcript=[])
    # Mock personas
    mock_session_manager.personas = {
        "skeptic": ChallengerPersona(id="skeptic", name="Skeptic", role="Lead", style="Critical", focus_areas=[])
    }
    # Mock update_agent_state to be async
    mock_session_manager.update_agent_state = AsyncMock()

    # Init Loop
    loop = OrchestratorLoop(session_manager=mock_session_manager)
    
    # Mock LLM response
    # We patch the instance method on the specific object we created
    # Check what type loop.llm is. It is likely MockLLM or OpenAIClient depending on env.
    # We'll just force the complete_structured return value.
    
    with patch.object(loop.llm, 'complete_structured') as mock_complete:
        mock_complete.return_value = {
            "interjection": True,
            "persona_id": "skeptic",
            "message": "I object!"
        }
        
        # Test Input
        mock_session_manager.state.transcript.append("Sensitive Topic")
        
        # Execute
        await loop.process_transcript_update("test")
        
        # Verify
        mock_session_manager.update_agent_state.assert_called_once_with(
            persona_id="skeptic",
            status="raising_hand",
            message="I object!"
        )

@pytest.mark.asyncio
async def test_orchestrator_no_interjection():
    # Setup Mocks
    mock_session_manager = MagicMock(spec=LiveSessionManager)
    mock_session_manager.state = SessionState(id="test", transcript=[])
    mock_session_manager.personas = {
        "skeptic": ChallengerPersona(id="skeptic", name="Skeptic", role="Lead", style="Critical", focus_areas=[])
    }
    mock_session_manager.update_agent_state = AsyncMock()

    loop = OrchestratorLoop(session_manager=mock_session_manager)
    
    with patch.object(loop.llm, 'complete_structured') as mock_complete:
        mock_complete.return_value = {
            "interjection": False
        }
        
        mock_session_manager.state.transcript.append("Boring Topic")
        
        await loop.process_transcript_update("test")
        
        # Verify NO call
        mock_session_manager.update_agent_state.assert_not_called()
