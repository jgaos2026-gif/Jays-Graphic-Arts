const http = require("node:http");
const { URL } = require("node:url");

const database = {
  leads: [],
  projects: [],
  invoices: [],
};

const idCounters = {
  leads: 1,
  projects: 1,
  invoices: 1,
};

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
  });
  res.end(body);
}

function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    let tooLarge = false;

    req.on("data", (chunk) => {
      if (tooLarge) {
        return;
      }
      if (body.length + chunk.length > 1_000_000) {
        tooLarge = true;
        reject(new Error("Payload too large"));
        return;
      }
      body += chunk;
    });

    req.on("end", () => {
      if (!body) {
        resolve({});
        return;
      }

      try {
        resolve(JSON.parse(body));
      } catch (error) {
        reject(new Error("Invalid JSON payload"));
      }
    });

    req.on("error", reject);
  });
}

function validateField(input, fieldName) {
  const value = input[fieldName];
  return typeof value === "string" && value.trim().length > 0;
}

function createResource(type, payload) {
  const item = {
    id: idCounters[type]++,
    createdAt: new Date().toISOString(),
    ...payload,
  };
  database[type].push(item);
  return item;
}

async function requestHandler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const { method } = req;
  const { pathname } = url;

  if (method === "GET" && pathname === "/") {
    sendJson(res, 200, {
      service: "Jays-Graphic-Arts Core Backend",
      status: "running",
      endpoints: [
        "GET /health",
        "GET /api",
        "GET /api/leads",
        "POST /api/leads",
        "GET /api/projects",
        "POST /api/projects",
        "GET /api/invoices",
        "POST /api/invoices",
      ],
    });
    return;
  }

  if (method === "GET" && pathname === "/health") {
    sendJson(res, 200, { status: "ok", timestamp: new Date().toISOString() });
    return;
  }

  if (method === "GET" && pathname === "/api") {
    sendJson(res, 200, {
      version: "1.0.0",
      resources: {
        leads: "/api/leads",
        projects: "/api/projects",
        invoices: "/api/invoices",
      },
    });
    return;
  }

  if (method === "GET" && pathname === "/api/leads") {
    sendJson(res, 200, { count: database.leads.length, leads: database.leads });
    return;
  }

  if (method === "POST" && pathname === "/api/leads") {
    try {
      const body = await parseBody(req);
      if (!validateField(body, "name") || !validateField(body, "email")) {
        sendJson(res, 400, { error: "name and email are required" });
        return;
      }

      const lead = createResource("leads", {
        name: body.name.trim(),
        email: body.email.trim(),
        serviceRequest: typeof body.serviceRequest === "string" ? body.serviceRequest.trim() : "",
      });

      sendJson(res, 201, lead);
      return;
    } catch (error) {
      if (error.message === "Payload too large") {
        sendJson(res, 413, { error: error.message });
        return;
      }
      sendJson(res, 400, { error: error.message });
      return;
    }
  }

  if (method === "GET" && pathname === "/api/projects") {
    sendJson(res, 200, { count: database.projects.length, projects: database.projects });
    return;
  }

  if (method === "POST" && pathname === "/api/projects") {
    try {
      const body = await parseBody(req);
      if (!validateField(body, "clientName") || !validateField(body, "title")) {
        sendJson(res, 400, { error: "clientName and title are required" });
        return;
      }

      const project = createResource("projects", {
        clientName: body.clientName.trim(),
        title: body.title.trim(),
        status: validateField(body, "status") ? body.status.trim() : "pending",
      });

      sendJson(res, 201, project);
      return;
    } catch (error) {
      if (error.message === "Payload too large") {
        sendJson(res, 413, { error: error.message });
        return;
      }
      sendJson(res, 400, { error: error.message });
      return;
    }
  }

  if (method === "GET" && pathname === "/api/invoices") {
    sendJson(res, 200, { count: database.invoices.length, invoices: database.invoices });
    return;
  }

  if (method === "POST" && pathname === "/api/invoices") {
    try {
      const body = await parseBody(req);
      if (
        !validateField(body, "projectId") ||
        typeof body.amount !== "number" ||
        !Number.isFinite(body.amount) ||
        body.amount <= 0
      ) {
        sendJson(res, 400, { error: "projectId is required and amount must be a positive JSON number" });
        return;
      }

      const invoice = createResource("invoices", {
        projectId: body.projectId.trim(),
        amount: body.amount,
        currency: validateField(body, "currency") ? body.currency.trim().toUpperCase() : "USD",
        paid: Boolean(body.paid),
      });

      sendJson(res, 201, invoice);
      return;
    } catch (error) {
      if (error.message === "Payload too large") {
        sendJson(res, 413, { error: error.message });
        return;
      }
      sendJson(res, 400, { error: error.message });
      return;
    }
  }

  sendJson(res, 404, { error: "Route not found" });
}

function createServer() {
  return http.createServer((req, res) => {
    requestHandler(req, res).catch((error) => {
      console.error("Request handler error:", error);
      sendJson(res, 500, { error: "Internal server error" });
    });
  });
}

function startServer() {
  const port = Number(process.env.PORT) || 3000;
  const host = process.env.HOST || "0.0.0.0";
  const server = createServer();
  server.listen(port, host, () => {
    console.log(`Server running at http://${host}:${port}`);
  });
  return server;
}

if (require.main === module) {
  startServer();
}

module.exports = {
  createServer,
  startServer,
};
