from dataclasses import asdict
from typing import Optional, List, Any

from backend.models.llm import LLMClient
from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeScorecard, ProbeResult
from backend.probes.scorecard import calculate_grade
from backend.probes.lib.cognitive import probe_cognitive_latency
from backend.probes.lib.memory import probe_episodic_continuity
from backend.probes.lib.linguistics import probe_linguistic_imperfection
from backend.probes.lib.emotions import probe_emotional_coherence
from backend.probes.lib.friction import probe_task_friction
from backend.probes.config import ENHANCED_PERSONAS

def run_full_probe_suite(agent_id: str, llm_client: Optional[LLMClient] = None) -> ProbeScorecard:
    """
    Run all 5 probes against an agent and generate scorecard.
    """
    harness = AgentTestHarness(llm_client)

    # Run all probes
    results = [
        probe_cognitive_latency(harness, agent_id),
        probe_episodic_continuity(harness, agent_id),
        probe_linguistic_imperfection(harness, agent_id),
        probe_emotional_coherence(harness, agent_id),
        probe_task_friction(harness, agent_id),
    ]

    # Collect scores
    scores = {r.probe_name.lower().replace(" ", "_"): r.score for r in results}
    total_score = sum(scores.values())

    # Check for uncanny valley penalty
    all_responses = []
    for r in results:
        for t in r.transcript:
            all_responses.append(t.response_text.lower())

    all_text = " ".join(all_responses)
    penalty_applied = False

    uncanny_phrases = ["as an ai", "as a language model", "i don't have feelings",
                      "i am an artificial", "i'm just a", "i cannot feel emotions"]
    for phrase in uncanny_phrases:
        if phrase in all_text:
            total_score -= 5
            penalty_applied = True
            break

    # Calculate telemetry
    all_latencies = [t.latency_ms for r in results for t in r.transcript]
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0
    latency_variance = "High" if max(all_latencies) - min(all_latencies) > 1000 else "Low"

    # Collect critical failures and wins
    critical_failures = []
    human_wins = []

    for r in results:
        for obs in r.key_observations:
            if "CRITICAL" in obs or "failure" in obs.lower() or "doormat" in obs.lower():
                critical_failures.append(f"[{r.probe_name}] {obs}")
            elif "excellent" in obs.lower() or "good" in obs.lower() or "shows" in obs.lower():
                human_wins.append(f"[{r.probe_name}] {obs}")

    # Generate coaching tip based on lowest score
    lowest_probe = min(results, key=lambda r: r.score)
    coaching_tips = {
        "Cognitive Latency": "Add more thinking markers (Hmm, Let me think...) and hedging language to system prompt.",
        "Episodic Continuity": "Emphasize memory retention in the prompt. Add explicit instruction to track and recall details.",
        "Linguistic Imperfection": "Include instruction to mirror user's tone and energy. Reduce corporate-speak patterns.",
        "Emotional Coherence": "Allow the persona to push back on unfair criticism. Remove excessive apology patterns.",
        "Task Friction": "Add instruction to simulate realistic effort when uncertain. Avoid instant omniscient responses.",
    }

    return ProbeScorecard(
        target_agent_persona=harness.personas[agent_id]["name"],
        test_script_summary=f"Ran 5 probes: latency, memory, speech, emotion, friction against {agent_id}",
        scores=scores,
        total_score=max(0, total_score),  # Floor at 0
        human_likeness_grade=calculate_grade(total_score, penalty_applied),
        telemetry_data={
            "average_latency_ms": round(avg_latency, 1),
            "latency_variance": latency_variance,
            "penalty_applied": penalty_applied
        },
        critical_failures=critical_failures if critical_failures else ["None detected"],
        human_wins=human_wins if human_wins else ["None detected"],
        coaching_tip=coaching_tips.get(lowest_probe.probe_name, "Review lowest-scoring dimension for improvement opportunities.")
    )
