from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""

    @abstractmethod
    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate structured JSON from a prompt."""

class MockLLM(LLMClient):
    def generate(self, prompt: str) -> str:
        return "This is a mock response."

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"mock_key": "mock_value"}

class OpenAILLM(LLMClient):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        try:
            # pylint: disable=import-outside-toplevel
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except ImportError as exc:
            raise ImportError("openai package is not installed. Run `pip install openai`.") from exc

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content or ""

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # For MVP, we'll just ask for JSON in the prompt and parse it.
        # In production, use structured outputs or function calling.
        system_prompt = "You are a helpful assistant that outputs JSON."
        if schema:
            system_prompt += f" Follow this schema: {json.dumps(schema)}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content or "{}"
        return dict(json.loads(content))
