import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const MAX_BODY = 16 * 1024;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const DEFAULT_ORIGINS = [
  'https://jgaos2026-gif.github.io',
  'https://jays-graphic-arts.ai',
  'https://www.jays-graphic-arts.ai',
];
const allowedServices = new Set(['logo','brand-system','rebrand','collateral','marketing-print','packaging','social','banners','email-templates','logo-animation','social-motion','infographic-motion','blog','ad-copy','email-campaigns','enterprise','other']);

function configuredOrigins() {
  const custom = (Deno.env.get('BRICK1_ALLOWED_ORIGINS') || '').split(',').map(v => v.trim()).filter(Boolean);
  return custom.length ? custom : DEFAULT_ORIGINS;
}

function cors(origin: string | null) {
  const configured = configuredOrigins();
  const allow = origin && configured.includes(origin) ? origin : 'null';
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Headers': 'content-type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Vary': 'Origin',
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
  };
}

function text(v: unknown, max: number) {
  if (typeof v !== 'string') return '';
  return v.trim().slice(0, max);
}

Deno.serve(async (req: Request) => {
  const origin = req.headers.get('origin');
  const headers = cors(origin);
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers });
  if (req.method !== 'POST') return new Response(JSON.stringify({ error: 'method_not_allowed' }), { status: 405, headers });
  if (!origin || headers['Access-Control-Allow-Origin'] !== origin) return new Response(JSON.stringify({ error: 'origin_not_allowed' }), { status: 403, headers });
  const len = Number(req.headers.get('content-length') || '0');
  if (len > MAX_BODY) return new Response(JSON.stringify({ error: 'payload_too_large' }), { status: 413, headers });
  if (!(req.headers.get('content-type') || '').toLowerCase().includes('application/json')) return new Response(JSON.stringify({ error: 'json_required' }), { status: 415, headers });

  let raw = '';
  try { raw = await req.text(); } catch { return new Response(JSON.stringify({ error: 'invalid_body' }), { status: 400, headers }); }
  if (new TextEncoder().encode(raw).byteLength > MAX_BODY) return new Response(JSON.stringify({ error: 'payload_too_large' }), { status: 413, headers });

  let body: Record<string, unknown>;
  try { body = JSON.parse(raw); } catch { return new Response(JSON.stringify({ error: 'malformed_json' }), { status: 400, headers }); }
  if (text(body.website, 200)) return new Response(JSON.stringify({ accepted: true }), { status: 202, headers });

  const firstName = text(body.firstName, 120);
  const lastName = text(body.lastName, 120);
  const email = text(body.email, 320).toLowerCase();
  const company = text(body.company, 200) || null;
  const service = text(body.service, 120);
  const budget = text(body.budget, 120);
  const timeline = text(body.timeline, 120);
  const brief = text(body.brief, 12000);
  const referral = text(body.referral, 120) || null;

  if (!firstName || !lastName || !EMAIL_RE.test(email) || !allowedServices.has(service) || !budget || !timeline || !brief) {
    return new Response(JSON.stringify({ error: 'invalid_inquiry' }), { status: 400, headers });
  }

  const url = Deno.env.get('SUPABASE_URL');
  const secret = Deno.env.get('SUPABASE_SECRET_KEY') || Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!url || !secret) return new Response(JSON.stringify({ error: 'backend_unavailable' }), { status: 503, headers });
  const admin = createClient(url, secret, { auth: { persistSession: false, autoRefreshToken: false } });

  const ip = (req.headers.get('x-forwarded-for') || req.headers.get('cf-connecting-ip') || 'unknown').split(',')[0].trim();
  const salt = Deno.env.get('BRICK1_RATE_SALT') || secret;
  const ipHash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${salt}:${ip}`));
  const ipHex = Array.from(new Uint8Array(ipHash)).map(b => b.toString(16).padStart(2, '0')).join('');
  const { data: allowed, error: rateError } = await admin.rpc('brick1_public_intake_allowed', { p_ip_hash: ipHex });
  if (rateError) return new Response(JSON.stringify({ error: 'rate_gate_unavailable' }), { status: 503, headers });
  if (!allowed) return new Response(JSON.stringify({ error: 'rate_limited' }), { status: 429, headers });

  const correlationId = crypto.randomUUID();
  const { data: inquiry, error: iErr } = await admin.rpc('brick1_create_inquiry', {
    p_email: email,
    p_first_name: firstName,
    p_last_name: lastName,
    p_company: company,
    p_service: service,
    p_budget: budget,
    p_timeline: timeline,
    p_brief: brief,
    p_referral: referral,
    p_correlation_id: correlationId,
  });
  if (iErr || !inquiry) return new Response(JSON.stringify({ error: 'inquiry_write_failed' }), { status: 503, headers });

  return new Response(JSON.stringify({ accepted: true, orderId: inquiry.order_id, state: inquiry.state, correlationId }), { status: 201, headers });
});
