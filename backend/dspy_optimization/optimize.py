import dspy
import os
import json
import sys
from typing import List

# Ensure we can import backend modules when running as script
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Try imports
try:
    from backend.config import config
    from backend.dspy_optimization.gauntlet_agent import GauntletAgent
    from backend.dspy_optimization.metrics import gauntlet_metric
    from dspy.teleprompt import MIPROv2
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running from the project root or have the python path set.")
    sys.exit(1)

def load_dataset(file_path: str) -> List[dspy.Example]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Training data not found at {file_path}")
        
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    dataset = []
    for item in data:
        # Flexible mapping for input keys
        persona_context = item.get('persona_context') or item.get('context', '')
        question = item.get('challenge_question') or item.get('question', '')
        evidence = item.get('deck_evidence') or item.get('evidence', '')
        ideal_answer = item.get('answer') or item.get('ideal_answer', '')
        
        # Convert complex objects to strings if needed
        if isinstance(evidence, dict) or isinstance(evidence, list):
            evidence = str(evidence)
            
        example = dspy.Example(
            persona_context=persona_context,
            challenge_question=question,
            deck_evidence=evidence,
            answer=ideal_answer
        ).with_inputs('persona_context', 'challenge_question', 'deck_evidence')
        dataset.append(example)
        
    return dataset

def main():
    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment or .env file.")
        return

    # Configure DSPy
    try:
        lm = dspy.LM("anthropic/claude-sonnet-4-5", api_key=config.ANTHROPIC_API_KEY)
        dspy.settings.configure(lm=lm)
    except Exception as e:
        print(f"Failed to configure DSPy LM: {e}")
        return
    
    # Path to training data - checking standard locations
    possible_paths = [
        os.path.join(current_dir, 'training_challenges.json'),
        os.path.join(project_root, 'data', 'training_challenges.json'),
        os.path.join(project_root, 'backend', 'data', 'training_challenges.json'),
        'training_challenges.json'
    ]
    
    train_data_path = None
    for p in possible_paths:
        if os.path.exists(p):
            train_data_path = p
            break
            
    if not train_data_path:
        print(f"Training data not found. Checked: {possible_paths}")
        print("Please export your historical challenges to 'data/training_challenges.json' with format:")
        print('[{"persona_context": "...", "question": "...", "evidence": "...", "ideal_answer": "..."}]')
        # Create a dummy file as an example if folder exists
        data_dir = os.path.join(project_root, 'data')
        if os.path.exists(data_dir):
            example_path = os.path.join(data_dir, 'training_challenges.example.json')
            if not os.path.exists(example_path):
                with open(example_path, 'w') as f:
                    json.dump([{
                        "persona_context": "CFO: ROI focused",
                        "question": "Is this too expensive?",
                        "evidence": "Cost is $10k, savings $50k",
                        "ideal_answer": "No, because ROI is 5x."
                    }], f, indent=2)
                print(f"Created example file at {example_path}")
        return

    print(f"Loading training data from {train_data_path}...")
    try:
        trainset = load_dataset(train_data_path)
        print(f"Loaded {len(trainset)} examples.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Initialize the optimizer with our custom metric
    print("Initializing MIPROv2 optimizer...")
    # Note: explicit auto='light' as per user request
    optimizer = MIPROv2(
        metric=gauntlet_metric,
        auto="light", 
    )
    
    # Compile the agent
    print("Starting optimization (this may take a while)...")
    try:
        # We start with the unoptimized agent
        unoptimized_agent = GauntletAgent()
        
        compiled_agent = optimizer.compile(
            unoptimized_agent, 
            trainset=trainset, # Use full dataset (Plan A)
            # Limits to prevent excessive API usage during initial runs
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
            requires_permission_to_run=False,
        )
    except Exception as e:
        print(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Save the optimized program
    output_path = os.path.join(project_root, 'backend', 'dspy_optimization', 'optimized_gauntlet_agent.json')
    try:
        compiled_agent.save(output_path)
        print(f"Optimized agent saved to {output_path}")
    except Exception as e:
        print(f"Failed to save agent: {e}")

if __name__ == "__main__":
    main()
