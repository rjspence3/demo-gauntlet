"""
Tests for precompute_flow.
"""
from unittest.mock import MagicMock
from backend.challenges.generator import ChallengeGenerator
from backend.models.core import ChallengerPersona, ResearchDossier, Slide, Challenge, Chunk

def test_precompute_flow() -> None:
    """Test the precomputation flow for challenges using the new pipeline."""
    # Setup Mocks
    mock_llm = MagicMock()
    mock_retriever = MagicMock()
    mock_retriever.get_chunks_for_slide.return_value = [
        Chunk(id="chunk_1", text="Tech content", slide_index=0, metadata={})
    ]
    mock_fact_store = MagicMock()
    mock_fact_store.get_facts_by_topic.return_value = []

    # Mock LLM responses for the 4-step pipeline (for each slide)
    # Slide 0 (Tech) - will have claims and generate question
    # Slide 1 (Finance) - will have no matching claims for CTO persona
    mock_llm.complete_with_system.side_effect = [
        # Slide 0 - Step 1: Claim extraction
        {
            "claims": [
                {
                    "id": "C1",
                    "text": "Tech claim",
                    "claim_type": "factual",
                    "importance": "high",
                    "confidence": 0.9,
                    "tags": ["Tech"]
                }
            ],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        },
        # Slide 0 - Step 2: Evidence selection
        {
            "evidence": [
                {
                    "id": "E1",
                    "text": "Tech evidence",
                    "source": "deck",
                    "collection": "deck_chunks",
                    "relevance": "high",
                    "stance": "supports",
                    "related_claim_ids": ["C1"],
                    "topics": ["Tech"],
                    "score_adjustment": 0.1
                }
            ],
            "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}
        },
        # Slide 0 - Step 3: Evidence analysis
        {
            "tensions": [
                {
                    "id": "T1",
                    "category": "risk_exposure",
                    "severity": "high",
                    "headline": "Tech risk",
                    "description": "Technical risk",
                    "related_claim_ids": ["C1"],
                    "supporting_evidence_ids": ["E1"],
                    "contradicting_evidence_ids": [],
                    "risk_tags": ["Tech"],
                    "question_seed": "Tech question?"
                }
            ],
            "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 1, "num_tensions": 1}
        },
        # Slide 0 - Step 4: Question synthesis
        {
            "questions": [
                {
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Generated Question",
                    "persona": None,
                    "difficulty": "medium",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {
                        "text": "Ideal Answer",
                        "key_points": ["Point 1"],
                        "evidence_ids": ["E1"]
                    }
                }
            ],
            "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
        },
        # Slide 0 - Grounding verification
        {"grounded": True, "issues": []},
        # Slide 1 - Step 1: Claim extraction (no Tech claims)
        {
            "claims": [
                {
                    "id": "C2",
                    "text": "Finance claim",
                    "claim_type": "metric",
                    "importance": "medium",
                    "confidence": 0.8,
                    "tags": ["Finance"]  # Not Tech, so CTO persona won't match
                }
            ],
            "meta": {"slide_index": 1, "used_speaker_notes": False}
        },
        # Slide 1 - Step 2: Evidence selection
        {
            "evidence": [],
            "meta": {"total_candidates": 0, "selected_count": 0, "discarded_count": 0}
        },
        # Slide 1 - Step 3: Evidence analysis (no tensions)
        {
            "tensions": [],
            "meta": {"slide_id": "slide_1", "num_claims": 1, "num_evidence_items": 0, "num_tensions": 0}
        }
    ]

    generator = ChallengeGenerator(mock_llm, mock_retriever, mock_fact_store)

    # Data
    persona = ChallengerPersona(
        id="cto", name="CTO", role="CTO", style="Skeptical", focus_areas=["Tech"], domain_tags=["Tech"]
    )
    dossier = ResearchDossier(session_id="s1")
    slides = [
        Slide(index=0, title="Slide 1", text="Tech Stack", tags=["Tech"]),
        Slide(index=1, title="Slide 2", text="Financials", tags=["Finance"])
    ]

    # Execute
    challenges = generator.generate_challenges(
        session_id="s1",
        persona=persona,
        deck_context="Context",
        dossier=dossier,
        slides=slides
    )

    # Verify
    # Should generate for Slide 0 (Tech) and skip Slide 1 (Finance - no matching tensions)
    assert len(challenges) == 1
    assert challenges[0].persona_id == "cto"
    assert challenges[0].question == "Generated Question"
    assert challenges[0].slide_index == 0
