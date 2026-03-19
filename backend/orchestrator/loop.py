import logging
import asyncio
import json
from typing import Optional, Dict
from backend.orchestrator.session import LiveSessionManager, AgentState
from backend.models.llm import AnthropicClient, OpenAIClient, MockLLM, LLMClient
from backend.config import config
from backend.models.core import ChallengerPersona

logger = logging.getLogger(__name__)

class OrchestratorLoop:
    def __init__(self, session_manager: LiveSessionManager) -> None:
        self.session_manager = session_manager
        self.llm: LLMClient
        self._setup_llm()
        # Per-session processing locks to prevent concurrent LLM calls for the same session
        self._locks: Dict[str, asyncio.Lock] = {}

    def _setup_llm(self) -> None:
        if config.ANTHROPIC_API_KEY:
            self.llm = AnthropicClient(api_key=config.ANTHROPIC_API_KEY, model="claude-sonnet-4-5")
        elif config.OPENAI_API_KEY:
            self.llm = OpenAIClient(api_key=config.OPENAI_API_KEY, model="gpt-4o")
        else:
            logger.warning("No LLM API key found. Using Mock LLM for Orchestrator.")
            self.llm = MockLLM()

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    async def process_transcript_update(self, session_id: str) -> None:
        """
        Called when new transcript data arrives for a session.
        Decides if it's time to run an evaluation.
        """
        lock = self._get_lock(session_id)
        if lock.locked():
            return

        async with lock:
            await self._evaluate_interjection(session_id)

    async def _evaluate_interjection(self, session_id: str) -> None:
        session = self.session_manager.get_state(session_id)
        if not session:
            return

        full_text = "\n".join(session.transcript)
        if not full_text:
            return

        context_window = full_text[-2000:]

        active_personas = self.session_manager.get_personas(session_id).values()
        if not active_personas:
            return

        personas_desc = "\n\n".join([
            f"ID: {p.id}\nName: {p.name}\nRole: {p.role}\nStyle: {p.style}\nPrompt: {p.agent_prompt}"
            for p in active_personas
        ])

        system_prompt = f"""You are the Orchestrator for a live presentation simulation.
Your goal is to decide if ONE of the AI personas should interrupt the presenter right now.

Active Personas:
{personas_desc}

RULES:
1. ONLY interrupt if the presenter has just made a controversial claim, a factual error, or said something that specifically triggers a persona's core concerns.
2. Do NOT interrupt just to be polite or agree.
3. If multiple personas want to speak, pick the most relevant one.
4. If no one strictly needs to speak, return "interjection": false.
5. Be "shy" - bias towards NOT interrupting unless necessary.

Output JSON format:
{{
    "interjection": boolean,
    "persona_id": "string (id of the agent) or null",
    "reason": "string explanation",
    "message": "string (the short text the agent wants to say/display)"
}}
"""

        user_prompt = f"Current Transcript (most recent last):\n...{context_window}\n\nShould anyone interject?"

        try:
            response = await asyncio.to_thread(
                self.llm.complete_structured,
                prompt=user_prompt,
                schema={"interjection": True}
            )

            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except Exception:
                    logger.error(f"Failed to parse Orchestrator JSON: {response}")
                    return
            else:
                data = response

            if data.get("interjection"):
                pid = data.get("persona_id")
                msg = data.get("message")
                logger.info(f"Orchestrator [{session_id}]: {pid} wants to interject: {msg}")
                if pid and msg:
                    await self.session_manager.update_agent_state(
                        session_id=session_id,
                        persona_id=pid,
                        status="raising_hand",
                        message=msg
                    )

        except Exception as e:
            logger.error(f"Error in Orchestrator loop for session {session_id}: {e}")
