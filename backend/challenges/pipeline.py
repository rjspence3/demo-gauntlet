"""
Challenger Pipeline - Orchestrates the 4-step reasoning chain.

Chains together:
1. ClaimExtractionAgent - Extract claims from slides
2. EvidenceSelectionAgent - Filter and link evidence to claims
3. EvidenceAnalysisAgent - Identify contradictions, gaps, and risks
4. QuestionSynthesisAgent - Generate targeted challenge questions
"""
import time
from typing import Dict, List, Optional, Protocol, Any

from backend.challenges.claim_extractor import ClaimExtractionAgent
from backend.challenges.evidence_selector import EvidenceSelectionAgent
from backend.challenges.evidence_analyzer import EvidenceAnalysisAgent
from backend.challenges.question_synthesizer import QuestionSynthesisAgent
from backend.models.core import (
    Slide,
    Chunk,
    Fact,
    Claim,
    CandidateEvidence,
    EvidenceItem,
    EvidenceSource,
    Tension,
    ChallengeQuestion,
    AnalysisResult,
    AnalysisMeta,
    PipelineConfig,
    PipelineMeta,
    PipelineResult,
)
from backend.models.llm import LLMClient
from backend.logger import get_logger

logger = get_logger(__name__)


class DeckRetrieverProtocol(Protocol):
    """Protocol for deck chunk retrieval."""
    def get_chunks_for_slide(self, slide_index: int, session_id: Optional[str] = None) -> List[Chunk]:
        """Retrieve chunks for a specific slide."""
        ...


class FactStoreProtocol(Protocol):
    """Protocol for research fact retrieval."""
    def get_facts_by_topic(self, topic: str, limit: int = 5) -> List[Fact]:
        """Retrieve facts by topic."""
        ...


def _chunk_to_candidate(chunk: Chunk, index: int) -> CandidateEvidence:
    """Convert a Chunk to CandidateEvidence."""
    return CandidateEvidence(
        id=chunk.id or f"chunk_{index}",
        text=chunk.text,
        source=EvidenceSource.DECK,
        collection="deck_chunks",
        base_score=1.0,  # Chunks from the same slide are highly relevant
        metadata=chunk.metadata
    )


def _fact_to_candidate(fact: Fact, index: int) -> CandidateEvidence:
    """Convert a Fact to CandidateEvidence."""
    return CandidateEvidence(
        id=fact.id or f"fact_{index}",
        text=fact.text,
        source=EvidenceSource.RESEARCH,
        collection="research_facts",
        base_score=0.8,  # Research facts have slightly lower base score
        metadata={
            "topic": fact.topic,
            "source_url": fact.source_url,
            "source_title": fact.source_title,
            "domain": fact.domain,
            "snippet": fact.snippet
        }
    )


