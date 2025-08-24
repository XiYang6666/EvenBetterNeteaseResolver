from fastapi.testclient import TestClient

from ebnr.app import app

client = TestClient(app)
