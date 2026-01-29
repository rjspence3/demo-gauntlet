"""
Tests for challenge_generator.
"""
from typing import Any
from unittest.mock import MagicMock
from backend.challenges.generator import ChallengeGenerator
from backend.models.core import ChallengerPersona, ResearchDossier, Challenge, Slide, Chunk

def test_generate_challenges() -> None:
    """Test generating challenges using the new pipeline."""
    mock_llm = MagicMock()

    # Set up mock responses for the 4-step pipeline
    mock_llm.complete_with_system.side_effect = [
        # Step 1: Claim extraction
        {
            "claims": [
                {
                    "id": "C1",
                    "text": "Test claim",
                    "claim_type": "factual",
                    "importance": "high",
                    "confidence": 0.9,
                    "tags": ["F1"]
                }
            ],
            "meta": {"slide_index": 0, "used_speaker_notes": False}
        },
        # Step 2: Evidence selection
        {
            "evidence": [
                {
                    "id": "E1",
                    "text": "Test evidence",
                    "source": "deck",
                    "collection": "deck_chunks",
                    "relevance": "high",
                    "stance": "supports",
                    "related_claim_ids": ["C1"],
                    "topics": ["F1"],
                    "score_adjustment": 0.1
                }
            ],
            "meta": {"total_candidates": 1, "selected_count": 1, "discarded_count": 0}
        },
        # Step 3: Evidence analysis
        {
            "tensions": [
                {
                    "id": "T1",
                    "category": "risk_exposure",
                    "severity": "high",
                    "headline": "Test tension",
                    "description": "Test description",
                    "related_claim_ids": ["C1"],
                    "supporting_evidence_ids": ["E1"],
                    "contradicting_evidence_ids": [],
                    "risk_tags": ["F1"],
                    "question_seed": "Test question?"
                }
            ],
            "meta": {"slide_id": "slide_0", "num_claims": 1, "num_evidence_items": 1, "num_tensions": 1}
        },
        # Step 4: Question synthesis
        {
            "questions": [
                {
                    "id": "Q1",
                    "tension_id": "T1",
                    "question": "Q1",
                    "persona": None,
                    "difficulty": "hard",
                    "related_claim_ids": ["C1"],
                    "evidence_ids": ["E1"],
                    "ideal_answer": {
                        "text": "A1",
                        "key_points": ["K1"],
                        "evidence_ids": ["E1"]
                    }
                }
            ],
            "meta": {"slide_id": "slide_0", "num_tensions": 1, "num_questions": 1, "grounded": True}
        },
        # Grounding verification
        {"grounded": True, "issues": []}
    ]

    persona = ChallengerPersona(
        id="p1", name="P1", role="R1", style="S1", focus_areas=["F1"], domain_tags=["F1"]
    )
    dossier = ResearchDossier(session_id="s1")

    mock_retriever = MagicMock()
    mock_retriever.get_chunks_for_slide.return_value = [
        Chunk(id="chunk_1", text="Chunk content", slide_index=0, metadata={})
    ]

    mock_fact_store = MagicMock()
    mock_fact_store.get_facts_by_topic.return_value = []

    generator = ChallengeGenerator(mock_llm, mock_retriever, mock_fact_store)
    challenges = generator.generate_challenges(
        session_id="s1",
        persona=persona,
        deck_context="Deck Context",
        dossier=dossier,
        slides=[Slide(index=0, title="Slide 1", text="Content", tags=["F1"])]
    )

    assert len(challenges) == 1
    assert challenges[0].question == "Q1"
    assert challenges[0].persona_id == "p1"
