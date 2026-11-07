"""Run from api/:  pip install -r requirements.txt pytest httpx && python -m pytest"""
from fastapi.testclient import TestClient

from main import app


def test_status_and_notes_round_trip():
    with TestClient(app) as client:
        status = client.get('/').json()
        assert status['status'] == 'ok' and status['storage'] in ('memory', 'postgres')
        created = client.post('/api/notes', json={'text': '  hello from the test  '})
        assert created.status_code == 201 and created.json()['text'] == 'hello from the test'
        note_id = created.json()['id']
        assert client.get('/api/notes').json()[0]['id'] == note_id
        assert client.delete(f'/api/notes/{note_id}').status_code == 204
        assert client.delete(f'/api/notes/{note_id}').status_code == 404


def test_bad_notes_are_refused():
    with TestClient(app) as client:
        assert client.post('/api/notes', json={'text': ''}).status_code == 422
        assert client.post('/api/notes', json={'text': 'x' * 501}).status_code == 422


def test_healthz_has_only_liveness_status(monkeypatch):
    monkeypatch.setattr('main.DATABASE_URL', None)
    with TestClient(app) as client:
        response = client.get('/healthz')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}
