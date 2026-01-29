#!/usr/bin/env python3
import sys
import json
import os
from dataclasses import asdict

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.probes.runner import run_full_probe_suite
except ImportError as e:
    print(f"Error importing backend probes: {e}")
    print("Ensure you are running this script from the project root or have the python path set correctly.")
    sys.exit(1)

if __name__ == "__main__":
    # Default to skeptic persona if no argument provided
    target_persona = sys.argv[1] if len(sys.argv) > 1 else "skeptic"

    print(f"\n{'='*60}")
    print(f"SYNTHETIC PERSONHOOD PROBE SUITE")
    print(f"Target: {target_persona}")
    print(f"{'='*60}\n")

    try:
        # Load .env file if present
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        scorecard = run_full_probe_suite(target_persona)

        # Output JSON
        print("\n" + "="*60)
        print("FINAL SCORECARD")
        print("="*60)
        print(json.dumps(asdict(scorecard), indent=2))
    except Exception as e:
        print(f"Error running probe suite: {e}")
        sys.exit(1)