class ChallengerPipeline:
    """
    Orchestrates the 4-step challenger reasoning chain.

    Processes slides through:
    1. Claim Extraction
    2. Evidence Selection
    3. Evidence Analysis
    4. Question Synthesis

    All steps are executed sequentially for simplicity and debuggability.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        deck_retriever: DeckRetrieverProtocol,
        fact_store: FactStoreProtocol,
        config: Optional[PipelineConfig] = None
    ):
        """
        Initialize the ChallengerPipeline.

        Args:
            llm_client: LLM client for all reasoning steps.
            deck_retriever: Retriever for deck chunks.
            fact_store: Store for research facts.
            config: Pipeline configuration options.
        """
        self.llm_client = llm_client
        self.deck_retriever = deck_retriever
        self.fact_store = fact_store
        self.config = config or PipelineConfig()
        
        # H-4: Pipeline results cache
        # Key: (slide_index, session_id), Value: dict with claims, evidence, tensions, steps_completed
        self._cache: Dict[tuple, Dict[str, Any]] = {}

        # Initialize all agents
        self.claim_extractor = ClaimExtractionAgent(llm_client)
        self.evidence_selector = EvidenceSelectionAgent(llm_client)
        self.evidence_analyzer = EvidenceAnalysisAgent(llm_client)
        self.question_synthesizer = QuestionSynthesisAgent(llm_client)

    def process_slide(
        self,
        slide: Slide,
        session_id: Optional[str] = None,
        persona: Optional[str] = None
    ) -> PipelineResult:
        """
        Process a single slide through all 4 steps of the reasoning chain.

        Args:
            slide: The slide to process.
            session_id: Optional session ID for scoped retrieval.
            persona: Optional persona name for question shaping.

        Returns:
            PipelineResult containing all intermediate and final outputs.
        """
        start_time = time.time()
        slide_id = f"slide_{slide.index}"
        cache_key = (slide.index, session_id)
        
        # Check cache for intermediate results (Steps 1-3)
        cached_data = self._cache.get(cache_key)
        
        if cached_data:
            logger.info(f"Using cached pipeline results for {slide_id} (Steps 1-3)")
            claims = cached_data["claims"]
            evidence = cached_data["evidence"]
            tensions = cached_data["tensions"]
            steps_completed = list(cached_data["steps_completed"]) # Copy
            errors = list(cached_data["errors"]) # Copy
        else:
            steps_completed: List[str] = []
            errors: List[str] = []

            claims: List[Claim] = []
            evidence: List[EvidenceItem] = []
            tensions: List[Tension] = []

            logger.info(f"Processing {slide_id} through pipeline")

            # Step 1: Claim Extraction
            try:
                extraction_result = self.claim_extractor.extract_claims(slide)
                claims = extraction_result.claims
                steps_completed.append("claim_extraction")
                logger.info(f"Step 1: Extracted {len(claims)} claims from {slide_id}")
            except Exception as e:
                error_msg = f"Claim extraction failed: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Step 1 failed for {slide_id}: {e}")
                # Return early - can't continue without claims
                return self._build_result(
                    slide_id, slide.index, start_time,
                    claims, evidence, tensions, [],
                    steps_completed, errors
                )

            if not claims:
                logger.info(f"No claims extracted from {slide_id}, returning empty result")
                steps_completed.append("no_claims")
                # Cache negative result too
                self._cache[cache_key] = {
                    "claims": [], "evidence": [], "tensions": [],
                    "steps_completed": steps_completed, "errors": errors
                }
                return self._build_result(
                    slide_id, slide.index, start_time,
                    claims, evidence, tensions, [],
                    steps_completed, errors
                )

            # Step 2: Evidence Retrieval and Selection
            try:
                candidate_evidence = self._retrieve_evidence(slide, claims, session_id)
                logger.info(f"Retrieved {len(candidate_evidence)} candidate evidence items")

                if candidate_evidence:
                    selection_result = self.evidence_selector.select_evidence(
                        claims, candidate_evidence
                    )
                    evidence = selection_result.evidence
                    logger.info(f"Step 2: Selected {len(evidence)} evidence items")
                else:
                    logger.info("No candidate evidence found")

                steps_completed.append("evidence_selection")
            except Exception as e:
                error_msg = f"Evidence selection failed: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Step 2 failed for {slide_id}: {e}")
                # Continue with empty evidence

            # Step 3: Evidence Analysis
            try:
                analysis_result = self.evidence_analyzer.analyze(
                    slide_id, claims, evidence
                )
                tensions = analysis_result.tensions
                steps_completed.append("evidence_analysis")
                logger.info(f"Step 3: Identified {len(tensions)} tensions")
            except Exception as e:
                error_msg = f"Evidence analysis failed: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Step 3 failed for {slide_id}: {e}")
                # Continue with empty tensions
                
            # Cache the results of steps 1-3
            self._cache[cache_key] = {
                "claims": claims,
                "evidence": evidence,
                "tensions": tensions,
                "steps_completed": steps_completed,
                "errors": errors
            }

        questions: List[ChallengeQuestion] = []
        
        if not tensions:
            logger.info(f"No tensions identified for {slide_id}")
            if "no_tensions" not in steps_completed:
                steps_completed.append("no_tensions")
            return self._build_result(
                slide_id, slide.index, start_time,
                claims, evidence, tensions, questions,
                steps_completed, errors
            )

        # Step 4: Question Synthesis
        try:
            # Build analysis result for synthesizer
            analysis = AnalysisResult(
                slide_id=slide_id,
                tensions=tensions,
                meta=AnalysisMeta(
                    slide_id=slide_id,
                    num_claims=len(claims),
                    num_evidence_items=len(evidence),
                    num_tensions=len(tensions)
                )
            )

            synthesis_result = self.question_synthesizer.synthesize(
                slide_id=slide_id,
                analysis=analysis,
                claims=claims,
                evidence=evidence,
                persona=persona
            )
            questions = synthesis_result.questions

            # Apply max questions limit
            if len(questions) > self.config.max_questions_per_slide:
                questions = questions[:self.config.max_questions_per_slide]

            steps_completed.append("question_synthesis")
            logger.info(f"Step 4: Generated {len(questions)} questions")
        except Exception as e:
            error_msg = f"Question synthesis failed: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Step 4 failed for {slide_id}: {e}")

        return self._build_result(
            slide_id, slide.index, start_time,
            claims, evidence, tensions, questions,
            steps_completed, errors
        )

    def process_deck(
        self,
        slides: List[Slide],
        session_id: Optional[str] = None,
        persona: Optional[str] = None
    ) -> List[PipelineResult]:
        """
        Process all slides in a deck sequentially.

        Args:
            slides: List of slides to process.
            session_id: Optional session ID for scoped retrieval.
            persona: Optional persona name for question shaping.

        Returns:
            List of PipelineResult, one per slide.
        """
        logger.info(f"Processing deck with {len(slides)} slides")
        results = []

        for slide in slides:
            result = self.process_slide(slide, session_id, persona)
            results.append(result)

        total_questions = sum(len(r.questions) for r in results)
        logger.info(f"Deck processing complete: {total_questions} total questions generated")

        return results

    def _retrieve_evidence(
        self,
        slide: Slide,
        claims: List[Claim],
        session_id: Optional[str] = None
    ) -> List[CandidateEvidence]:
        """
        Retrieve candidate evidence from deck chunks and research facts.

        Args:
            slide: The current slide.
            claims: Extracted claims to find evidence for.
            session_id: Optional session ID for scoped retrieval.

        Returns:
            List of CandidateEvidence from both sources.
        """
        candidates: List[CandidateEvidence] = []

        # 1. Get deck chunks for this slide
        try:
            chunks = self.deck_retriever.get_chunks_for_slide(
                slide.index, session_id=session_id
            )
            for i, chunk in enumerate(chunks):
                candidates.append(_chunk_to_candidate(chunk, i))
            logger.debug(f"Retrieved {len(chunks)} deck chunks")
        except Exception as e:
            logger.warning(f"Failed to retrieve deck chunks: {e}")

        # 2. Get research facts by claim tags
        try:
            all_tags: set = set()
            for claim in claims:
                all_tags.update(claim.tags)

            facts_seen: set = set()
            for tag in all_tags:
                facts = self.fact_store.get_facts_by_topic(tag, limit=3)
                for i, fact in enumerate(facts):
                    if fact.id not in facts_seen:
                        facts_seen.add(fact.id)
                        candidates.append(_fact_to_candidate(fact, len(candidates)))
            logger.debug(f"Retrieved {len(facts_seen)} research facts")
        except Exception as e:
            logger.warning(f"Failed to retrieve research facts: {e}")

        return candidates

    def _build_result(
        self,
        slide_id: str,
        slide_index: int,
        start_time: float,
        claims: List[Claim],
        evidence: List[EvidenceItem],
        tensions: List[Tension],
        questions: List[ChallengeQuestion],
        steps_completed: List[str],
        errors: List[str]
    ) -> PipelineResult:
        """Build the final PipelineResult."""
        processing_time_ms = int((time.time() - start_time) * 1000)

        return PipelineResult(
            slide_id=slide_id,
            claims=claims,
            evidence=evidence,
            tensions=tensions,
            questions=questions,
            meta=PipelineMeta(
                slide_index=slide_index,
                processing_time_ms=processing_time_ms,
                steps_completed=steps_completed,
                errors=errors
            )
        )
