import os

from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite://"

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
