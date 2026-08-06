'use strict';

const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data', 'nodes.json');

app.use(express.json());
app.use(express.static(__dirname));

// ── Helpers ──────────────────────────────────────────────────────────────────

function loadNodes() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveNodes(nodes) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(nodes, null, 2));
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
  const { id, name, host, port } = req.body;
  if (!id || !name || !host) {
    return res.status(400).json({ error: 'id, name, and host are required' });
  }
  const nodes = loadNodes();
  if (nodes.find(n => n.id === id)) {
    return res.status(409).json({ error: 'Node id already registered' });
  }
  const node = {
    id,
    name,
    host,
    port: port || 4000,
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
app.listen(PORT, () => {
  console.log(`IROONLINK3 Control Room listening on http://localhost:${PORT}`);
});

module.exports = app;
