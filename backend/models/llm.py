"""
LLM Client abstractions and implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    """
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Generate text from a prompt."""

    @abstractmethod
    def complete_structured(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate structured JSON from a prompt."""

    @abstractmethod
    def complete_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        structured: bool = False
    ) -> Dict[str, Any] | str:
        """Generate response with separate system and user prompts."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the LLM provider is reachable."""

class MockLLM(LLMClient):
    """
    Mock LLM client for testing.
    """
    def complete(self, prompt: str) -> str:
        """Generate text from a prompt."""
        return "This is a mock response."

    def complete_structured(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate structured JSON from a prompt."""
        return {"mock_key": "mock_value"}

    def complete_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        structured: bool = False
    ) -> Dict[str, Any] | str:
        """Generate response with separate system and user prompts."""
        if structured:
            # Detect which type of response to return based on system prompt
            prompt_lower = system_prompt.lower()
            if "grounding verification" in prompt_lower:
                return self._mock_grounding_verification_response()
            elif "challenge question synthesizer" in prompt_lower or "question generator" in prompt_lower:
                return self._mock_question_synthesis_response()
            elif "critical analysis" in prompt_lower or "identify tensions" in prompt_lower:
                return self._mock_evidence_analysis_response()
            elif "evidence analysis" in prompt_lower or "filter" in prompt_lower:
                return self._mock_evidence_selection_response()
            else:
                return self._mock_claim_extraction_response()
        return "This is a mock response."

    def _mock_claim_extraction_response(self) -> Dict[str, Any]:
        """Return mock claim extraction response."""
        return {
            "claims": [
                {
                    "id": "C1",
                    "text": "Mock claim for testing",
                    "type": "factual",
                    "importance": "medium",
                    "confidence": 0.8,
                    "tags": ["mock"],
                    "source_spans": [{"start": 0, "end": 10, "origin": "slide_body"}]
                }
            ],
            "meta": {
                "slide_index": 0,
                "used_speaker_notes": False,
                "notes": "Mock extraction"
            }
        }

    def _mock_evidence_selection_response(self) -> Dict[str, Any]:
        """Return mock evidence selection response."""
        return {
            "evidence": [
                {
                    "id": "E1",
                    "relevance": "high",
                    "stance": "supports",
                    "related_claim_ids": ["C1"],
                    "topics": ["mock", "testing"],
                    "score_adjustment": 0.1,
                    "notes": "Mock evidence for testing"
                }
            ],
            "meta": {
                "total_candidates": 2,
                "selected_count": 1,
                "discarded_count": 1,
                "processing_notes": "Mock processing"
            }
        }

    def _mock_evidence_analysis_response(self) -> Dict[str, Any]:
        """Return mock evidence analysis response."""
        return {
            "tensions": [
                {
                    "id": "T1",
                    "category": "contradiction",
                    "severity": "high",
                    "headline": "Cost savings claim contradicts industry data",
                    "description": "The claimed 40% cost reduction conflicts with industry benchmarks showing 15-25% typical savings.",
                    "related_claim_ids": ["C1"],
                    "supporting_evidence_ids": [],
                    "contradicting_evidence_ids": ["E1"],
                    "risk_tags": ["cost", "roi"],
                    "question_seed": "How do you reconcile your cost savings claim with industry benchmarks?",
                    "notes": "Mock tension for testing"
                }
            ],
            "meta": {
                "slide_id": "slide_0",
                "num_claims": 1,
                "num_evidence_items": 1,
                "num_tensions": 1,
                "processing_notes": "Mock analysis"
            }
        }

    def _mock_question_synthesis_response(self) -> Dict[str, Any]:
        """Return mock question synthesis response."""
        return {
            "questions": [
                {
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Your slide claims 40% cost savings, but industry benchmarks show 15-25% is typical. How do you reconcile this discrepancy?",
                    "persona": None,
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {
                        "text": "The 40% cost savings figure includes both direct and indirect savings. While direct savings align with industry benchmarks at 20%, we achieve additional savings through automation and reduced maintenance overhead.",
                        "key_points": [
                            "Direct savings of 20% align with industry benchmarks",
                            "Additional 20% from automation benefits",
                            "Reduced maintenance overhead contributes to total savings",
                            "Total figure validated by customer case studies"
                        ],
                        "evidence_ids": ["E1"]
                    },
                    "notes": "Mock question for testing"
                }
            ],
            "meta": {
                "slide_id": "slide_0",
                "num_tensions": 1,
                "num_questions": 1,
                "grounded": True,
                "notes": "Mock synthesis"
            }
        }

    def _mock_grounding_verification_response(self) -> Dict[str, Any]:
        """Return mock grounding verification response."""
        return {
            "grounded": True,
            "issues": []
        }

    def health_check(self) -> bool:
        """Check if the LLM provider is reachable."""
        return True

class OpenAIClient(LLMClient):
    """
    OpenAI LLM client implementation.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key.
            model: Model name to use.
        """
        try:
            # pylint: disable=import-outside-toplevel
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
        except ImportError as exc:
            raise ImportError("openai package is not installed. Run `pip install openai`.") from exc

    def _should_retry_error(self, exception: Exception) -> bool:
        """Check if the error is retryable."""
        # Add specific OpenAI errors here if needed, e.g. RateLimitError, APIConnectionError
        return True 

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def complete(self, prompt: str) -> str:
        """Generate text from a prompt."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            # Re-raise for tenacity to handle, unless it's a non-retryable error
            raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def complete_structured(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate structured JSON from a prompt."""
        # For MVP, we'll just ask for JSON in the prompt and parse it.
        # In production, use structured outputs or function calling.
        system_prompt = "You are a helpful assistant that outputs JSON."
        if schema:
            system_prompt += f" Follow this schema: {json.dumps(schema)}"

        try:
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
        except Exception as e:
             # Re-raise for tenacity to handle
             raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def complete_with_system(
        self,
        system_prompt: str,
        user_prompt: str,
        structured: bool = False
    ) -> Dict[str, Any] | str:
        """Generate response with separate system and user prompts."""
        try:
            kwargs: Dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if structured:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""

            if structured:
                return dict(json.loads(content)) if content else {}
            return content
        except Exception as e:
            # Re-raise for tenacity
            raise e

    def health_check(self) -> bool:
        """Check if the OpenAI API is reachable."""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
