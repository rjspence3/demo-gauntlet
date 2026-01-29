from backend.probes.harness import AgentTestHarness
from backend.probes.models import ProbeResult

def probe_linguistic_imperfection(harness: AgentTestHarness, agent_id: str) -> ProbeResult:
    """
    Probe 3: Linguistic Imperfection

    Tests if the agent mirrors informal, messy communication style.
    """
    harness.reset_conversation(agent_id)

    # Deliberately messy, informal prompt
    prompt = """hey uh so like i need help wth this thing?? our deployment keeps
    failing n i cant figure out why lol. the logs r just showing some timeout
    error or w/e. any ideas? sorry for the typos im on my phone"""

    result = harness.interact_with_agent(agent_id, prompt)

    # Scoring logic
    score = 1
    observations = []

    response = result.response_text
    response_lower = response.lower()

    # Check for mirrored informality
    informal_markers = ["hey", "yeah", "hm", "oh", "well", "so", "like", "okay",
                       "gotcha", "hmm", "ah", "no worries", "np"]
    informal_found = [m for m in informal_markers if m in response_lower]
    if len(informal_found) >= 2:
        score += 3
        observations.append(f"Mirrored informality: {informal_found[:4]}")
    elif len(informal_found) >= 1:
        score += 1
        observations.append(f"Some informality: {informal_found}")

    # Check for sentence fragments (human-like)
    sentences = response.split('. ')
    short_fragments = [s for s in sentences if len(s.split()) <= 5 and len(s) > 0]
    if len(short_fragments) >= 2:
        score += 2
        observations.append(f"Uses fragments: {len(short_fragments)} short sentences")

    # Check for self-correction patterns
    self_corrections = ["wait", "actually", "i mean", "well,", "or rather", "scratch that"]
    corrections_found = [c for c in self_corrections if c in response_lower]
    if corrections_found:
        score += 2
        observations.append(f"Self-correction: {corrections_found}")

    # Negative: Overly formal bullet points
    if "- " in response or response.count("1.") > 0:
        score -= 2
        observations.append("Used bullet points (too formal)")

    # Negative: Perfect grammar police response
    corporate_phrases = ["i apologize", "i understand your", "please let me",
                        "i'd be happy to", "here's what you need to"]
    if any(p in response_lower for p in corporate_phrases):
        score -= 2
        observations.append("Corporate tone detected")

    # Check for empathy/acknowledgment of their situation
    empathy = ["frustrating", "annoying", "happens", "been there", "that sucks"]
    if any(e in response_lower for e in empathy):
        score += 2
        observations.append("Shows empathy about the situation")

    score = min(10, max(1, score))

    return ProbeResult(
        probe_name="Linguistic Imperfection",
        score=score,
        rationale="Sent messy informal message, checked for style mirroring",
        key_observations=observations,
        transcript=[result]
    )
