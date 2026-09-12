import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const DEFAULT_ORIGINS = [
  "https://jgaos2026-gif.github.io",
  "https://jays-graphic-arts.ai",
  "https://www.jays-graphic-arts.ai",
];

function origins(): string[] {
  const configured = (Deno.env.get("BRICK1_ALLOWED_ORIGINS") || "")
    .split(",").map((value) => value.trim()).filter(Boolean);
  return configured.length ? configured : DEFAULT_ORIGINS;
}

function headers(origin: string | null): Headers {
  const allowed = origin && origins().includes(origin) ? origin : "null";
  return new Headers({
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Headers": "content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
}

function json(body: Record<string, unknown>, status: number, origin: string | null) {
  return new Response(JSON.stringify(body), { status, headers: headers(origin) });
}

Deno.serve(async (request: Request) => {
  const origin = request.headers.get("origin");
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: headers(origin) });
  if (request.method !== "POST") return json({ error: "method_not_allowed" }, 405, origin);
  if (!origin || !origins().includes(origin)) return json({ error: "origin_not_allowed" }, 403, origin);
  if (!(request.headers.get("content-type") || "").toLowerCase().includes("application/json")) {
    return json({ error: "json_required" }, 415, origin);
  }

  let body: Record<string, unknown>;
  try {
    body = await request.json();
  } catch {
    return json({ error: "malformed_json" }, 400, origin);
  }

  const orderId = typeof body.orderId === "string" ? body.orderId.trim() : "";
  const paymentType = body.paymentType === "deposit" || body.paymentType === "balance"
    ? body.paymentType
    : "";
  if (!orderId || !paymentType) return json({ error: "invalid_checkout_request" }, 400, origin);

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseSecret = Deno.env.get("SUPABASE_SECRET_KEY") ||
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  const stripeSecret = Deno.env.get("STRIPE_SECRET_KEY");
  const successUrl = Deno.env.get("BRICK1_CHECKOUT_SUCCESS_URL");
  const cancelUrl = Deno.env.get("BRICK1_CHECKOUT_CANCEL_URL");
  if (!supabaseUrl || !supabaseSecret || !stripeSecret || !successUrl || !cancelUrl) {
    return json({ error: "checkout_not_configured" }, 503, origin);
  }

  const admin = createClient(supabaseUrl, supabaseSecret, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: order, error: orderError } = await admin
    .schema("brick1")
    .from("orders")
    .select("id,quote_total_cents,deposit_required_cents,paid_cents,state")
    .eq("id", orderId)
    .maybeSingle();

  if (orderError || !order) return json({ error: "order_not_found" }, 404, origin);

  let amountCents = 0;
  if (paymentType === "deposit") {
    if (order.state !== "DEPOSIT_REQUIRED" || !order.deposit_required_cents) {
      return json({ error: "deposit_not_due" }, 409, origin);
    }
    amountCents = Number(order.deposit_required_cents);
  } else {
    if (order.state !== "BALANCE_REQUIRED" || !order.quote_total_cents) {
      return json({ error: "balance_not_due" }, 409, origin);
    }
    amountCents = Number(order.quote_total_cents) - Number(order.paid_cents || 0);
  }
  if (!Number.isSafeInteger(amountCents) || amountCents <= 0) {
    return json({ error: "invalid_amount" }, 422, origin);
  }

  const form = new URLSearchParams();
  form.set("mode", "payment");
  form.set("success_url", successUrl);
  form.set("cancel_url", cancelUrl);
  form.set("client_reference_id", orderId);
  form.set("line_items[0][quantity]", "1");
  form.set("line_items[0][price_data][currency]", "usd");
  form.set("line_items[0][price_data][unit_amount]", String(amountCents));
  form.set("line_items[0][price_data][product_data][name]",
    paymentType === "deposit" ? "Jay's Graphic Arts — project deposit" : "Jay's Graphic Arts — project balance");
  form.set("metadata[order_id]", orderId);
  form.set("metadata[payment_type]", paymentType);
  form.set("metadata[amount_cents]", String(amountCents));
  form.set("payment_intent_data[metadata][order_id]", orderId);
  form.set("payment_intent_data[metadata][payment_type]", paymentType);

  const stripeResponse = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${stripeSecret}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
  });
  const stripePayload = await stripeResponse.json();
  if (!stripeResponse.ok || !stripePayload.url) {
    return json({ error: "stripe_session_failed" }, 502, origin);
  }

  return json({
    accepted: true,
    orderId,
    paymentType,
    amountCents,
    checkoutUrl: stripePayload.url,
    sessionId: stripePayload.id,
  }, 201, origin);
});
