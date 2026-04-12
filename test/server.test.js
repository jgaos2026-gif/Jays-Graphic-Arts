const test = require("node:test");
const assert = require("node:assert/strict");

const { createServer } = require("../src/server");

function getBaseUrl(server) {
  const address = server.address();
  return `http://127.0.0.1:${address.port}`;
}

test("GET /health returns ok", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

  try {
    const response = await fetch(`${getBaseUrl(server)}/health`);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.equal(body.status, "ok");
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("POST /api/leads creates and lists lead", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

  try {
    const createResponse = await fetch(`${getBaseUrl(server)}/api/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Jane Smith",
        email: "jane@example.com",
        serviceRequest: "Logo package",
      }),
    });

    assert.equal(createResponse.status, 201);
    const created = await createResponse.json();
    assert.equal(created.name, "Jane Smith");

    const listResponse = await fetch(`${getBaseUrl(server)}/api/leads`);
    assert.equal(listResponse.status, 200);
    const list = await listResponse.json();
    assert.ok(list.count >= 1);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("POST /api/invoices validates payload", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

  try {
    const response = await fetch(`${getBaseUrl(server)}/api/invoices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ projectId: "1", amount: "100" }),
    });

    assert.equal(response.status, 400);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("POST /api/invoices rejects non-positive amounts", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

  try {
    const response = await fetch(`${getBaseUrl(server)}/api/invoices`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ projectId: "1", amount: 0 }),
    });

    assert.equal(response.status, 400);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test("POST endpoints reject payloads over 1MB", async () => {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

  try {
    const oversized = JSON.stringify({
      name: "Jane Smith",
      email: "jane@example.com",
      serviceRequest: "a".repeat(1_000_050),
    });
    const response = await fetch(`${getBaseUrl(server)}/api/leads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: oversized,
    });

    assert.equal(response.status, 413);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
