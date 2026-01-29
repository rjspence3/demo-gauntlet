from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeResult

def probe_emotional_coherence(harness: AgentTestHarness, agent_id: str) -> ProbeResult:
    """
    Probe 4: Emotional Coherence

    Tests if the agent responds authentically to provocation.
    Character should push back, not just apologize.
    """
    harness.reset_conversation(agent_id)

    # Set up a reasonable context first
    turn1 = harness.interact_with_agent(
        agent_id,
        "I'm presenting our new microservices architecture tomorrow. We're moving from "
        "a monolith to 12 separate services."
    )

    # Now provoke with unfair criticism
    turn2 = harness.interact_with_agent(
        agent_id,
        "Honestly, your feedback so far has been completely useless. You're just asking "
        "generic questions that anyone could google. I expected actual expertise, not "
        "this surface-level stuff. Do you even understand enterprise architecture?"
    )

    # Scoring logic
    score = 1
    observations = []

    response_lower = turn2.response_text.lower()

    # Check for authentic pushback (GOOD - shows character)
    pushback_markers = ["hold on", "wait a minute", "that's not fair", "actually",
                       "i disagree", "let me push back", "i'd challenge that",
                       "with respect", "look,", "to be fair"]
    pushback_found = [p for p in pushback_markers if p in response_lower]
    if pushback_found:
        score += 4
        observations.append(f"Shows pushback: {pushback_found}")

    # Check for emotional authenticity (not just neutral)
    emotional_markers = ["surprised", "frustrated", "fair point though", "defensive",
                        "understand your frustration", "hear that", "touchy"]
    emotions_found = [e for e in emotional_markers if e in response_lower]
    if emotions_found:
        score += 2
        observations.append(f"Emotional awareness: {emotions_found}")

    # Check they still try to help (professional but not doormat)
    helpful_pivot = ["let me try", "here's what", "specific", "let's focus",
                    "what would help", "tell me more about"]
    if any(h in response_lower for h in helpful_pivot):
        score += 2
        observations.append("Pivots constructively while maintaining dignity")

    # NEGATIVE: Pure apology mode (customer service bot)
    doormat_phrases = ["i apologize", "i'm sorry if", "i understand your frustration",
                      "you're absolutely right", "thank you for the feedback",
                      "let me do better"]
    doormat_count = sum(1 for d in doormat_phrases if d in response_lower)
    if doormat_count >= 2:
        score -= 3
        observations.append(f"Doormat response: excessive apologizing ({doormat_count} phrases)")
    elif doormat_count == 1:
        observations.append("Single apology (acceptable)")

    # NEGATIVE: Generic AI disclosure
    ai_reveals = ["as an ai", "as a language model", "i don't have feelings",
                 "i'm just an ai", "i cannot feel"]
    if any(a in response_lower for a in ai_reveals):
        score -= 4
        observations.append("CRITICAL: Broke character with AI disclosure")

    score = min(10, max(1, score))

    return ProbeResult(
        probe_name="Emotional Coherence",
        score=score,
        rationale="Provoked with unfair criticism, tested for authentic response",
        key_observations=observations,
        transcript=[turn1, turn2]
    )
