import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const SIGNATURE_TOLERANCE_SECONDS = 300;

function hex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes)).map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function parseSignature(header: string): { timestamp: number; signatures: string[] } | null {
  let timestamp = 0;
  const signatures: string[] = [];
  for (const part of header.split(",")) {
    const [key, value] = part.split("=", 2);
    if (key === "t") timestamp = Number(value);
    if (key === "v1" && value) signatures.push(value);
  }
  return timestamp > 0 && signatures.length ? { timestamp, signatures } : null;
}

async function sign(payload: string, secret: string, timestamp: number): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  return hex(await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(`${timestamp}.${payload}`),
  ));
}

function equal(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let index = 0; index < a.length; index++) result |= a.charCodeAt(index) ^ b.charCodeAt(index);
  return result === 0;
}

Deno.serve(async (request: Request) => {
  if (request.method !== "POST") return new Response("method_not_allowed", { status: 405 });
  const secret = Deno.env.get("STRIPE_WEBHOOK_SECRET");
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseSecret = Deno.env.get("SUPABASE_SECRET_KEY") ||
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!secret || !supabaseUrl || !supabaseSecret) {
    return new Response(JSON.stringify({ error: "webhook_not_configured" }), {
      status: 503, headers: { "Content-Type": "application/json" },
    });
  }

  const payload = await request.text();
  const signature = parseSignature(request.headers.get("stripe-signature") || "");
  if (!signature || Math.abs(Math.floor(Date.now() / 1000) - signature.timestamp) > SIGNATURE_TOLERANCE_SECONDS) {
    return new Response(JSON.stringify({ error: "invalid_signature" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }
  const expected = await sign(payload, secret, signature.timestamp);
  if (!signature.signatures.some((candidate) => equal(candidate, expected))) {
    return new Response(JSON.stringify({ error: "invalid_signature" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  let event: Record<string, any>;
  try {
    event = JSON.parse(payload);
  } catch {
    return new Response(JSON.stringify({ error: "malformed_event" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  if (event.type !== "checkout.session.completed" || event.data?.object?.payment_status !== "paid") {
    return new Response(JSON.stringify({ received: true, handled: false }), {
      status: 200, headers: { "Content-Type": "application/json" },
    });
  }

  const session = event.data.object;
  const orderId = session.metadata?.order_id || session.client_reference_id;
  const amountCents = Number(session.amount_total);
  const providerEventId = String(event.id || "");
  if (!orderId || !Number.isSafeInteger(amountCents) || amountCents <= 0 || !providerEventId) {
    return new Response(JSON.stringify({ error: "invalid_payment_event" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  const admin = createClient(supabaseUrl, supabaseSecret, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: existing } = await admin.schema("brick1").from("payment_events")
    .select("id").eq("provider", "stripe").eq("provider_event_id", providerEventId).maybeSingle();
  if (existing) {
    return new Response(JSON.stringify({ received: true, duplicate: true }), {
      status: 200, headers: { "Content-Type": "application/json" },
    });
  }

  const { error } = await admin.rpc("brick1_record_payment", {
    p_order_id: orderId,
    p_provider: "stripe",
    p_provider_event_id: providerEventId,
    p_amount_cents: amountCents,
    p_synthetic: false,
    p_actor: "STRIPE_WEBHOOK",
    p_correlation_id: crypto.randomUUID(),
  });
  if (error) {
    return new Response(JSON.stringify({ error: "payment_record_failed" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ received: true, handled: true }), {
    status: 200, headers: { "Content-Type": "application/json" },
  });
});
