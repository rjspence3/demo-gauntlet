
# DSPy Optimization & Benchmarking

This directory contains tools for optimizing and benchmarking the Gauntlet Agent.

## Files

- **`gauntlet_agent.py`**: The defining class for the DSPy agent module.
- **`standard_agent.py`**: A baseline agent using standard "Prompt Engineering" techniques (Zero-Shot CoT with robust instructions) for comparison.
- **`optimize.py`**: The script using `MIPROv2` to optimize `GauntletAgent` against `training_challenges.json`.
- **`run_large_benchmark.py`**: The main entry point for generating data and running a head-to-head comparison.

## Usage

### 1. Generate Data & Run Benchmark
To generate a synthetic dataset (e.g., 50 simulated pitch decks) and run the comparison:

```bash
python backend/dspy_optimization/run_large_benchmark.py
```

This will:
1. Check for `synthetic_challenges.json`. If missing, it generates 50 examples using GPT-4o.
2. Load the `StandardAgent` (Baseline).
3. Load the `GauntletAgent` (Optimized if `optimized_gauntlet_agent.json` exists, else Unoptimized).
4. Run both agents on all challenges.
5. Grade responses using the `EvaluationEngine` (Metrics: Accuracy, Completeness, Clarity, Truth).
6. Output a report to `benchmark_report_large.md`.

### 2. Generate Data Only
To purely generate data without running the benchmark:

```bash
python backend/dspy_optimization/data_generator.py --count 100
```

### 3. Inspect the Optimized Agent
To see what instructions and few-shot examples DSPy selected:

```bash
python backend/dspy_optimization/inspect_agent.py
```
