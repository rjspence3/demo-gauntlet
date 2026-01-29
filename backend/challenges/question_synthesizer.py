"""
Question Synthesis Agent for generating challenge questions from tensions.

This is Step 4 in the multi-step reasoning chain for challenger agents.
"""
from typing import List, Dict, Any, Optional, Union
from backend.models.core import (
    Claim,
    EvidenceItem,
    Tension,
    TensionCategory,
    TensionSeverity,
    AnalysisResult,
    IdealAnswer,
    ChallengeQuestion,
    QuestionSynthesisMeta,
    QuestionSynthesisResult,
    ChallengerPersona,
)
from backend.models.llm import LLMClient
from backend.challenges.difficulty import DifficultyCalculator
from backend.logger import get_logger

logger = get_logger(__name__)

QUESTION_SYNTHESIS_SYSTEM_PROMPT = """You are a challenge question synthesizer. Given tensions identified from analyzing claims and evidence, your job is to generate high-quality challenge questions that a stakeholder might ask.

## Question Construction Rules

Each question must directly target a single tension. Use one of these standard patterns based on tension category:

1. **CONTRADICTION**: "Your slide claims X, but evidence shows Y. How do you reconcile these?"
2. **MISSING_EVIDENCE**: "You assert X, but no supporting data appears. What evidence supports this?"
3. **RISK_EXPOSURE**: "If assumption X fails, what is the mitigation for Y?"
4. **COMPETITIVE_GAP**: "Competitor X provides Y; how do you differentiate?"
5. **AMBIGUITY**: "X is unclear; can you clarify what you mean by Y?"

## Ideal Answer Rules

- Must be grounded in the actual EvidenceItem objects provided.
- Must list evidence_ids explicitly (use the exact IDs from the evidence list).
- Must extract 3-6 key_points as bullet points.
- Must be truthful to provided evidence (no hallucinations).
- If no evidence supports the answer, acknowledge this gap.

## Difficulty Assignment

Based on tension severity:
- HIGH severity tensions → "hard"
- MEDIUM severity tensions → "medium"
- LOW severity tensions → "easy"

## Output Format

Output ONLY valid JSON matching this schema:
{
  "questions": [
    {
      "id": "Q1",
      "tension_id": "T1",
      "question": "The full question text",
      "persona": null,
      "difficulty": "hard | medium | easy",
      "related_claim_ids": ["C1", "C2"],
      "evidence_ids": ["E1", "E3"],
      "ideal_answer": {
        "text": "The complete ideal answer text",
        "key_points": [
          "First key point",
          "Second key point",
          "Third key point"
        ],
        "evidence_ids": ["E1", "E3"]
      },
      "notes": "Optional notes about this question"
    }
  ],
  "meta": {
    "slide_id": "slide_0",
    "num_tensions": 2,
    "num_questions": 2,
    "grounded": true,
    "notes": "Processing notes"
  }
}

IMPORTANT:
- Generate exactly one question per tension (for HIGH and MEDIUM severity).
- Skip LOW severity tensions unless there are fewer than 2 questions total.
- Every question MUST have a valid tension_id matching a provided tension.
- Evidence IDs in ideal_answer must match actual evidence IDs provided.
- If no tensions provided, return empty questions list."""

GROUNDING_VERIFICATION_PROMPT = """You are a grounding verification specialist. Your job is to verify that a challenge question and its ideal answer are properly grounded in the provided evidence.

## Verification Criteria

1. The question must reference claims or tensions that exist.
2. The ideal answer must cite evidence IDs that were actually provided.
3. The key points in the ideal answer must be derivable from the evidence.
4. No hallucinated facts or evidence should be present.

## Output Format

Output ONLY valid JSON:
{
  "grounded": true | false,
  "issues": ["List of specific grounding issues if any"]
}

If all criteria are met, return {"grounded": true, "issues": []}.
If any criteria fail, return {"grounded": false, "issues": ["description of issue"]}."""


