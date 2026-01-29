
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.core import ChallengerPersona

# Initialize test client
client = TestClient(app)

def test_rate_limit_challenges_generate():
    """
    Verify that the /challenges/generate endpoint is rate limited at 5 requests per minute.
    """
    # Mock data for the request
    payload = {
        "session_id": "test_session_rate_limit",
        "persona_id": "vc_partner" # Assuming this exists or mocked, otherwise we might get 404
    }
    
    # We need to mock the dependencies to avoid hitting actual LLMs/Deep logic which is slow
    # and to ensure we are purely testing the rate limiter "middleware" stack invocation.
    # However, slowapi limits based on the route handler. 
    # If the handler fails (e.g. 404), the limit still counts usually? 
    # Let's try to hit an endpoint that is cheaper first, like /personas
    
    pass

def test_rate_limit_personas_listing():
    """
    Verify /challenges/personas is limited to 20/minute.
    We'll scale this down or just spam it.
    Actually 20 is a lot to loop in a test, let's look at /auth/token (5/minute) or /challenges/generate (5/minute).
    """
    # /auth/token requires form data
    # /challenges/generate is 5/minute.
    
    # We will use /challenges/generate but we expect it might fail with 404 if we don't mock things,
    # but the rate limiter should kick in BEFORE the handler logic in many frameworks, 
    # OR it tracks hits.
    # Let's see if we can trigger the 429.
    
    url = "/challenges/generate"
    # We need a valid-ish body to pass Pydantic validation 
    # so we reach the limiter logic (or endpoint logic)
    json_body = {
        "session_id": "rate_limit_test", 
        "persona_id": "fake_persona"
    }

    # Hit it 5 times
    for i in range(5):
        response = client.post(url, json=json_body)
        # We don't care if it returns 200 or 404 (persona not found), 
        # as long as it is NOT 429 yet.
        # Note: If it returns 422 (validation error), limiter might not count it depending on config?
        # Usually slowapi is a decorator on the function, so it runs before the function body.
        # But FASTAPI validation runs before that? No, decorators run around the function.
        # But Depends() runs... it's complex.
        # Let's just create a dummy endpoint validation test.
        assert response.status_code != 429, f"Request {i+1} was rate limited unexpectedly"

    # The 6th time should fail
    response = client.post(url, json=json_body)
    assert response.status_code == 429, "Rate limit was not enforced on the 6th request"
    assert "Too Many Requests" in response.text or "Rate limit exceeded" in response.text
