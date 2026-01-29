import logging
import asyncio
import json
from typing import Optional, List, Dict, Any
from backend.orchestrator.session import LiveSessionManager, AgentState
from backend.models.llm import OpenAIClient, MockLLM, LLMClient
from backend.config import config
from backend.models.core import ChallengerPersona

logger = logging.getLogger(__name__)

class OrchestratorLoop:
    def __init__(self, session_manager: LiveSessionManager) -> None:
        self.session_manager = session_manager
        self.llm: LLMClient
        self._setup_llm()
        self.processing_lock = asyncio.Lock()

    def _setup_llm(self) -> None:
        if config.OPENAI_API_KEY:
            # use a faster model for the loop if possible, e.g. gpt-4o-mini or gpt-3.5-turbo
            # for now defaulting to standard config, but ideally should be configurable
            self.llm = OpenAIClient(api_key=config.OPENAI_API_KEY, model="gpt-4o")
        else:
            logger.warning("No OpenAI API key found. Using Mock LLM for Orchestrator.")
            self.llm = MockLLM()

    async def process_transcript_update(self, session_id: str) -> None:
        """
        Called when new transcript data arrives.
        Decides if it's time to run an evaluation.
        """
        # Simple debounce/check:
        # In a real system, we'd check if we have enough new tokens since last run.
        # For this demo, we'll run on every significant chunk or throttle elsewhere.
        
        # We use a lock to prevent concurrent LLM calls for the same session (race conditions)
        if self.processing_lock.locked():
            return

        async with self.processing_lock:
            await self._evaluate_interjection(session_id)

    async def _evaluate_interjection(self, session_id: str) -> None:
        session = self.session_manager.state # Simplified: assume single session state
        
        # Get recent context (last 2000 chars approx)
        full_text = "\n".join(session.transcript)
        if not full_text:
            return
            
        context_window = full_text[-2000:]
        
        # Construct Prompt
        # We need to know which personas are active
        active_personas = self.session_manager.personas.values()
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
            # Run LLM
            # Note: This is a blocking call in the synchronous structure of LLMClient, 
            # ideally LLMClient would be async. For now we run in executor if needed, 
            # but standard OpenAI client is sync. 
            # We'll rely on fast models or async wrapper in future.
            # Using to_thread for safety.
            response = await asyncio.to_thread(
                self.llm.complete_structured, 
                prompt=user_prompt, 
                schema={"interjection": True} # Dummy schema hint
            )
            
            # If using MockLLM or if complete_structured returns dict directly:
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except:
                    logger.error(f"Failed to parse Orchestrator JSON: {response}")
                    return
            else:
                data = response

            if data.get("interjection"):
                pid = data.get("persona_id")
                msg = data.get("message")
                logger.info(f"Orchestrator decided: {pid} wants to interject: {msg}")
                if pid and msg:
                    await self.session_manager.update_agent_state(
                        persona_id=pid,
                        status="raising_hand",
                        message=msg
                    )

        except Exception as e:
            logger.error(f"Error in Orchestrator loop: {e}")

# Global instance
orchestrator = OrchestratorLoop(session_manager=LiveSessionManager()) # Will be replaced by shared instance
