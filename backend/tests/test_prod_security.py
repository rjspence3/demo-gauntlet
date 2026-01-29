
import os
import pytest
from backend.config import Config

def test_production_security_check():
    # Simulate production environment
    os.environ["ENV_MODE"] = "production"
    # Ensure default key is used (which it is in the code I saw)
    
    config = Config()
    
    # Check that validate_security raises ValueError
    with pytest.raises(ValueError, match="SECRET_KEY must be changed"):
        config.validate_security()
    
    print("Security check passed: Production mode with default key raises ValueError")

if __name__ == "__main__":
    try:
        test_production_security_check()
    except Exception as e:
        print(f"Verification failed: {e}")
        exit(1)
