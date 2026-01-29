import os
import time
from typing import Dict, Optional

from backend.models.llm import OpenAIClient, LLMClient
from backend.probes.models import InteractionResult, ConversationContext
from backend.probes.config import ENHANCED_PERSONAS

class AgentTestHarness:
    """Test harness for probing agent human-likeness."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize with LLM client."""
        if llm_client is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                # We raise a gentle warning or error, but let's stick to the original logic:
                # Original logic raised ValueError. We'll do the same but more robustly.
                # However, for default usage, we might want to check the environment.
                if not os.environ.get("OPENAI_API_KEY"):
                   raise ValueError("OPENAI_API_KEY environment variable required")
                
            self.llm = OpenAIClient(api_key=api_key, model="gpt-4o")
        else:
            self.llm = llm_client

        self.personas = ENHANCED_PERSONAS
        self.conversation_contexts: Dict[str, ConversationContext] = {}

    def interact_with_agent(
        self,
        agent_id: str,
        message: str,
        continue_conversation: bool = True
    ) -> InteractionResult:
        """
        Send a message to an agent and get response with latency.

        Args:
            agent_id: Persona ID (skeptic, budget_hawk, compliance, executive)
            message: User message to send
            continue_conversation: Whether to maintain conversation history

        Returns:
            InteractionResult with response and latency
        """
        if agent_id not in self.personas:
            raise ValueError(f"Unknown agent: {agent_id}. Available: {list(self.personas.keys())}")

        persona = self.personas[agent_id]
        system_prompt = persona["agent_prompt"]

        # Get or create conversation context
        if agent_id not in self.conversation_contexts:
            self.conversation_contexts[agent_id] = ConversationContext()

        ctx = self.conversation_contexts[agent_id]

        if not continue_conversation:
            ctx = ConversationContext()
            self.conversation_contexts[agent_id] = ctx

        # Add user message to history
        ctx.add_turn("user", message)
        turn_number = len([m for m in ctx.history if m["role"] == "user"])

        # Build full prompt with history
        history_text = ""
        if len(ctx.history) > 1:
            history_text = "\n\nCONVERSATION HISTORY:\n"
            for msg in ctx.history[:-1]:  # Exclude current message
                role_label = "User" if msg["role"] == "user" else "You"
                history_text += f"{role_label}: {msg['content']}\n"

        full_user_prompt = f"{history_text}\nUser: {message}\n\nRespond naturally as your character:"

        # Time the response
        start_time = time.perf_counter()

        response = self.llm.complete_with_system(
            system_prompt=system_prompt,
            user_prompt=full_user_prompt,
            structured=False
        )

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Ensure response is string
        response_text = str(response) if response else ""

        # Add assistant response to history
        ctx.add_turn("assistant", response_text)

        return InteractionResult(
            response_text=response_text,
            latency_ms=latency_ms,
            turn_number=turn_number,
            prompt=message
        )

    def reset_conversation(self, agent_id: str):
        """Clear conversation history for an agent."""
        if agent_id in self.conversation_contexts:
            self.conversation_contexts[agent_id] = ConversationContext()
