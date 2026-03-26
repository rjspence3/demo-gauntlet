
import os
import pytest
from backend.config import Config

def test_production_security_check():
    # Remove any overrides so Config uses the insecure default SECRET_KEY.
    # In CI, SECRET_KEY may be set as a real env var, which would skip the check.
    saved = {k: os.environ.pop(k, None) for k in ["ENV_MODE", "SECRET_KEY", "ANTHROPIC_API_KEY"]}
    try:
        os.environ["ENV_MODE"] = "production"
        config = Config()

        # SECRET_KEY check must fire before ANTHROPIC_API_KEY check.
        with pytest.raises(ValueError, match="SECRET_KEY must be changed"):
            config.validate_security()

        print("Security check passed: Production mode with default key raises ValueError")
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

if __name__ == "__main__":
    try:
        test_production_security_check()
    except Exception as e:
        print(f"Verification failed: {e}")
        exit(1)