def _format_tensions_for_prompt(tensions: List[Tension]) -> str:
    """Format tensions for inclusion in the LLM prompt."""
    if not tensions:
        return "No tensions provided."

    lines = []
    for t in tensions:
        category = t.category.value if hasattr(t.category, 'value') else str(t.category)
        severity = t.severity.value if hasattr(t.severity, 'value') else str(t.severity)
        lines.append(f"[{t.id}] (category: {category}, severity: {severity})")
        lines.append(f"  Headline: {t.headline}")
        lines.append(f"  Description: {t.description}")
        lines.append(f"  Related claims: {', '.join(t.related_claim_ids)}")
        if t.supporting_evidence_ids:
            lines.append(f"  Supporting evidence: {', '.join(t.supporting_evidence_ids)}")
        if t.contradicting_evidence_ids:
            lines.append(f"  Contradicting evidence: {', '.join(t.contradicting_evidence_ids)}")
        if t.question_seed:
            lines.append(f"  Question seed: {t.question_seed}")
        lines.append("")
    return "\n".join(lines)


def _format_claims_for_prompt(claims: List[Claim]) -> str:
    """Format claims for inclusion in the LLM prompt."""
    if not claims:
        return "No claims provided."

    lines = []
    for claim in claims:
        claim_type = claim.claim_type.value if hasattr(claim.claim_type, 'value') else str(claim.claim_type)
        importance = claim.importance.value if hasattr(claim.importance, 'value') else str(claim.importance)
        lines.append(f"[{claim.id}] ({claim_type}, importance: {importance})")
        lines.append(f"  Text: {claim.text}")
        lines.append("")
    return "\n".join(lines)


def _format_evidence_for_prompt(evidence: List[EvidenceItem]) -> str:
    """Format evidence for inclusion in the LLM prompt."""
    if not evidence:
        return "No evidence provided."

    lines = []
    for ev in evidence:
        stance = ev.stance.value if hasattr(ev.stance, 'value') else str(ev.stance)
        lines.append(f"[{ev.id}] (stance: {stance})")
        lines.append(f"  Text: {ev.text}")
        lines.append(f"  Related claims: {', '.join(ev.related_claim_ids)}")
        lines.append("")
    return "\n".join(lines)


def _build_persona_context(persona: ChallengerPersona) -> str:
    """
    Build rich persona context for inclusion in synthesis prompt.

    Args:
        persona: The challenger persona configuration.

    Returns:
        Formatted persona context string.
    """
    focus_areas = ", ".join(persona.focus_areas) if persona.focus_areas else "General business concerns"
    domain_tags = ", ".join(persona.domain_tags) if persona.domain_tags else "General"

    return f"""## Persona Context
You are generating questions for: **{persona.name}** ({persona.role})

**Communication Style:** {persona.style}
**Focus Areas:** {focus_areas}
**Domain Expertise:** {domain_tags}

Shape questions to match this persona's:
- Professional perspective as a {persona.role}
- Communication style: {persona.style}
- Primary concerns around: {focus_areas}

Questions should feel natural coming from someone in this role."""


def _filter_tensions_for_persona(
    tensions: List[Tension],
    persona: ChallengerPersona
) -> List[Tension]:
    """
    Filter tensions relevant to a persona's domain expertise.

    Args:
        tensions: All identified tensions.
        persona: The challenger persona configuration.

    Returns:
        Tensions relevant to the persona, with HIGH severity always included.
    """
    if not persona.domain_tags:
        # No filtering if persona has no domain tags
        return tensions

    persona_tags = set(persona.domain_tags)
    relevant: List[Tension] = []

    for t in tensions:
        tension_tags = set(t.risk_tags) if t.risk_tags else set()

        # Include if tags overlap
        if tension_tags.intersection(persona_tags):
            relevant.append(t)
        # Always include HIGH severity tensions regardless of tags
        elif t.severity == TensionSeverity.HIGH:
            relevant.append(t)

    # Fallback: if no relevant tensions found, return top 2 by severity
    if not relevant and tensions:
        # Sort by severity (HIGH > MEDIUM > LOW)
        severity_order = {TensionSeverity.HIGH: 0, TensionSeverity.MEDIUM: 1, TensionSeverity.LOW: 2}
        sorted_tensions = sorted(tensions, key=lambda x: severity_order.get(x.severity, 2))
        relevant = sorted_tensions[:2]

    return relevant


