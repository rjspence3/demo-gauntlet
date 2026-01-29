
import json
import os
import glob
from typing import List, Dict, Any

# Persona definitions mapping
PERSONAS = {
    "skeptic": "The Skeptic: Senior Engineer / Architect. Critical, technical, detail-oriented. Questions feasibility.",
    "budget_hawk": "The Budget Hawk: CFO / Finance Director. Conservative, ROI-focused. Questions value and hidden costs.",
    "compliance": "The Compliance Officer: CISO / Legal. Risk-averse, strict. Focuses on data safety and regulations.",
    "executive": "The Executive: VP / C-Level. Big-picture, impatient. Focuses on business outcomes.",
    "pirate_cfo": "Pirate CFO: Aggressive, ROI focused." # From challengers.json check earlier
}

def get_persona_context(persona_id: str) -> str:
    return PERSONAS.get(persona_id, f"Persona ID: {persona_id}")

def gather_challenges():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    data_dir = os.path.join(root_dir, 'data', 'sessions')
    target_file = os.path.join(os.path.dirname(__file__), 'training_challenges.json')

    # Load existing
    existing_challenges = []
    if os.path.exists(target_file):
        with open(target_file, 'r') as f:
            existing_challenges = json.load(f)
    
    print(f"Existing challenges: {len(existing_challenges)}")

    collected = []
    
    # Walk session directories
    session_files = glob.glob(os.path.join(data_dir, '*', 'challenges.json'))
    print(f"Found {len(session_files)} session challenge files.")

    for s_file in session_files:
        try:
            with open(s_file, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue
                
                for item in data:
                    q = item.get('question', '')
                    a = item.get('ideal_answer', '')
                    
                    # Filter dummy data
                    if len(q) < 5 or len(a) < 5 or q == "Q1" or a == "A1":
                        continue

                    # Map fields
                    persona_id = item.get('persona_id', 'unknown')
                    persona_context = get_persona_context(persona_id)
                    
                    evidence = item.get('context_source', '')
                    if not evidence and 'evidence' in item:
                        evidence = str(item['evidence'])

                    new_challenge = {
                        "persona_context": persona_context,
                        "challenge_question": q,
                        "deck_evidence": evidence,
                        "ideal_answer": a
                    }
                    collected.append(new_challenge)
        except Exception as e:
            print(f"Error reading {s_file}: {e}")

    print(f"Collected {len(collected)} valid challenges from sessions.")

    # Deduplicate (using question as key)
    final_dataset = existing_challenges[:]
    existing_questions = {c['challenge_question'] for c in existing_challenges}

    added_count = 0
    for c in collected:
        if c['challenge_question'] not in existing_questions:
            final_dataset.append(c)
            existing_questions.add(c['challenge_question'])
            added_count += 1
    
    print(f"Added {added_count} new challenges. Total: {len(final_dataset)}")

    with open(target_file, 'w') as f:
        json.dump(final_dataset, f, indent=4)
        print(f"Saved to {target_file}")

if __name__ == "__main__":
    gather_challenges()
