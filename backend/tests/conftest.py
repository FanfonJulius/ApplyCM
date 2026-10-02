import os
import tempfile

# Must be set before any `app` import: settings and the engine are module-level.
_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE.name}"
os.environ["JWT_SECRET"] = "test-secret-not-used-anywhere-else-0123456789"
os.environ["EMAIL_BACKEND"] = "console"
os.environ.pop("EMAIL_REDIRECT_TO", None)

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.database import engine
from app.main import app


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _auth_headers(client: TestClient, email: str, password: str = "s3cret-pass") -> dict:
    assert client.post("/api/auth/signup", json={"email": email, "password": password}).status_code == 201
    res = client.post("/api/auth/login", data={"username": email, "password": password})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return _auth_headers(client, "student@example.com")


@pytest.fixture
def make_auth(client):
    return lambda email: _auth_headers(client, email)


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    try:
        os.unlink(_DB_FILE.name)
    except (PermissionError, OSError):
        pass
