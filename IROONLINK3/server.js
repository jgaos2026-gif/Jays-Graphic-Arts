'use strict';

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data', 'nodes.json');
const MAX_NODE_FIELD_LENGTH = 120;
const NODE_ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$/;

app.disable('x-powered-by');
app.use(express.json({ limit: '16kb' }));
app.use(express.static(__dirname));
app.use('/api', (_req, res, next) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
});

// ── Helpers ──────────────────────────────────────────────────────────────────

function ensureDataDir() {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
}

function loadNodes() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveNodes(nodes) {
  ensureDataDir();
  const tempFile = `${DATA_FILE}.tmp`;
  fs.writeFileSync(tempFile, JSON.stringify(nodes, null, 2));
  fs.renameSync(tempFile, DATA_FILE);
}

function sanitizeNodeString(value) {
  if (typeof value !== 'string') return '';
  return value.trim().slice(0, MAX_NODE_FIELD_LENGTH);
}

function normalizePort(value) {
  if (value === undefined || value === null || value === '') return 4000;
  const port = Number.parseInt(value, 10);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('port must be an integer between 1 and 65535');
  }
  return port;
}

function parseNodePayload(body) {
  const id = sanitizeNodeString(body && body.id);
  const name = sanitizeNodeString(body && body.name);
  const host = sanitizeNodeString(body && body.host);
  const port = normalizePort(body && body.port);

  if (!id || !name || !host) {
    throw new Error('id, name, and host are required');
  }
  if (!NODE_ID_PATTERN.test(id)) {
    throw new Error('id must start with a letter or number and use only letters, numbers, dot, underscore, or dash');
  }
  if (/\s/.test(host)) {
    throw new Error('host must not contain spaces');
  }

  return { id, name, host, port };
}

// ── API routes ────────────────────────────────────────────────────────────────

// GET /api/status  — server heartbeat
app.get('/api/status', (_req, res) => {
  res.json({ status: 'online', timestamp: new Date().toISOString(), version: '1.0.0' });
});

// GET /api/nodes  — list all protection nodes
app.get('/api/nodes', (_req, res) => {
  res.json(loadNodes());
});

// GET /api/nodes/:id  — single node detail
app.get('/api/nodes/:id', (req, res) => {
  const node = loadNodes().find(n => n.id === req.params.id);
  if (!node) return res.status(404).json({ error: 'Node not found' });
  res.json(node);
});

// POST /api/nodes  — register a new protection node
app.post('/api/nodes', (req, res) => {
  let payload;
  try {
    payload = parseNodePayload(req.body);
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
  const nodes = loadNodes();
  if (nodes.find(n => n.id === payload.id)) {
    return res.status(409).json({ error: 'Node id already registered' });
  }
  const node = {
    ...payload,
    status: 'registered',
    registeredAt: new Date().toISOString(),
    lastSeen: null,
  };
  nodes.push(node);
  saveNodes(nodes);
  res.status(201).json(node);
});

// PATCH /api/nodes/:id/heartbeat  — protection node check-in
app.patch('/api/nodes/:id/heartbeat', (req, res) => {
  const nodes = loadNodes();
  const node = nodes.find(n => n.id === req.params.id);
  if (!node) return res.status(404).json({ error: 'Node not found' });
  node.status = 'online';
  node.lastSeen = new Date().toISOString();
  saveNodes(nodes);
  res.json(node);
});

// DELETE /api/nodes/:id  — deregister a node
app.delete('/api/nodes/:id', (req, res) => {
  const nodes = loadNodes();
  const idx = nodes.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Node not found' });
  const [removed] = nodes.splice(idx, 1);
  saveNodes(nodes);
  res.json(removed);
});

// ── Catch-all → serve index.html ─────────────────────────────────────────────
app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// ── Start ─────────────────────────────────────────────────────────────────────
function startServer(port = PORT) {
  return app.listen(port, () => {
    console.log(`IROONLINK3 Control Room listening on http://localhost:${port}`);
  });
}

if (require.main === module) {
  startServer();
}

app.use((err, _req, res, next) => {
  if (err instanceof SyntaxError && 'body' in err) {
    return res.status(400).json({ error: 'Malformed JSON body' });
  }
  return next(err);
});

module.exports = app;
module.exports.startServer = startServer;
