'use strict';

/**
 * register-node.js
 * CLI helper: register a protection node with the IROONLINK3 control room.
 *
 * Usage:
 *   node scripts/register-node.js <id> <name> <host> [port]
 *
 * Example:
 *   node scripts/register-node.js node-003 "Tertiary Guardian" 192.168.1.20 4003
 */

const http = require('http');

const [,, id, name, host, port] = process.argv;

if (!id || !name || !host) {
  console.error('Usage: node scripts/register-node.js <id> <name> <host> [port]');
  process.exit(1);
}

const body = JSON.stringify({ id, name, host, port: parseInt(port || '4000', 10) });
const options = {
  hostname: 'localhost',
  port: process.env.PORT || 3000,
  path: '/api/nodes',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  },
};

const req = http.request(options, res => {
  let data = '';
  res.on('data', chunk => { data += chunk; });
  res.on('end', () => {
    const parsed = JSON.parse(data);
    if (res.statusCode === 201) {
      console.log(`✓ Node registered: ${parsed.id} (${parsed.name}) @ ${parsed.host}:${parsed.port}`);
    } else {
      console.error(`✗ Error ${res.statusCode}: ${parsed.error || data}`);
      process.exit(1);
    }
  });
});

req.on('error', err => {
  console.error(`✗ Connection failed: ${err.message}`);
  console.error('  Is the IROONLINK3 Control Room running? Start it with: node server.js');
  process.exit(1);
});

req.write(body);
req.end();
