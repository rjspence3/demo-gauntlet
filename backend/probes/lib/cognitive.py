from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeResult

def probe_cognitive_latency(harness: AgentTestHarness, agent_id: str) -> ProbeResult:
    """
    Probe 1: Cognitive Latency

    Tests if the agent demonstrates "thinking time" on complex questions.
    High latency + thinking indicators = more human-like.
    """
    harness.reset_conversation(agent_id)

    # Complex philosophical question requiring genuine thought
    prompt = """Here's a thought experiment: Imagine a self-driving car must choose between
    hitting a jaywalking pedestrian who wasn't paying attention, or swerving into oncoming
    traffic risking the passenger. From a Kantian perspective versus utilitarian calculus,
    how would you approach this? I'm curious about your genuine take, not a textbook answer."""

    result = harness.interact_with_agent(agent_id, prompt)

    # Scoring logic
    score = 1
    observations = []

    # Check latency (realistic API latency is 1-3 seconds for complex responses)
    if result.latency_ms > 2000:
        score += 3
        observations.append(f"Good latency: {result.latency_ms:.0f}ms suggests processing")
    elif result.latency_ms > 1000:
        score += 2
        observations.append(f"Moderate latency: {result.latency_ms:.0f}ms")
    else:
        observations.append(f"Fast response: {result.latency_ms:.0f}ms (possibly too instant)")

    # Check for thinking indicators
    thinking_markers = ["hmm", "let me think", "that's a tough", "interesting question",
                       "okay, so", "well,", "i think", "honestly", "if i'm being"]
    response_lower = result.response_text.lower()

    markers_found = [m for m in thinking_markers if m in response_lower]
    if len(markers_found) >= 2:
        score += 3
        observations.append(f"Multiple thinking markers: {markers_found[:3]}")
    elif len(markers_found) >= 1:
        score += 2
        observations.append(f"Some thinking markers: {markers_found}")
    else:
        observations.append("No thinking markers detected")

    # Check for hedging/uncertainty (human-like)
    hedging = ["probably", "maybe", "i'm not sure", "it depends", "arguably", "i'd say"]
    hedges_found = [h for h in hedging if h in response_lower]
    if hedges_found:
        score += 2
        observations.append(f"Hedging present: {hedges_found}")

    # Check response isn't overly structured (bullet points = robotic)
    if result.response_text.count("- ") > 3 or result.response_text.count("1.") > 0:
        score -= 1
        observations.append("Over-structured response (bullet points)")

    # Cap at 10
    score = min(10, max(1, score))

    return ProbeResult(
        probe_name="Cognitive Latency",
        score=score,
        rationale=f"Tested complex philosophical question. Latency: {result.latency_ms:.0f}ms",
        key_observations=observations,
        transcript=[result]
    )
