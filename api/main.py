"""Notes API: a small FastAPI service used to test Cloudhop deploys and cloud switches.

Stores notes in Postgres when DATABASE_URL is set (Cloudhop's Compose file sets it), otherwise in memory
for quick local runs. GET / answers health checks, so a deploy can confirm the app is up.
"""
import os
import socket
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from itertools import count

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATABASE_URL = os.environ.get('DATABASE_URL')
STARTED = datetime.now(UTC)


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class MemoryStore:
    """Used when there is no database: notes vanish on restart."""

    kind = 'memory'

    def __init__(self):
        self.notes = []
        self.ids = count(1)

    def list(self):
        return list(reversed(self.notes))

    def add(self, text):
        note = {'id': next(self.ids), 'text': text, 'created_at': datetime.now(UTC).isoformat()}
        self.notes.append(note)
        return note

    def delete(self, note_id):
        before = len(self.notes)
        self.notes = [note for note in self.notes if note['id'] != note_id]
        return len(self.notes) < before


class PostgresStore:
    """Notes survive restarts, and move with the database when Cloudhop switches clouds."""

    kind = 'postgres'

    def __init__(self, url):
        import psycopg  # Imported here so memory mode needs no database driver.
        from psycopg.rows import dict_row
        self.connect = lambda: psycopg.connect(url, row_factory=dict_row, autocommit=True)
        # Compose starts the API and Postgres together, so the database may need a few seconds.
        for attempt in range(30):
            try:
                with self.connect() as conn:
                    conn.execute('CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, text TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())')
                return
            except psycopg.OperationalError:
                if attempt == 29:
                    raise
                time.sleep(1)

    def list(self):
        with self.connect() as conn:
            rows = conn.execute('SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 200').fetchall()
        return [{**row, 'created_at': row['created_at'].isoformat()} for row in rows]

    def add(self, text):
        with self.connect() as conn:
            row = conn.execute('INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at', (text,)).fetchone()
        return {**row, 'created_at': row['created_at'].isoformat()}

    def delete(self, note_id):
        with self.connect() as conn:
            return conn.execute('DELETE FROM notes WHERE id = %s', (note_id,)).rowcount > 0


store = None


@asynccontextmanager
async def lifespan(_app):
    global store
    store = PostgresStore(DATABASE_URL) if DATABASE_URL else MemoryStore()
    yield


app = FastAPI(title='Notes API', lifespan=lifespan)
# The frontend runs on another port (or host), so it needs CORS. Set ALLOWED_ORIGINS to lock it down.
app.add_middleware(CORSMiddleware, allow_origins=os.environ.get('ALLOWED_ORIGINS', '*').split(','), allow_methods=['GET', 'POST', 'DELETE'], allow_headers=['Content-Type'])


@app.get('/')
def status():
    """Health check and a quick view of where the app is running."""
    return {
        'service': 'notes-api',
        'status': 'ok',
        'storage': store.kind,
        'host': socket.gethostname(),
        'cloud': os.environ.get('CLOUD_NAME', 'unknown'),
        'release': os.environ.get('RELEASE', 'local'),
        'started_at': STARTED.isoformat(),
    }


@app.get('/api/notes')
def list_notes():
    return store.list()


@app.post('/api/notes', status_code=201)
def add_note(note: NoteIn):
    return store.add(note.text.strip())


@app.delete('/api/notes/{note_id}', status_code=204)
def delete_note(note_id: int):
    if not store.delete(note_id):
        raise HTTPException(404, 'Note not found')


@app.get('/healthz')
def healthz():
    """Minimal liveness response without host or deployment metadata."""
    return {'status': 'ok'}
