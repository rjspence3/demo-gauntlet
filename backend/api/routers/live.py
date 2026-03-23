from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.orchestrator.session import session_manager
from backend.orchestrator.loop import OrchestratorLoop
from backend.challenges.personas import ChallengerRegistry

router = APIRouter(prefix="/live", tags=["live"])

orchestrator = OrchestratorLoop(session_manager)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id: str | None = None
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "init_session":
                session_id = data.get("session_id", "default")
                persona_ids = data.get("persona_ids", [])
                registry = ChallengerRegistry()
                selected_personas = [p for pid in persona_ids if (p := registry.get_persona(pid))]
                if not selected_personas:
                    selected_personas = registry.list_personas()[:2]

                session_manager.register_connection(websocket, session_id)
                session_manager.set_personas(session_id, selected_personas)
                await session_manager.broadcast_state(session_id)

            elif msg_type == "transcript_chunk" and session_id:
                text = data.get("text", "")
                await session_manager.add_transcript_chunk(session_id, text)
                await orchestrator.process_transcript_update(session_id)

    except WebSocketDisconnect:
        if session_id:
            session_manager.disconnect(websocket, session_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WebSocket error: {e}")
        if session_id:
            session_manager.disconnect(websocket, session_id)
