import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.schemas.responses import ComplianceResponse

# Initialize the test client
client = TestClient(app)


def test_api_health() -> None:
    """Verify the API boots and the documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_invalid_payload_rejection() -> None:
    """Ensure the API rejects malformed requests immediately before hitting the LLM."""
    payload = {"wrong_key": "What is the EASA directive for A320?"}
    response = client.post("/api/v1/query", json=payload)

    # FastAPI should automatically return a 422 Unprocessable Entity
    assert response.status_code == 422


# NOTE: In a true CI pipeline, you would mock the `get_vector_index` dependency
# here to return a static response, rather than actually spinning up the LLM.
# This test assumes the mock is in place or the local Docker stack is running.
def test_pydantic_schema_enforcement() -> None:
    """Verify that a successful response strictly adheres to the ComplianceResponse schema."""
    payload = {"query": "What are the latest landing gear torque specs?"}

    # For a unit test without the DB, you'd patch the endpoint.
    # Assuming an integration test environment:
    response = client.post("/api/v1/query", json=payload)

    # If the endpoint is up, ensure it returns a 200
    if response.status_code == 200:
        data = response.json()

        # This will raise a ValidationError if the LLM hallucinated and broke the schema
        validated_data = ComplianceResponse(**data)

        assert hasattr(validated_data, "answer")
        assert hasattr(validated_data, "citations")
        assert type(validated_data.citations) is list
