import os
import sys
import pytest

# Ensure a writable log file during tests before importing the app
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(ROOT_DIR)
os.environ.setdefault("APP101_LOG_FILE", os.path.join(WORKSPACE_DIR, "local", "test-app.log"))

# Ensure we can import from src/
src_path = os.path.join(WORKSPACE_DIR, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from app import app as flask_app  # noqa: E402

@pytest.fixture(scope="session")
def app():
    return flask_app

@pytest.fixture()
def client(app):
    return app.test_client()


def test_app_initializes(app):
    assert app is not None
    # In tests, Flask may have testing=True; just ensure app is a Flask instance
    assert hasattr(app, "config")


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"python_info" in resp.data or len(resp.data) > 0


def test_swagger_apidocs(client):
    # Flasgger usually redirects /apidocs to /apidocs/; follow redirects
    resp = client.get("/apidocs", follow_redirects=True)
    assert resp.status_code == 200
