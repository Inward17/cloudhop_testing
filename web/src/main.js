// Where the API lives. Set VITE_API_URL at build time to override.
// Default: locally (Vite on 5173) the API is on port 8000; when Cloudhop deploys both to one server,
// the API gets the main address (port 80) and this site another port, so use the same host, port 80.
const API = import.meta.env.VITE_API_URL
  ?? `${location.protocol}//${location.hostname}${location.port === '5173' ? ':8000' : ''}`;

const $ = (id) => document.getElementById(id);

async function call(path, options = {}) {
  const response = await fetch(API + path, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`${response.status} ${(await response.json().catch(() => ({}))).detail ?? response.statusText}`);
  return response.status === 204 ? null : response.json();
}

function showError(error) {
  $('error').textContent = error ? `Could not reach the API at ${API}: ${error.message}` : '';
  $('error').hidden = !error;
}

function render(notes) {
  $('notes').replaceChildren(...notes.map((note) => {
    const item = document.createElement('li');
    const body = document.createElement('div');
    const text = document.createElement('span');
    text.textContent = note.text; // textContent, never innerHTML: notes are user input.
    const when = document.createElement('time');
    when.textContent = new Date(note.created_at).toLocaleString();
    when.className = 'muted';
    body.append(text, when);
    const remove = document.createElement('button');
    remove.textContent = 'Delete';
    remove.className = 'ghost';
    remove.onclick = async () => { await call(`/api/notes/${note.id}`, { method: 'DELETE' }).catch(showError); load(); };
    item.append(body, remove);
    return item;
  }));
  if (!notes.length) {
    const empty = document.createElement('li');
    empty.className = 'muted';
    empty.textContent = 'No notes yet.';
    $('notes').replaceChildren(empty);
  }
}

async function load() {
  try {
    const [status, notes] = await Promise.all([call('/'), call('/api/notes')]);
    $('status').textContent = `API ok on ${status.cloud === 'unknown' ? status.host : status.cloud}, notes stored in ${status.storage}.`;
    render(notes);
    showError(null);
  } catch (error) {
    $('status').textContent = 'API not reachable.';
    showError(error);
  }
}

$('add').onsubmit = async (event) => {
  event.preventDefault();
  const text = $('text').value.trim();
  if (!text) return;
  try {
    await call('/api/notes', { method: 'POST', body: JSON.stringify({ text }) });
    $('text').value = '';
    load();
  } catch (error) {
    showError(error);
  }
};

load();
