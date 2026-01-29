"""
Implementations of specific challenger agents.
"""
import uuid
import random
from dataclasses import asdict
from typing import List, Dict, Any, Optional
from backend.challenges.agent import ChallengerAgent
from backend.challenges.claim_extractor import ClaimExtractionAgent
from backend.challenges.pipeline import ChallengerPipeline
from backend.models.core import (
    Slide, Challenge, ChallengerPersona, ResearchDossier, EvaluationResult,
    Claim, ClaimExtractionResult, ClaimImportance, ChallengeQuestion,
    PipelineConfig, PipelineResult
)
from backend.models.store import DeckRetriever
from backend.models.fact_store import FactStore
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)

class BaseChallenger(ChallengerAgent):
    """
    Base implementation of a challenger agent.

    Uses a multi-step reasoning chain via ChallengerPipeline:
    1. Claim Extraction - Extract claims from slides
    2. Evidence Selection - Filter and link evidence to claims
    3. Evidence Analysis - Identify contradictions, gaps, risks
    4. Question Synthesis - Generate targeted challenge questions
    """
    def __init__(
        self,
        persona: ChallengerPersona,
        pipeline: Optional[ChallengerPipeline] = None,
        use_pipeline: bool = True
    ):
        """
        Initialize the challenger agent.

        Args:
            persona: The challenger persona configuration.
            pipeline: Optional pre-configured pipeline. If None and use_pipeline=True,
                      pipeline will be created during precompute_challenges().
            use_pipeline: Whether to use the new pipeline (True) or legacy logic (False).
        """
        self.persona = persona
        self.id = persona.id
        self.name = persona.name
        self.role = persona.role
        self.domain_tags = persona.domain_tags
        self._pipeline = pipeline
        self._use_pipeline = use_pipeline

    def _filter_claims_for_persona(self, claims: List[Claim]) -> List[Claim]:
        """
        Filter claims that are relevant to this persona's focus areas.
        """
        persona_tags = set(self.domain_tags)
        relevant_claims = []

        for claim in claims:
            claim_tags = set(claim.tags)
            # Check if claim tags overlap with persona's domain
            if claim_tags.intersection(persona_tags):
                relevant_claims.append(claim)
            # Also include high-importance claims even without tag match
            elif claim.importance == ClaimImportance.HIGH:
                relevant_claims.append(claim)

        return relevant_claims

    def _format_claims_for_prompt(self, claims: List[Claim]) -> str:
        """Format claims for inclusion in LLM prompts."""
        if not claims:
            return "No specific claims extracted."

        lines = []
        for claim in claims:
            lines.append(f"- [{claim.id}] ({claim.claim_type.value}, {claim.importance.value}): {claim.text}")
            if claim.tags:
                lines.append(f"  Tags: {', '.join(claim.tags)}")
        return "\n".join(lines)

    def _convert_question_to_challenge(
        self,
        question: ChallengeQuestion,
        session_id: str,
        slide: Slide,
        pipeline_result: PipelineResult
    ) -> Challenge:
        """
        Convert a ChallengeQuestion to the legacy Challenge format.

        Args:
            question: The ChallengeQuestion from the pipeline.
            session_id: Current session ID.
            slide: The source slide.
            pipeline_result: Full pipeline result for evidence lookup.

        Returns:
            Challenge object compatible with existing storage/API.
        """
        # Build evidence dict from pipeline result
        evidence_dict: Dict[str, List[Any]] = {"chunks": [], "facts": []}

        for ev in pipeline_result.evidence:
            if ev.id in question.evidence_ids:
                if ev.source.value == "deck":
                    evidence_dict["chunks"].append(ev.text)
                else:
                    evidence_dict["facts"].append({
                        "id": ev.id,
                        "text": ev.text,
                        "topics": ev.topics
                    })

        # Find related tension for metadata
        tension_headline = ""
        tension_category = ""
        for t in pipeline_result.tensions:
            if t.id == question.tension_id:
                tension_headline = t.headline
                tension_category = t.category.value
                break

        return Challenge(
            id=str(uuid.uuid4()),
            session_id=session_id,
            persona_id=self.id,
            question=question.question,
            ideal_answer=question.ideal_answer.text,
            key_points=question.ideal_answer.key_points,
            tone="professional",
            difficulty=question.difficulty,
            slide_index=slide.index,
            evidence=evidence_dict,
            metadata={
                "tension_id": question.tension_id,
                "tension_headline": tension_headline,
                "tension_category": tension_category,
                "related_claim_ids": question.related_claim_ids,
                "evidence_ids": question.evidence_ids,
                "pipeline_generated": True,
                "grounded": question.grounded
            }
        )

    def precompute_challenges(
        self,
        session_id: str,
        deck_context: str,
        slides: List[Slide],
        deck_retriever: DeckRetriever,
        fact_store: FactStore,
        dossier: ResearchDossier,
        llm_client: LLMClient
    ) -> List[Challenge]:
        """
        Precompute challenges using the multi-step reasoning chain.

        Uses ChallengerPipeline when enabled:
        1. Claim Extraction -> 2. Evidence Selection -> 3. Analysis -> 4. Question Synthesis

        Falls back to legacy logic when pipeline is disabled.
        """
        logger.info(f"Precomputing challenges for {self.name} across {len(slides)} slides.")

        # Use new pipeline if enabled
        if self._use_pipeline:
            return self._precompute_with_pipeline(
                session_id, slides, deck_retriever, fact_store, llm_client
            )

        # Legacy path (kept for backwards compatibility)
        return self._precompute_legacy(
            session_id, deck_context, slides, deck_retriever, fact_store, dossier, llm_client
        )

    def _precompute_with_pipeline(
        self,
        session_id: str,
        slides: List[Slide],
        deck_retriever: DeckRetriever,
        fact_store: FactStore,
        llm_client: LLMClient
    ) -> List[Challenge]:
        """Precompute challenges using the new pipeline."""
        # Create pipeline if not provided
        pipeline = self._pipeline
        if pipeline is None:
            pipeline = ChallengerPipeline(
                llm_client=llm_client,
                deck_retriever=deck_retriever,
                fact_store=fact_store,
                config=PipelineConfig(max_questions_per_slide=2)
            )

        challenges = []

        # Process each slide through the pipeline
        for slide in slides:
            try:
                result = pipeline.process_slide(
                    slide=slide,
                    session_id=session_id,
                    persona=self.name
                )

                # Filter questions by persona relevance
                for question in result.questions:
                    # Check if any related claims match persona domain tags
                    relevant = self._is_question_relevant(question, result)
                    if relevant:
                        challenge = self._convert_question_to_challenge(
                            question, session_id, slide, result
                        )
                        challenges.append(challenge)

            except Exception as e:
                logger.error(f"Pipeline failed for slide {slide.index}: {e}")

        logger.info(f"Pipeline generated {len(challenges)} challenges for {self.name}")
        return challenges

    def _is_question_relevant(
        self,
        question: ChallengeQuestion,
        result: PipelineResult
    ) -> bool:
        """Check if a question is relevant to this persona."""
        persona_tags = set(self.domain_tags)

        # Check if any related claims have matching tags
        for claim in result.claims:
            if claim.id in question.related_claim_ids:
                claim_tags = set(claim.tags)
                if claim_tags.intersection(persona_tags):
                    return True
                # Always include high-importance claims
                if claim.importance == ClaimImportance.HIGH:
                    return True

        # Check tension risk tags
        for tension in result.tensions:
            if tension.id == question.tension_id:
                tension_tags = set(tension.risk_tags)
                if tension_tags.intersection(persona_tags):
                    return True

        # Include if no specific filtering applies (fallback)
        return len(self.domain_tags) == 0

    def _precompute_legacy(
        self,
        session_id: str,
        deck_context: str,
        slides: List[Slide],
        deck_retriever: DeckRetriever,
        fact_store: FactStore,
        dossier: ResearchDossier,
        llm_client: LLMClient
    ) -> List[Challenge]:
        """Legacy precompute logic (kept for backwards compatibility)."""
        import warnings
        warnings.warn("_precompute_legacy is deprecated. Use ChallengerPipeline instead.", DeprecationWarning, stacklevel=2)
        challenges = []

        # Step 1: Extract claims from all slides
        claim_extractor = ClaimExtractionAgent(llm_client)
        slide_claims: Dict[int, ClaimExtractionResult] = {}

        for slide in slides:
            extraction_result = claim_extractor.extract_claims(slide)
            slide_claims[slide.index] = extraction_result
            logger.debug(f"Extracted {len(extraction_result.claims)} claims from slide {slide.index}")

        # Process each slide with claims
        for slide in slides:
            extraction_result = slide_claims.get(slide.index)
            if not extraction_result or not extraction_result.claims:
                logger.debug(f"No claims for slide {slide.index}, skipping")
                continue

            # Step 2: Filter claims for this persona
            relevant_claims = self._filter_claims_for_persona(extraction_result.claims)
            if not relevant_claims:
                logger.debug(f"No relevant claims for {self.name} on slide {slide.index}")
                continue

            # Step 3: Retrieve Evidence
            # 3a. Deck Chunks
            chunks = deck_retriever.get_chunks_for_slide(slide.index)
            chunk_texts = [c.text for c in chunks]

            # 3b. Research Facts (by claim tags)
            facts = []
            all_claim_tags = set()
            for claim in relevant_claims:
                all_claim_tags.update(claim.tags)

            for tag in all_claim_tags:
                facts.extend(fact_store.get_facts_by_topic(tag, limit=2))

            fact_texts = [f.text for f in facts]

            # Step 4: Generate Challenge with claim-grounded reasoning
            if self.persona.agent_prompt:
                base_prompt = self.persona.agent_prompt
            else:
                # OPTIMIZED DSPy Prompt
                base_prompt = f"""
                Imagine you are an executive persona (e.g., CTO, CFO, etc.) facing a challenge question related to your specific role.
                Your task is to craft a well-informed response by considering the persona's unique perspective, goals, and concerns.
                Utilize the provided evidence from a presentation deck to support your argument.
                Begin by analyzing the situation step-by-step from the persona's viewpoint, ensuring your response is grounded in facts and addresses the challenge accurately, clearly, and comprehensively.
                Use simple, direct language suitable for a live presentation. Avoid complex sentence structures.

                Persona: {self.name}, {self.role}
                Style: {self.persona.style}
                Focus Areas: {', '.join(self.persona.focus_areas)}
                """

            claims_text = self._format_claims_for_prompt(relevant_claims)

            prompt = f"""
            {base_prompt}

            Context:
            Slide Title: {slide.title}
            Slide Content: {slide.text}

            ## Extracted Claims (from slide analysis):
            {claims_text}

            ## Supporting Evidence from Deck:
            {chr(10).join([f"- {c}" for c in chunk_texts]) if chunk_texts else "None available"}

            ## Research Facts (external sources):
            {chr(10).join([f"- {f}" for f in fact_texts]) if fact_texts else "None available"}

            ## Your Task:
            Generate 1 challenging question/objection that:
            1. TARGETS a specific claim from the list above (reference the claim ID)
            2. Is grounded in either deck evidence OR research facts
            3. Matches your persona's expertise and communication style

            Challenge Types to consider:
            - Claim Verification: Challenge a factual/metric claim with counter-evidence
            - Risk Exposure: Highlight risks the claim overlooks
            - Cost/ROI Challenge: Question financial assumptions
            - Technical Depth Check: Probe implementation details
            - Competitive Objection: Compare to alternatives

            Output JSON:
            {{
                "targeted_claim_id": "C1",
                "challenge_type": "Claim Verification | Risk Exposure | Cost/ROI Challenge | Technical Depth Check | Competitive Objection",
                "question": {{
                    "text": "The question text",
                    "reasoning": "Why this claim deserves scrutiny from your perspective"
                }},
                "ideal_answer": {{
                    "text": "The ideal grounded answer...",
                    "key_points": ["point 1", "point 2", "point 3"],
                    "tone": "concise-technical",
                    "evidence_used": {{
                        "chunks": ["exact text of used chunks..."],
                        "facts": ["exact text of used facts..."]
                    }}
                }},
                "difficulty": "easy | medium | hard"
            }}
            """

            try:
                response = llm_client.complete_structured(prompt)

                if not response or "question" not in response:
                    continue

                q_data = response["question"]
                a_data = response["ideal_answer"]

                # Find the targeted claim for metadata
                targeted_claim_id = response.get("targeted_claim_id", "")
                targeted_claim = next(
                    (c for c in relevant_claims if c.id == targeted_claim_id),
                    None
                )

                challenges.append(Challenge(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    persona_id=self.id,
                    question=q_data.get("text", ""),
                    ideal_answer=a_data.get("text", ""),
                    key_points=a_data.get("key_points", []),
                    tone=a_data.get("tone", "professional"),
                    difficulty=response.get("difficulty", "medium"),
                    slide_index=slide.index,
                    evidence={
                        "chunks": a_data.get("evidence_used", {}).get("chunks", []),
                        "facts": [asdict(f) for f in facts]
                    },
                    metadata={
                        "challenge_type": response.get("challenge_type", "Unknown"),
                        "targeted_claim_id": targeted_claim_id,
                        "targeted_claim_text": targeted_claim.text if targeted_claim else "",
                        "reasoning": q_data.get("reasoning", "")
                    }
                ))
            except Exception as e:
                logger.error(f"Failed to generate challenge for {self.name} on slide {slide.index}: {e}")

        logger.info(f"Generated {len(challenges)} challenges for {self.name}.")
        return challenges

    def decide_questions_for_slide(
        self,
        slide_index: int,
        challenges: List[Challenge]
    ) -> List[Challenge]:
        """
        Decide whether to trigger a challenge for a specific slide.
        """
        # Filter challenges for this slide
        slide_challenges = [c for c in challenges if c.slide_index == slide_index]
        
        if not slide_challenges:
            return []
            
        # Trigger Probability Rule (8.4)
        # base_p = 0.15 + 0.35*relevance_score + 0.35*evidence_score
        
        # Estimate scores for MVP
        relevance_score = 1.0 # We already filtered by tags
        
        # Check if we have evidence
        has_evidence = False
        if slide_challenges:
            first_c = slide_challenges[0]
            if first_c.evidence.get("chunks") or first_c.evidence.get("facts"):
                has_evidence = True
        
        evidence_score = 1.0 if has_evidence else 0.0
        
        base_p = 0.15 + (0.35 * relevance_score) + (0.35 * evidence_score)
        
        # Cap at 0.85
        base_p = min(base_p, 0.85)

        if random.random() < base_p:
            return slide_challenges[:1] # Return top challenge
            
        return []

    def evaluate_response(
        self,
        question: Challenge,
        user_answer: str,
        llm_client: LLMClient
    ) -> EvaluationResult:
        """
        Evaluate the user's response to a challenge.
        """
        logger.info(f"Evaluating response for {self.name}")
        
        prompt = f"""
        You are roleplaying as {self.name}, a {self.role}.
        Your style is: {self.persona.style}
        
        Question asked: "{question.question}"
        Ideal Answer: "{question.ideal_answer}"
        Key Points to hit: {', '.join(question.key_points)}
        
        User's Answer: "{user_answer}"
        
        Evaluate the user's answer based on your persona and the ideal answer.
        
        Scoring Weights:
        - Accuracy: 0.45
        - Completeness: 0.35
        - Clarity: 0.15
        - Truth Alignment: 0.05
        
        Score Buckets:
        - >= 80: Good
        - 50-79: Okay
        - < 50: Weak
        
        Output JSON format:
        {{
            "score": 85,
            "feedback": "Your feedback here...",
            "accuracy_assessment": "Assessment of accuracy...",
            "completeness_assessment": "Assessment of completeness...",
            "tone_assessment": "Assessment of tone..."
        }}
        """
        
        try:
            response = llm_client.complete_structured(prompt)
            return EvaluationResult(
                score=response.get("score", 0),
                feedback=response.get("feedback", ""),
                accuracy_assessment=response.get("accuracy_assessment", ""),
                completeness_assessment=response.get("completeness_assessment", ""),
                tone_assessment=response.get("tone_assessment", "")
            )
        except Exception as e:
            logger.error(f"Failed to evaluate response for {self.name}: {e}")
            return EvaluationResult(
                score=0,
                feedback="Failed to evaluate response.",
                accuracy_assessment="Error",
                completeness_assessment="Error",
                tone_assessment="Error"
            )

class CTOAgent(BaseChallenger):
    """
    CTO persona implementation.
    """
    pass

class CFOAgent(BaseChallenger):
    """
    CFO persona implementation.
    """
    pass

class ComplianceAgent(BaseChallenger):
    """
    Compliance officer persona implementation.
    """
    pass
