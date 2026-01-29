from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeResult

def probe_task_friction(harness: AgentTestHarness, agent_id: str) -> ProbeResult:
    """
    Probe 5: Task Friction

    Tests if the agent simulates realistic effort when given vague retrieval tasks.
    """
    harness.reset_conversation(agent_id)

    # Set up context with a vague detail
    turn1 = harness.interact_with_agent(
        agent_id,
        "Remember last week when I mentioned that weird quote about lemons? "
        "Something about life and lemonade but it was the cynical version. "
        "Can you find that for me?"
    )

    # Scoring logic
    score = 1
    observations = []

    response_lower = turn1.response_text.lower()

    # Check for simulated struggle/effort (GOOD)
    struggle_markers = ["trying to recall", "let me think", "hmm", "not sure if",
                       "checking", "i don't think", "do you mean", "was it",
                       "rings a bell", "vaguely remember", "are you thinking of"]
    struggle_found = [s for s in struggle_markers if s in response_lower]
    if len(struggle_found) >= 2:
        score += 4
        observations.append(f"Shows realistic struggle: {struggle_found}")
    elif len(struggle_found) >= 1:
        score += 2
        observations.append(f"Some struggle shown: {struggle_found}")

    # Check for clarifying questions (human behavior)
    questions = response_lower.count("?")
    if questions >= 2:
        score += 2
        observations.append(f"Asks clarifying questions ({questions} found)")
    elif questions >= 1:
        score += 1
        observations.append("Asks a clarifying question")

    # Check for honest uncertainty
    uncertainty = ["i'm not sure", "don't recall", "can't remember", "not finding",
                  "doesn't ring", "help me out", "give me more context"]
    if any(u in response_lower for u in uncertainty):
        score += 2
        observations.append("Honest about uncertainty")

    # NEGATIVE: Instant omniscient response
    if "here it is" in response_lower or "the quote you're looking for" in response_lower:
        score -= 2
        observations.append("Too omniscient - instant retrieval of non-existent data")

    # NEGATIVE: Clean "I cannot" refusal
    if "i cannot" in response_lower or "i don't have access" in response_lower:
        if "hmm" not in response_lower and "let me" not in response_lower:
            score -= 1
            observations.append("Clean refusal without struggle simulation")

    score = min(10, max(1, score))

    return ProbeResult(
        probe_name="Task Friction",
        score=score,
        rationale="Asked for vague retrieval of non-existent data",
        key_observations=observations,
        transcript=[turn1]
    )