def _build_synthesis_user_prompt(
    slide_id: str,
    tensions: List[Tension],
    claims: List[Claim],
    evidence: List[EvidenceItem],
    persona: Optional[Union[str, ChallengerPersona]] = None
) -> str:
    """
    Build the user prompt for question synthesis.

    Args:
        slide_id: Identifier for the slide.
        tensions: Identified tensions to generate questions for.
        claims: Extracted claims from the slide.
        evidence: Available evidence items.
        persona: Optional persona (string name or ChallengerPersona object).

    Returns:
        Formatted user prompt string.
    """
    tensions_text = _format_tensions_for_prompt(tensions)
    claims_text = _format_claims_for_prompt(claims)
    evidence_text = _format_evidence_for_prompt(evidence)

    prompt = f"""## Slide: {slide_id}

## Tensions ({len(tensions)} total):
{tensions_text}

## Claims ({len(claims)} total):
{claims_text}

## Evidence ({len(evidence)} total):
{evidence_text}
"""

    # Add persona context if provided
    if persona:
        if isinstance(persona, ChallengerPersona):
            prompt += _build_persona_context(persona)
        else:
            # Simple string persona
            prompt += f"""
## Persona Context
Generate questions appropriate for a {persona} stakeholder. Focus on their typical concerns and communication style.
"""

    prompt += """
Generate challenge questions based on the tensions above. Each question should:
1. Target a specific tension
2. Include a grounded ideal answer
3. Reference actual evidence IDs

Output JSON with the questions."""

    return prompt


def _build_grounding_user_prompt(
    question: ChallengeQuestion,
    evidence: List[EvidenceItem]
) -> str:
    """Build the user prompt for grounding verification."""
    evidence_text = _format_evidence_for_prompt(evidence)

    return f"""## Question to Verify

Question ID: {question.id}
Tension ID: {question.tension_id}
Question: {question.question}

## Ideal Answer

Text: {question.ideal_answer.text}
Key Points: {', '.join(question.ideal_answer.key_points)}
Evidence IDs cited: {', '.join(question.ideal_answer.evidence_ids)}

## Available Evidence
{evidence_text}

Verify that this question and ideal answer are properly grounded in the provided evidence."""


def _severity_to_difficulty(severity: TensionSeverity) -> str:
    """Map tension severity to question difficulty."""
    mapping = {
        TensionSeverity.HIGH: "hard",
        TensionSeverity.MEDIUM: "medium",
        TensionSeverity.LOW: "easy",
    }
    return mapping.get(severity, "medium")


def _create_fallback_question(
    tension: Tension,
    question_index: int
) -> ChallengeQuestion:
    """Create a fallback question when LLM fails."""
    difficulty = _severity_to_difficulty(tension.severity)

    return ChallengeQuestion(
        id=f"Q{question_index}",
        tension_id=tension.id,
        question=f"What are the risks behind: {tension.headline}?",
        persona=None,
        difficulty=difficulty,
        related_claim_ids=tension.related_claim_ids,
        evidence_ids=tension.contradicting_evidence_ids + tension.supporting_evidence_ids,
        ideal_answer=IdealAnswer(
            text="This question requires further analysis of the identified tension.",
            key_points=[
                f"Tension category: {tension.category.value}",
                f"Severity: {tension.severity.value}",
                tension.description[:100] if tension.description else "No description available"
            ],
            evidence_ids=[]
        ),
        grounded=False,
        notes="Fallback question generated due to LLM error"
    )


def _parse_ideal_answer(data: Dict[str, Any]) -> IdealAnswer:
    """Parse ideal answer from response data."""
    return IdealAnswer(
        text=data.get("text", ""),
        key_points=data.get("key_points", []),
        evidence_ids=data.get("evidence_ids", [])
    )


