
import json
import os
import dspy
import sys
import statistics
from typing import List, Dict
from pathlib import Path

# Ensure paths
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from backend.config import config
from backend.dspy_optimization.gauntlet_agent import GauntletAgent
from backend.dspy_optimization.metrics import get_engine

def load_data(path: Path) -> List[Dict]:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Data file not found at {path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        return []

def main():
    if not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        return

    # 1. Configuration
    lm = dspy.LM("openai/gpt-4o", api_key=config.OPENAI_API_KEY)
    dspy.settings.configure(lm=lm)

    # 2. Load Agents
    print("🤖 Loading Agents...")
    
    # Baseline (Unoptimized)
    unoptimized_agent = GauntletAgent()

    # Optimized
    opt_path = current_dir / "optimized_gauntlet_agent.json"
    if not opt_path.exists():
        print(f"Optimized agent not found at {opt_path}")
        return
    optimized_agent = GauntletAgent.from_file(str(opt_path))

    # 3. Load Data
    data_path = current_dir / "training_challenges.json"
    if not data_path.exists():
        print("Data file not found.")
        return
    
    # Limit to first 10 for speed if needed, or run all. 
    # With 16 examples, we can run all.
    examples = load_data(data_path)
    if not examples:
        return # Exit if no data
        
    print(f"📊 Running Comparison on {len(examples)} examples...")

    engine = get_engine()
    
    results: List[Dict] = []
    
    print(f"{'ID':<4} | {'Before':<8} | {'After':<8} | {'Delta':<8}")
    print("-" * 35)

    for i, ex in enumerate(examples):
        # Extract inputs
        p_context = ex.get('persona_context', '')
        question = ex.get('challenge_question') or ex.get('question', '')
        evidence = ex.get('deck_evidence') or ex.get('evidence', '')
        ideal = ex.get('ideal_answer') or ex.get('answer', '')

        if not question or not ideal:
            continue

        # Run Unoptimized
        try:
            pred_unopt = unoptimized_agent(
                persona_context=p_context,
                challenge_question=question,
                deck_evidence=evidence
            )
            score_unopt = engine.evaluate(user_answer=pred_unopt.response, ideal_answer=ideal).score
        except Exception as e:
            print(f"Error running unoptimized: {e}")
            score_unopt = 0.0

        # Run Optimized
        try:
            pred_opt = optimized_agent(
                persona_context=p_context,
                challenge_question=question,
                deck_evidence=evidence
            )
            score_opt = engine.evaluate(user_answer=pred_opt.response, ideal_answer=ideal).score
        except Exception as e:
            print(f"Error running optimized: {e}")
            score_opt = 0.0
            
        delta = score_opt - score_unopt
        
        print(f"{i+1:<4} | {score_unopt:.2f}     | {score_opt:.2f}     | {delta:+.2f}")
        
        results.append({
            "id": i+1,
            "question": question,
            "score_before": score_unopt,
            "score_after": score_opt,
            "delta": delta,
            "response_before": pred_unopt.response,
            "response_after": pred_opt.response
        })

    # 4. Generate Report
    if not results:
        print("No results generated.")
        return

    avg_before = statistics.mean([r['score_before'] for r in results])
    avg_after = statistics.mean([r['score_after'] for r in results])
    avg_delta = avg_after - avg_before
    
    report_path = current_dir / "dspy_comparison_analysis.md"
    
    with open(report_path, "w") as f:
        f.write("# DSPy Optimization: Before & After Analysis\n\n")
        f.write(f"**Date:** {os.popen('date').read().strip()}\n\n")
        f.write("## 🏆 Executive Summary\n")
        f.write(f"- **Final Average Score:** {avg_after:.2f} / 100\n")
        f.write(f"- **Baseline Score:** {avg_before:.2f} / 100\n")
        f.write(f"- **Improvement:** {avg_delta:+.2f} points\n\n")
        
        f.write("## 📊 Detailed Breakdown\n")
        f.write("| ID | Baseline Score | Optimized Score | Delta | Question |\n")
        f.write("| -- | :---: | :---: | :---: | --- |\n")
        
        for r in results:
            q_short = (r['question'][:50] + '...') if len(r['question']) > 50 else r['question']
            f.write(f"| {r['id']} | {r['score_before']:.1f} | {r['score_after']:.1f} | {r['delta']:+.1f} | {q_short} |\n")
            
        f.write("\n## 📝 Qualitative Examples\n")
        # Show top improved and top regression (if any)
        sorted_results = sorted(results, key=lambda x: x['delta'], reverse=True)
        top_improved = sorted_results[0]
        
        f.write(f"### Best Improvement (Example {top_improved['id']})\n")
        f.write(f"**Question:** {top_improved['question']}\n\n")
        f.write(f"**Before (Score: {top_improved['score_before']}):**\n> {top_improved['response_before']}\n\n")
        f.write(f"**After (Score: {top_improved['score_after']}):**\n> {top_improved['response_after']}\n\n")

    print(f"\nAnalysis complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
