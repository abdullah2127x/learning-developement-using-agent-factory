---
name: stripe-nextjs
description: |
  Comprehensive guide for building payment systems with Stripe in Next.js App Router
  with TypeScript. This skill should be used when users need to implement one-time
  checkout sessions, subscription billing, webhook event handling, customer portals,
  server actions for payments, webhook signature verification, or production-ready
  payment flows from basic checkout to complex subscription management.
---

# Stripe + Next.js App Router + TypeScript

## Mental Model

```
One-Time Payment:
  Server Action → Checkout Session → Stripe Hosted/Embedded → Return URL → Verify Session

Subscription:
  Server Action → Checkout Session (mode: "subscription") → Stripe
       ↓
  Webhooks → constructEvent (signature verify) → DB provisioning
       ↓
  Customer Portal → Manage billing
```

**Key principle**: Stripe tells YOU when things happen via webhooks. Never trust client-side redirects alone — always use webhooks to provision/revoke access.

## Quick Start (4 Steps)

### 1. Install

```bash
npm install stripe @stripe/stripe-js @stripe/react-stripe-js
```

### 2. Environment Variables

```env
STRIPE_SECRET_KEY="sk_test_..."
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
```

### 3. Stripe client (lib/stripe.ts)

```typescript
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-01-27.acacia",  // Pin API version
  typescript: true,
});
```

### 4. Create Checkout Session (Server Action)

```typescript
"use server";
import { stripe } from "@/lib/stripe";
import { redirect } from "next/navigation";

export async function createCheckoutSession(priceId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/cancel`,
  });
  redirect(session.url!);
}
```

## Decision Trees

### Which checkout mode?

```
Selling a single product once? → mode: "payment"
  └─ Recurring billing? → mode: "subscription"
        └─ Setting up card for later? → mode: "setup"
```

### Hosted vs Embedded Checkout?

```
Want Stripe-hosted page (simplest)? → success_url + cancel_url
  └─ Want checkout embedded in your page? → ui_mode: "embedded" + return_url + fetchClientSecret
        └─ Need full UI control? → Stripe Elements (advanced)
```

### Webhook Events to Handle

```
Subscriptions:
  checkout.session.completed    → Create DB record, provision access
  invoice.paid                  → Renew access each billing cycle
  invoice.payment_failed        → Notify customer, revoke if past_due
  customer.subscription.updated → Sync plan changes
  customer.subscription.deleted → Revoke access

One-time payments:
  checkout.session.completed    → Fulfill order
  payment_intent.succeeded      → Alternative fulfillment trigger
  payment_intent.payment_failed → Handle failure
```

## File Structure

```
lib/
  stripe.ts                    # Stripe client (server-only)
  stripe-client.ts             # loadStripe (client-only)
app/
  actions/
    checkout.ts                # Server Actions (createCheckoutSession, etc.)
    billing.ts                 # createPortalSession
  api/
    webhooks/
      route.ts                 # POST handler (raw body, signature verify)
  checkout/
    page.tsx                   # Server Component (create session)
  return/
    page.tsx                   # Post-payment success (verify session)
  billing/
    page.tsx                   # Customer portal redirect
components/
  EmbeddedCheckout.tsx         # 'use client' — @stripe/react-stripe-js
  PricingCard.tsx              # Calls server action
```

## Environment Variables

```env
# Keys from dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY="sk_test_..."                # Server only (NO NEXT_PUBLIC)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_test_..." # Client safe

# From dashboard.stripe.com/webhooks
STRIPE_WEBHOOK_SECRET="whsec_..."              # Server only

# Your domain
NEXT_PUBLIC_URL="http://localhost:3000"        # Or your production URL
```

**Critical**: `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` must NEVER have `NEXT_PUBLIC_` prefix.

## Production Checklist

- [ ] Switch from `sk_test_` to `sk_live_` keys in production
- [ ] Switch from `pk_test_` to `pk_live_` publishable key
- [ ] API version pinned with `apiVersion` in Stripe constructor
- [ ] Webhook handler uses raw body (not parsed JSON)
- [ ] Webhook signature verified with `constructEvent` on every request
- [ ] Webhook handler is idempotent (handles duplicate events)
- [ ] Subscription DB record updated on `checkout.session.completed`
- [ ] Access revoked on `customer.subscription.deleted`
- [ ] `invoice.paid` renews access on each billing cycle
- [ ] Customer portal enabled in Stripe Dashboard (Configuration)
- [ ] Webhook endpoint registered in Stripe Dashboard
- [ ] Error handling returns `400` for invalid signatures, `200` for all others
- [ ] `STRIPE_SECRET_KEY` never exposed to client

## Reference Files

| File | Content | Search Pattern |
|------|---------|----------------|
| `references/checkout-sessions.md` | Hosted, embedded, one-time, subscription checkout | `grep -i "checkout\|session\|ui_mode\|fetchClientSecret"` |
| `references/webhooks.md` | Route handler, constructEvent, event types, idempotency | `grep -i "webhook\|constructEvent\|signature\|stripe-signature"` |
| `references/subscriptions.md` | Subscription lifecycle, provisioning, plan upgrades, trials | `grep -i "subscription\|invoice\|provision\|cancel\|trial"` |
| `references/customer-portal.md` | Billing portal session, manage subscriptions, deep links | `grep -i "portal\|billing\|portalSession\|manage"` |
| `references/typescript-types.md` | Stripe TypeScript types, event narrowing, helper types | `grep -i "Stripe.Event\|Stripe.Checkout\|as Stripe\."` |
| `references/common-mistakes.md` | Anti-patterns, raw body, test clock, debugging | `grep -i "mistake\|wrong\|rawBody\|error\|debug"` |