def _parse_question(data: Dict[str, Any]) -> ChallengeQuestion:
    """Parse a single question from response data."""
    ideal_answer_data = data.get("ideal_answer", {})

    return ChallengeQuestion(
        id=data.get("id", "Q0"),
        tension_id=data.get("tension_id", ""),
        question=data.get("question", ""),
        persona=data.get("persona"),
        difficulty=data.get("difficulty", "medium"),
        related_claim_ids=data.get("related_claim_ids", []),
        evidence_ids=data.get("evidence_ids", []),
        ideal_answer=_parse_ideal_answer(ideal_answer_data),
        grounded=data.get("grounded", True),
        notes=data.get("notes")
    )


def _parse_synthesis_response(
    response: Dict[str, Any],
    slide_id: str,
    num_tensions: int
) -> QuestionSynthesisResult:
    """Parse the LLM response into QuestionSynthesisResult."""
    questions_data = response.get("questions", [])
    meta_data = response.get("meta", {})

    questions = [_parse_question(q) for q in questions_data]

    meta = QuestionSynthesisMeta(
        slide_id=meta_data.get("slide_id", slide_id),
        num_tensions=meta_data.get("num_tensions", num_tensions),
        num_questions=meta_data.get("num_questions", len(questions)),
        grounded=meta_data.get("grounded", True),
        notes=meta_data.get("notes")
    )

    return QuestionSynthesisResult(questions=questions, meta=meta)


