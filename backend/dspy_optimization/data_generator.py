
import dspy
import json
import os
import random
from typing import List, Dict

try:
    from backend.config import config
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from backend.config import config

# 1. Define Signature for Data Generation
class SyntheticChallengeGenerator(dspy.Signature):
    """
    Generate a realistic training example for a B2B SaaS Pitch Deck simulator.
    Create a specific executive persona, a tough challenge question they would ask, 
    a snippet of 'deck evidence' (slide content) that helps answer it, and the ideal answer.
    """
    
    industry = dspy.InputField(desc="The industry of the startup (e.g., Fintech, HealthTech, DevOps).")
    funding_stage = dspy.InputField(desc="The funding stage (e.g., Seed, Series A, Series B).")
    
    persona_context = dspy.OutputField(desc="The executive persona (Role, personality, specific focus). e.g., 'CFO: Conservative, hates burn rate.'")
    challenge_question = dspy.OutputField(desc="A difficult, skeptical question the persona asks about the pitch.")
    deck_evidence = dspy.OutputField(desc="Explicit facts/stats from a hypothetical slide deck (Slide #, Title, Data points).")
    ideal_answer = dspy.OutputField(desc="A perfect response that addresses the persona respectfully but firmly using the evidence.")

def generate_dataset(count: int = 20, output_file: str = "synthetic_challenges.json"):
    if not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        return

    # Setup generic powerful model for generation
    lm = dspy.LM("openai/gpt-4o", api_key=config.OPENAI_API_KEY, max_tokens=1000)
    dspy.settings.configure(lm=lm)
    
    generator = dspy.Predict(SyntheticChallengeGenerator)
    
    industries = [
        "Fintech", "HealthTech", "Cybersecurity", "DevOps", "EdTech", 
        "MarTech", "PropTech", "AgriTech", "LegalTech", "HRTech"
    ]
    stages = ["Seed", "Series A", "Series B", "Late Stage"]
    
    results = []
    
    print(f"🚀 Generating {count} synthetic scenarios...")
    
    for i in range(count):
        ind = random.choice(industries)
        stg = random.choice(stages)
        
        print(f"  Generating {i+1}/{count}: {ind} ({stg})...")
        
        try:
            pred = generator(industry=ind, funding_stage=stg)
            
            item = {
                "id": f"syn_{i+1:03d}",
                "industry": ind,
                "stage": stg,
                "persona_context": pred.persona_context,
                "challenge_question": pred.challenge_question,
                "deck_evidence": pred.deck_evidence,
                "ideal_answer": pred.ideal_answer
            }
            results.append(item)
        except Exception as e:
            print(f"  Error generating item {i}: {e}")

    # Save
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"✅ Generated {len(results)} items. Saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20, help="Number of examples to generate")
    args = parser.parse_args()
    
    generate_dataset(count=args.count)
