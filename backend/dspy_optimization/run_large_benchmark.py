
import json
import os
import dspy
import sys
import statistics
import concurrent.futures
from typing import List, Dict

# Ensure paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.config import config
from backend.dspy_optimization.gauntlet_agent import GauntletAgent
from backend.dspy_optimization.standard_agent import StandardAgent
from backend.dspy_optimization.metrics import get_engine

def load_or_generate_data(path: str, count: int = 50):
    if not os.path.exists(path):
        print(f"📉 Data file not found. Generating {count} examples...")
        from backend.dspy_optimization.data_generator import generate_dataset
        generate_dataset(count=count, output_file=os.path.basename(path))
    
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def evaluate_single(item, agent, engine, agent_name):
    """Run a single evaluation to be parallelized."""
    p_context = item.get('persona_context', '')
    question = item.get('challenge_question') or item.get('question', '')
    evidence = item.get('deck_evidence') or item.get('evidence', '')
    ideal = item.get('ideal_answer') or item.get('answer', '')
    
    if not question or not ideal:
        return None

    try:
        pred = agent(
            persona_context=p_context,
            challenge_question=question,
            deck_evidence=evidence
        )
        
        # Grading
        result = engine.evaluate(user_answer=pred.response, ideal_answer=ideal)
        score = result.score
        
        return {
            "score": score,
            "response": pred.response,
            "breakdown": result.breakdown
        }
    except Exception as e:
        print(f"Error {agent_name} on {item.get('id', '?')}: {e}")
        return {"score": 0.0, "response": "ERROR", "breakdown": {}}

def main():
    if not config.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found.")
        return

    # 1. Config
    lm = dspy.LM("anthropic/claude-sonnet-4-5", api_key=config.ANTHROPIC_API_KEY)
    dspy.settings.configure(lm=lm)
    engine = get_engine()

    # 2. Load Data
    data_file = os.path.join(current_dir, "synthetic_challenges.json")
    challenges = load_or_generate_data(data_file, count=50) # Set to 50 for "Large Set"
    
    print(f"📊 Benchmarking {len(challenges)} scenarios...")

    # 3. Load Agents
    # A. Standard (Mocking 'Normal Prompting')
    standard_agent = StandardAgent()
    
    # B. DSPy Optimized
    opt_path = os.path.join(current_dir, "optimized_gauntlet_agent.json")
    if not os.path.exists(opt_path):
        print(f"Warning: Optimized agent not found at {opt_path}. Using fresh agent.")
        dspy_agent = GauntletAgent()
    else:
        dspy_agent = GauntletAgent.from_file(opt_path)

    results = []
    
    print(f"{'ID':<6} | {'Normal':<8} | {'DSPy':<8} | {'Delta':<8}")
    print("-" * 40)

    # 4. Execution Loop (Sequential for stability/clarity, can be parallelized)
    for i, ex in enumerate(challenges):
        # Run Standard
        res_std = evaluate_single(ex, standard_agent, engine, "Standard")
        
        # Run DSPy
        res_dspy = evaluate_single(ex, dspy_agent, engine, "DSPy")
        
        if not res_std or not res_dspy:
            continue
            
        delta = res_dspy['score'] - res_std['score']
        
        print(f"{ex.get('id', i):<6} | {res_std['score']:.2f}     | {res_dspy['score']:.2f}     | {delta:+.2f}")
        
        results.append({
            "id": ex.get('id', i),
            "industry": ex.get('industry', 'N/A'),
            "question": ex.get('challenge_question'),
            "score_std": res_std['score'],
            "score_dspy": res_dspy['score'],
            "delta": delta,
            "resp_std": res_std['response'],
            "resp_dspy": res_dspy['response']
        })

    # 5. Analysis
    avg_std = statistics.mean([r['score_std'] for r in results])
    avg_dspy = statistics.mean([r['score_dspy'] for r in results])
    
    # Save Report
    report_path = os.path.join(current_dir, "benchmark_report_large.md")
    with open(report_path, "w") as f:
        f.write("# 🏟️ DSPy vs Standard Prompting Benchmark\n\n")
        f.write(f"**Scenarios Tested:** {len(results)}\n")
        f.write(f"**Date:** {os.popen('date').read().strip()}\n\n")
        
        f.write("## 🏁 Finals\n")
        f.write(f"- **Standard Prompting Avg:** {avg_std:.2f}\n")
        f.write(f"- **DSPy Optimized Avg:**     {avg_dspy:.2f}\n")
        f.write(f"- **Winner:** {'DSPy' if avg_dspy > avg_std else 'Standard'} by {abs(avg_dspy - avg_std):.2f} pts\n\n")
        
        f.write("## 📉 Raw Data\n")
        f.write("| ID | Industry | Standard | DSPy | Delta | Question |\n")
        f.write("| -- | -- | :---: | :---: | :---: | --- |\n")
        for r in results: 
            q_short = (r['question'][:40] + '..') if r['question'] else ''
            f.write(f"| {r['id']} | {r['industry']} | {r['score_std']:.1f} | {r['score_dspy']:.1f} | {r['delta']:+.1f} | {q_short} |\n")
            
    print(f"\n✅ Benchmark Complete. Report: {report_path}")

if __name__ == "__main__":
    main()
