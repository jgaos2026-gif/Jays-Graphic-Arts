# Brick 1 Stripe setup

This integration keeps Stripe credentials and payment authority server-side.

## Functions

- `brick1-checkout` accepts only an order reference and payment type.
- It reads the amount from the protected `brick1.orders` record.
- It creates a hosted Stripe Checkout Session.
- `stripe-webhook` verifies the Stripe signature and records only paid sessions.
- Duplicate Stripe event IDs are ignored safely.

## Required Supabase secrets

Set these in the Supabase project that hosts the Brick 1 schema:

```text
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
BRICK1_CHECKOUT_SUCCESS_URL=https://jgaos2026-gif.github.io/Jays-Graphic-Arts/pay.html?status=success
BRICK1_CHECKOUT_CANCEL_URL=https://jgaos2026-gif.github.io/Jays-Graphic-Arts/pay.html?status=cancelled
BRICK1_ALLOWED_ORIGINS=https://jgaos2026-gif.github.io,https://jays-graphic-arts.ai,https://www.jays-graphic-arts.ai
```

Use the Supabase project URL and service secret already required by the intake function. Never commit any secret or use a client-side Stripe secret.

## Deployment sequence

1. Apply the Brick 1 migrations to the intended Supabase project.
2. Deploy `brick1-intake`, `brick1-checkout`, and `stripe-webhook`.
3. Set the secrets above.
4. In Stripe Workbench, create a webhook endpoint for:
   `https://<project-ref>.supabase.co/functions/v1/stripe-webhook`
5. Subscribe it to `checkout.session.completed`.
6. Run Stripe test-mode first with a test key and test webhook secret.
7. Create a synthetic order, generate a deposit Checkout Session, complete it with Stripe test card `4242 4242 4242 4242`, and confirm:
   - Stripe marks the session paid.
   - the webhook returns HTTP 200;
   - the Brick 1 order records the payment once;
   - the order moves to `DEPOSIT_CONFIRMED`.
8. Repeat with a balance payment and verify the final payment gate.

## Not yet proven by this source change

- Supabase connectivity or migration success.
- Stripe account configuration, price/tax settings, or business verification.
- A production payment.
- End-to-end deployment of the functions.