class QuestionSynthesisAgent:
    """
    Agent responsible for synthesizing challenge questions from tensions.

    This is the fourth step in the reasoning chain:
    1. Claim Extraction -> extracts structured claims
    2. Evidence Selection -> filters and links evidence to claims
    3. Evidence Analysis -> identifies contradictions, gaps, and risks
    4. Question Synthesis (this) -> generates targeted questions from tensions
    """

    def __init__(
        self,
        llm_client: LLMClient,
        use_adaptive_difficulty: bool = True
    ):
        """
        Initialize the QuestionSynthesisAgent.

        Args:
            llm_client: LLM client for synthesis.
            use_adaptive_difficulty: If True, recalculate difficulty using
                                     DifficultyCalculator instead of relying
                                     solely on LLM-assigned difficulty.
        """
        self.llm_client = llm_client
        self.use_adaptive_difficulty = use_adaptive_difficulty
        self._difficulty_calculator = DifficultyCalculator() if use_adaptive_difficulty else None

    def synthesize(
        self,
        slide_id: str,
        analysis: AnalysisResult,
        claims: List[Claim],
        evidence: List[EvidenceItem],
        persona: Optional[Union[str, ChallengerPersona]] = None
    ) -> QuestionSynthesisResult:
        """
        Synthesize challenge questions from analysis results.

        Args:
            slide_id: Identifier for the slide being processed.
            analysis: AnalysisResult containing identified tensions.
            claims: List of claims extracted from the slide.
            evidence: List of evidence items linked to claims.
            persona: Optional persona (string name or ChallengerPersona object).
                     If ChallengerPersona, enables persona-based tension filtering.

        Returns:
            QuestionSynthesisResult containing generated questions.
        """
        tensions = analysis.tensions

        # Apply persona-based filtering if ChallengerPersona provided
        if isinstance(persona, ChallengerPersona):
            relevant_tensions = _filter_tensions_for_persona(tensions, persona)
            logger.info(f"Persona filtering: {len(tensions)} -> {len(relevant_tensions)} tensions for {persona.name}")
        else:
            # Default: filter to HIGH and MEDIUM severity tensions
            relevant_tensions = [
                t for t in tensions
                if t.severity in (TensionSeverity.HIGH, TensionSeverity.MEDIUM)
            ]

            # If too few, include LOW severity
            if len(relevant_tensions) < 2:
                relevant_tensions = tensions

        if not relevant_tensions:
            logger.info(f"No tensions to synthesize questions for slide {slide_id}")
            return QuestionSynthesisResult(
                questions=[],
                meta=QuestionSynthesisMeta(
                    slide_id=slide_id,
                    num_tensions=0,
                    num_questions=0,
                    grounded=True,
                    notes="No tensions to generate questions from"
                )
            )

        user_prompt = _build_synthesis_user_prompt(
            slide_id, relevant_tensions, claims, evidence, persona
        )

        logger.info(f"Synthesizing questions from {len(relevant_tensions)} tensions for slide {slide_id}")

        try:
            response = self.llm_client.complete_with_system(
                system_prompt=QUESTION_SYNTHESIS_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                structured=True
            )

            if isinstance(response, dict):
                result = _parse_synthesis_response(response, slide_id, len(relevant_tensions))

                # Verify grounding for each question
                all_grounded = True
                verified_questions = []

                for question in result.questions:
                    is_grounded = self.verify_grounding(question, evidence)

                    if not is_grounded:
                        # Retry with stricter prompt
                        logger.warning(f"Question {question.id} failed grounding, retrying...")
                        retried_question = self._retry_question_synthesis(
                            question, relevant_tensions, claims, evidence, persona
                        )

                        if retried_question:
                            is_grounded = self.verify_grounding(retried_question, evidence)
                            retried_question.grounded = is_grounded
                            if is_grounded:
                                verified_questions.append(retried_question)
                            else:
                                all_grounded = False
                                # C-2: Exclude ungrounded questions
                                logger.warning(f"Dropping question {question.id} due to grounding failure after retry")
                        else:
                            all_grounded = False
                            logger.warning(f"Dropping question {question.id} due to grounding failure (retry failed)")
                    else:
                        question.grounded = True
                        verified_questions.append(question)


                result.questions = verified_questions
                result.meta.grounded = all_grounded
                result.meta.num_questions = len(verified_questions)

                # Apply adaptive difficulty if enabled
                if self.use_adaptive_difficulty and self._difficulty_calculator:
                    result.questions = self._apply_adaptive_difficulty(
                        result.questions, relevant_tensions, claims, evidence
                    )

                logger.info(f"Synthesis complete for slide {slide_id}: {len(result.questions)} questions generated")
                return result
            else:
                # Non-dict response, use fallback
                logger.warning(f"Unexpected response type from LLM for slide {slide_id}")
                return self._create_fallback_result(slide_id, relevant_tensions)

        except Exception as e:
            logger.error(f"Failed to synthesize questions for slide {slide_id}: {e}")
            return self._create_fallback_result(slide_id, relevant_tensions)

    def verify_grounding(
        self,
        question: ChallengeQuestion,
        evidence: List[EvidenceItem]
    ) -> bool:
        """
        Verify that a question and its ideal answer are properly grounded.

        Args:
            question: The question to verify.
            evidence: Available evidence items.

        Returns:
            True if the question is properly grounded, False otherwise.
        """
        user_prompt = _build_grounding_user_prompt(question, evidence)

        try:
            response = self.llm_client.complete_with_system(
                system_prompt=GROUNDING_VERIFICATION_PROMPT,
                user_prompt=user_prompt,
                structured=True
            )

            if isinstance(response, dict):
                grounded = response.get("grounded", False)
                if not grounded:
                    issues = response.get("issues", [])
                    logger.warning(f"Grounding issues for {question.id}: {issues}")
                return grounded
            return False

        except Exception as e:
            logger.error(f"Grounding verification failed for {question.id}: {e}")
            return False

    def _retry_question_synthesis(
        self,
        original_question: ChallengeQuestion,
        tensions: List[Tension],
        claims: List[Claim],
        evidence: List[EvidenceItem],
        persona: Optional[str]
    ) -> Optional[ChallengeQuestion]:
        """
        Retry question synthesis with stricter grounding requirements.

        Args:
            original_question: The original question that failed grounding.
            tensions: Available tensions.
            claims: Available claims.
            evidence: Available evidence.
            persona: Optional persona context.

        Returns:
            Regenerated question or None if retry fails.
        """
        # Find the original tension
        target_tension = None
        for t in tensions:
            if t.id == original_question.tension_id:
                target_tension = t
                break

        if not target_tension:
            return None

        stricter_prompt = f"""Regenerate a challenge question for this specific tension.
You MUST cite evidence IDs that exist in the provided evidence list.

## Tension to Target
ID: {target_tension.id}
Category: {target_tension.category.value}
Headline: {target_tension.headline}
Description: {target_tension.description}

## Available Evidence (you MUST use these IDs)
{_format_evidence_for_prompt(evidence)}

## Requirements
- The ideal_answer.evidence_ids MUST only contain IDs from the evidence list above
- Key points MUST be derivable from the evidence text
- Do not hallucinate or invent evidence

Output a single question in JSON format:
{{
  "id": "{original_question.id}",
  "tension_id": "{target_tension.id}",
  "question": "...",
  "persona": null,
  "difficulty": "{original_question.difficulty}",
  "related_claim_ids": [...],
  "evidence_ids": [...],
  "ideal_answer": {{
    "text": "...",
    "key_points": [...],
    "evidence_ids": [...]
  }},
  "notes": "Regenerated with stricter grounding"
}}"""

        try:
            response = self.llm_client.complete_with_system(
                system_prompt="You are a question generator. Output only valid JSON.",
                user_prompt=stricter_prompt,
                structured=True
            )

            if isinstance(response, dict):
                # Handle both wrapped and unwrapped responses
                if "questions" in response and response["questions"]:
                    return _parse_question(response["questions"][0])
                elif "id" in response:
                    return _parse_question(response)

            return None

        except Exception as e:
            logger.error(f"Retry synthesis failed: {e}")
            return None

    def _create_fallback_result(
        self,
        slide_id: str,
        tensions: List[Tension]
    ) -> QuestionSynthesisResult:
        """
        Create fallback result when LLM synthesis fails.

        Args:
            slide_id: The slide identifier.
            tensions: Available tensions.

        Returns:
            QuestionSynthesisResult with fallback questions.
        """
        questions = [
            _create_fallback_question(t, i + 1)
            for i, t in enumerate(tensions)
        ]

        return QuestionSynthesisResult(
            questions=questions,
            meta=QuestionSynthesisMeta(
                slide_id=slide_id,
                num_tensions=len(tensions),
                num_questions=len(questions),
                grounded=False,
                notes="Fallback question templates used due to LLM error"
            )
        )

    def _apply_adaptive_difficulty(
        self,
        questions: List[ChallengeQuestion],
        tensions: List[Tension],
        claims: List[Claim],
        evidence: List[EvidenceItem]
    ) -> List[ChallengeQuestion]:
        """
        Apply adaptive difficulty calculation to questions.

        Overrides the LLM-assigned difficulty with a calculated value
        based on weighted factors.

        Args:
            questions: Questions with LLM-assigned difficulty.
            tensions: Tensions used to generate the questions.
            claims: Claims from the slide.
            evidence: Evidence items from retrieval.

        Returns:
            Questions with recalculated difficulty and explanation notes.
        """
        updated_questions = []

        # Build tension lookup
        tension_map = {t.id: t for t in tensions}

        for question in questions:
            # Find the tension this question targets
            tension = tension_map.get(question.tension_id)

            if tension and self._difficulty_calculator:
                # Calculate new difficulty
                difficulty, score, factors, explanation = (
                    self._difficulty_calculator.calculate_with_explanation(
                        tension, claims, evidence
                    )
                )

                # Update difficulty if different
                original_difficulty = question.difficulty
                if difficulty != original_difficulty:
                    logger.debug(
                        f"Question {question.id} difficulty adjusted: "
                        f"{original_difficulty} -> {difficulty} (score: {score:.2f})"
                    )

                # Create updated question with new difficulty
                updated_question = ChallengeQuestion(
                    id=question.id,
                    tension_id=question.tension_id,
                    question=question.question,
                    persona=question.persona,
                    difficulty=difficulty,
                    related_claim_ids=question.related_claim_ids,
                    evidence_ids=question.evidence_ids,
                    ideal_answer=question.ideal_answer,
                    grounded=question.grounded,
                    notes=f"{question.notes or ''}\n{explanation}".strip()
                )
                updated_questions.append(updated_question)
            else:
                # No tension found, keep original
                updated_questions.append(question)

        return updated_questions
