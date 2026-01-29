from backend.dspy_optimization.gauntlet_agent import GauntletAgent
import dspy
import os
import sys

# Ensure we can run from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def main():
    path = "backend/dspy_optimization/optimized_gauntlet_agent.json"
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run optimize.py first.")
        return

    # Load your new brain
    try:
        agent = GauntletAgent.from_file(path)
    except Exception as e:
        print(f"Failed to load agent: {e}")
        return

    print("=== OPTIMIZED AGENT INSPECTION ===")
    
    if hasattr(agent.prog, 'predictors'):
        predictors = agent.prog.predictors()
        if predictors:
            predictor = predictors[0]
        if hasattr(predictor, 'extended_signature'):
            print("\n[OPTIMIZED INSTRUCTION]")
            print(predictor.extended_signature.instructions)
        
        # Print the few-shot examples it selected
        if hasattr(predictor, 'demos'):
            print("\n[SELECTED FEW-SHOT EXAMPLES]")
            for i, demo in enumerate(predictor.demos):
                q = getattr(demo, 'challenge_question', 'N/A')
                a = getattr(demo, 'response', 'N/A')

                # Fallback to dict access if getattr fails
                if q == 'N/A' and isinstance(demo, dict):
                    q = demo.get('challenge_question', 'N/A')
                    a = demo.get('response', 'N/A')
                
                # Truncate for readability
                try: 
                    # print(f"Example {i+1} Raw: {demo}")
                    pass
                except:
                    pass
                q_short = (str(q)[:75] + '..') if len(str(q)) > 75 else str(q)
                a_short = (str(a)[:75] + '..') if len(str(a)) > 75 else str(a)
                print(f"Example {i+1}:")
                print(f"  Q: {q_short}")
                print(f"  A: {a_short}")
    else:
        print("Could not find predictors in the agent program.")

if __name__ == "__main__":
    main()
