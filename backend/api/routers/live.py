from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from backend.orchestrator.session import session_manager
from backend.orchestrator.loop import OrchestratorLoop
from backend.challenges.personas import ChallengerRegistry

router = APIRouter(prefix="/live", tags=["live"])

# Initialize Orchestrator with the global session manager
# In a real app, this should be dependency injected or handled in lifespan
orchestrator = OrchestratorLoop(session_manager)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await session_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            
            msg_type = data.get("type")
            
            if msg_type == "init_session":
                # Initialize with specific personas
                received_session_id = data.get("session_id", "default")
                # TODO: In future, use received_session_id to partition state
                persona_ids = data.get("persona_ids", [])
                registry = ChallengerRegistry()
                selected_personas = []
                for pid in persona_ids:
                    p = registry.get_persona(pid)
                    if p:
                        selected_personas.append(p)
                
                # Default if none selected
                if not selected_personas:
                    selected_personas = registry.list_personas()[:2]
                    
                session_manager.set_personas(selected_personas)
                
            elif msg_type == "transcript_chunk":
                text = data.get("text", "")
                await session_manager.add_transcript_chunk(text)
                # Trigger orchestrator (fire and forget / background not easily available in WS loop same way)
                # We can just await it or spawn task
                await orchestrator.process_transcript_update(session_id="default")
                
    except WebSocketDisconnect:
        session_manager.disconnect(websocket)
    except Exception as e:
        # Log error but don't crash server
        print(f"WebSocket error: {e}")
        session_manager.disconnect(websocket)
