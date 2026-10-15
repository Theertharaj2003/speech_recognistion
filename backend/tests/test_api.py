import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health(client):
    r=client.get('/api/health')
    assert r.status_code == 200 and r.json()['status'] == 'ok'

def test_seeded_subjects(client):
    r=client.get('/api/subjects')
    assert r.status_code == 200 and len(r.json()) >= 3

def test_questions_and_recommendation(client):
    s=client.get('/api/subjects').json()[0]
    assert client.get(f"/api/subjects/{s['id']}/questions").json()
    assert client.get(f"/api/recommendations/{s['id']}").json()['action'] in {'review','easier','same','harder'}
