
import json
import os
import dspy
import sys

# Ensure backend imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.config import config
from backend.dspy_optimization.gauntlet_agent import GauntletAgent
from backend.dspy_optimization.metrics import get_engine

def run_diagnostics():
    if not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        return

    # 1. Setup
    lm = dspy.LM("openai/gpt-4o", api_key=config.OPENAI_API_KEY)
    dspy.settings.configure(lm=lm)

    # 2. Load the "Brain"
    print("🧠 Loading Optimized Agent...")
    agent_path = os.path.join(os.path.dirname(__file__), "optimized_gauntlet_agent.json")
    if not os.path.exists(agent_path):
        print(f"Agent file not found at {agent_path}")
        return
        
    # Start with fresh agent, then load state
    agent = GauntletAgent()
    agent.load(agent_path)

    # 3. Load Data
    data_path = os.path.join(os.path.dirname(__file__), "training_challenges.json")
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return

    with open(data_path, "r") as f:
        # Just testing the first 5 to spot patterns
        data = json.load(f)[:5]

    print("\n📊 RUBRIC BREAKDOWN")
    print("=" * 65)

    engine = get_engine()

    for i, ex in enumerate(data):
        # Map fields correctly based on training_challenges.json
        # The file uses: persona_context, challenge_question, deck_evidence, ideal_answer
        p_context = ex.get('persona_context', '')
        question = ex.get('challenge_question') or ex.get('question', '')
        evidence = ex.get('deck_evidence') or ex.get('evidence', '')
        ideal = ex.get('ideal_answer') or ex.get('answer', '')

        # Run the agent
        pred = agent(
            persona_context=p_context,
            challenge_question=question,
            deck_evidence=evidence
        )

        # Score it using engine
        result = engine.evaluate(
            user_answer=pred.response,
            ideal_answer=ideal
        )
        
        breakdown = result.breakdown
        total_score = result.score

        # Print the "Forensic Report" for this question
        print(f"\n📝 Scenario {i+1}: {question[:50]}...")
        print(f"   Response Length: {len(pred.response.split())} words")
        print("-" * 30)
        
        # Display the 4 Dimensions clearly
        # Weights from engine: Acc 0.45, Comp 0.35, Clarity 0.15, Truth 0.05
        print(f"   🎯 Accuracy      (0.45): {breakdown.get('accuracy', 0):.2f}")
        print(f"   📚 Completeness  (0.35): {breakdown.get('completeness', 0):.2f}")
        print(f"   👓 Clarity       (0.15): {breakdown.get('clarity', 0):.2f}")
        print(f"   ⚖️  Truth Align   (0.05): {breakdown.get('truth_alignment', 0):.2f}")
        print("-" * 30)
        print(f"   🏆 TOTAL SCORE:  {total_score:.2f}")

if __name__ == "__main__":
    run_diagnostics()
