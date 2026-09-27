"""Pytest configuration and test client fixture."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from apps.api.core.database import get_db


def override_get_db():
    """Provides None for database session in unit tests."""
    yield None


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a synchronous FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
