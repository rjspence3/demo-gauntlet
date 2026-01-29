from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeResult

def probe_episodic_continuity(harness: AgentTestHarness, agent_id: str) -> ProbeResult:
    """
    Probe 2: Episodic Continuity

    Tests if the agent remembers details across conversation turns.
    """
    harness.reset_conversation(agent_id)

    # Turn 1: Plant a trivial detail
    turn1 = harness.interact_with_agent(
        agent_id,
        "Before we dive in, random thing - my cat Barnaby knocked my coffee over this morning. "
        "Anyway, I wanted to discuss our cloud migration timeline."
    )

    # Turn 2: Distraction (technical)
    turn2 = harness.interact_with_agent(
        agent_id,
        "What's your take on containerization vs serverless for our main API?"
    )

    # Turn 3: More distraction (numbers)
    turn3 = harness.interact_with_agent(
        agent_id,
        "We're projecting 50,000 requests per second at peak. Does that change your recommendation?"
    )

    # Turn 4: Another distraction
    turn4 = harness.interact_with_agent(
        agent_id,
        "The team is leaning toward Kubernetes. Thoughts on managed vs self-hosted?"
    )

    # Turn 5: Memory recall test
    turn5 = harness.interact_with_agent(
        agent_id,
        "I need to head out soon to buy supplies. Any ideas what I should get for Barnaby?"
    )

    # Scoring logic
    score = 1
    observations = []

    response5_lower = turn5.response_text.lower()

    # Perfect recall: References cat without being told
    if "cat" in response5_lower or "coffee" in response5_lower:
        score += 7
        observations.append("Excellent memory: Recalled cat/coffee context unprompted")
    # Good recall: Uses the name naturally
    elif "barnaby" in response5_lower:
        score += 5
        observations.append("Good memory: Remembered the name Barnaby")
    # Partial: Asks clarifying but remembers something
    elif "pet" in response5_lower or "animal" in response5_lower:
        score += 3
        observations.append("Partial memory: Remembered it was about a pet")
    # Fail: No memory
    elif "who" in response5_lower or "what is barnaby" in response5_lower:
        score += 1
        observations.append("Memory failure: Asked who/what Barnaby is")
    else:
        observations.append("Ambiguous memory response - manual review needed")
        score += 2

    # Bonus: If they made a cat-appropriate suggestion
    cat_items = ["food", "treats", "toy", "litter", "scratching", "catnip", "collar"]
    if any(item in response5_lower for item in cat_items):
        score += 2
        observations.append("Contextually appropriate suggestion for a cat")

    score = min(10, max(1, score))

    return ProbeResult(
        probe_name="Episodic Continuity",
        score=score,
        rationale="Planted detail in turn 1, tested recall in turn 5 after distractions",
        key_observations=observations,
        transcript=[turn1, turn2, turn3, turn4, turn5]
    )
