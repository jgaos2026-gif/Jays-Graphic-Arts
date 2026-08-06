'use strict';

/**
 * server.test.js
 * Basic API tests for the IROONLINK3 Control Room server.
 * Run with: node --test tests/server.test.js
 * (Requires Node.js >= 18 for the built-in test runner.)
 */

const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('http');

// Start the server on a random port for testing
process.env.PORT = '0';
const app = require('../server');

let server;
let baseUrl;

// Helper: make an HTTP request and return { status, body }
function request(method, path, payload) {
  return new Promise((resolve, reject) => {
    const body = payload ? JSON.stringify(payload) : undefined;
    const opts = {
      hostname: 'localhost',
      port: new URL(baseUrl).port,
      path,
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(body ? { 'Content-Length': Buffer.byteLength(body) } : {}),
      },
    };
    const req = http.request(opts, res => {
      let data = '';
      res.on('data', c => { data += c; });
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

test.before(() => new Promise(resolve => {
  server = app.listen(0, () => {
    baseUrl = `http://localhost:${server.address().port}`;
    resolve();
  });
}));

test.after(() => new Promise(resolve => {
  if (server.closeAllConnections) server.closeAllConnections();
  server.close();
  setTimeout(() => { resolve(); process.exit(0); }, 200);
}));

test('GET /api/status returns online', async () => {
  const { status, body } = await request('GET', '/api/status');
  assert.equal(status, 200);
  assert.equal(body.status, 'online');
  assert.ok(body.timestamp);
});

test('GET /api/nodes returns an array', async () => {
  const { status, body } = await request('GET', '/api/nodes');
  assert.equal(status, 200);
  assert.ok(Array.isArray(body));
});

test('POST /api/nodes registers a new node', async () => {
  const payload = { id: 'test-node', name: 'Test Node', host: '127.0.0.1', port: 9999 };
  const { status, body } = await request('POST', '/api/nodes', payload);
  assert.equal(status, 201);
  assert.equal(body.id, 'test-node');
  assert.equal(body.status, 'registered');
});

test('POST /api/nodes returns 409 for duplicate id', async () => {
  const payload = { id: 'test-node', name: 'Duplicate', host: '127.0.0.1' };
  const { status, body } = await request('POST', '/api/nodes', payload);
  assert.equal(status, 409);
  assert.ok(body.error);
});

test('POST /api/nodes returns 400 when required fields missing', async () => {
  const { status, body } = await request('POST', '/api/nodes', { id: 'x' });
  assert.equal(status, 400);
  assert.ok(body.error);
});

test('GET /api/nodes/:id returns the node', async () => {
  const { status, body } = await request('GET', '/api/nodes/test-node');
  assert.equal(status, 200);
  assert.equal(body.id, 'test-node');
});

test('GET /api/nodes/:id returns 404 for unknown id', async () => {
  const { status } = await request('GET', '/api/nodes/does-not-exist');
  assert.equal(status, 404);
});

test('PATCH /api/nodes/:id/heartbeat updates lastSeen', async () => {
  const { status, body } = await request('PATCH', '/api/nodes/test-node/heartbeat');
  assert.equal(status, 200);
  assert.equal(body.status, 'online');
  assert.ok(body.lastSeen);
});

test('DELETE /api/nodes/:id removes the node', async () => {
  const { status, body } = await request('DELETE', '/api/nodes/test-node');
  assert.equal(status, 200);
  assert.equal(body.id, 'test-node');
  const { status: s2 } = await request('GET', '/api/nodes/test-node');
  assert.equal(s2, 404);
});
