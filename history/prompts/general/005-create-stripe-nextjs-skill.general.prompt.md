---
id: 005
title: Create Stripe Next.js Skill
stage: general
date: 2026-02-14
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["skill-creation","stripe","nextjs","payments","webhooks","subscriptions","typescript"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/stripe-nextjs/SKILL.md
  - .claude/skills/stripe-nextjs/references/checkout-sessions.md
  - .claude/skills/stripe-nextjs/references/webhooks.md
  - .claude/skills/stripe-nextjs/references/subscriptions.md
  - .claude/skills/stripe-nextjs/references/customer-portal.md
  - .claude/skills/stripe-nextjs/references/typescript-types.md
  - .claude/skills/stripe-nextjs/references/common-mistakes.md
tests:
  - none
---

## Prompt

Using your 'skill-creator-pro' skill create a new skill for Stripe payment integration in Next.js App Router with TypeScript. I will use it to build complete payment systems from simple one-time checkouts to complex subscription management with webhooks and customer portals. Use context7 skill to study official Stripe documentation for Next.js integration, checkout sessions, webhooks, subscriptions, customer portal, TypeScript types, webhook signature verification, and server actions with Stripe API, then build it so no self assumed knowledge.

## Response snapshot

Created the `stripe-nextjs` skill with full domain knowledge sourced from official Stripe documentation via Context7 (library ID: `/websites/stripe`, 49110 snippets) and Stripe docs WebFetch.

**Domain discovery sources:**
- Context7: Stripe checkout sessions, webhook signature verification, subscription/customer portal patterns
- WebFetch: `docs.stripe.com/checkout/embedded/quickstart` — embedded checkout flow
- WebFetch: `docs.stripe.com/billing/subscriptions/build-subscriptions` — subscription lifecycle

**Skill files created:**

1. **SKILL.md** — Mental model (one-time vs subscription flows), decision trees (checkout mode, hosted vs embedded, webhook events), file structure, environment variables, production checklist, reference index

2. **references/checkout-sessions.md** — Server-only Stripe client setup, hosted checkout (Server Action + session verification), embedded checkout (`EmbeddedCheckoutProvider` + `fetchClientSecret`), subscription checkout, full session configuration options

3. **references/webhooks.md** — Complete Route Handler with `runtime = "nodejs"` + `req.text()` for raw body, `constructEvent` signature verification, all subscription/payment event handlers, idempotency pattern (processedEvents table), Stripe CLI testing commands, required events table

4. **references/subscriptions.md** — Full subscription checkout with customer reuse, Prisma DB schema, webhook handlers for all subscription lifecycle events, status types table, plan upgrade/downgrade/cancel/reactivate patterns, free trial via checkout session

5. **references/customer-portal.md** — `createBillingPortalSession` Server Action, billing page with subscription display, Route Handler alternative, portal deep links (payment_method_update / subscription_cancel / subscription_update_confirm), webhook events from portal actions

6. **references/typescript-types.md** — All Stripe resource types, event type narrowing (`as Stripe.Checkout.Session`), `Stripe.Subscription.Status` union, expandable field helpers, `ActionResult<T>` for Server Actions, PLANS constant with `as const`

7. **references/common-mistakes.md** — 12 anti-patterns with before/after fixes (req.json vs req.text, secret key exposure, trusting success URL, no idempotency, non-200 on errors, Edge Runtime, missing metadata, duplicate customers), 12-symptom debugging table

**Key patterns encoded:**
- Webhooks are authoritative (never trust client-side success URL)
- Always use `req.text()` not `req.json()` for webhook raw body
- `export const runtime = "nodejs"` required (Edge Runtime incompatible)
- Reuse `stripeCustomerId` to prevent duplicate customers
- Always pass `metadata: { userId }` on checkout session + subscription_data
- Return 200 after valid signature even on business logic errors

## Outcome

- ✅ Impact: Production-ready Stripe payment skill covering one-time payments, subscriptions, webhooks, and customer portal — sourced entirely from official Stripe docs via Context7
- 🧪 Tests: none
- 📁 Files: 7 files created under `.claude/skills/stripe-nextjs/`
- 🔁 Next prompts: Use `/stripe-nextjs` when implementing checkout, subscriptions, or webhook handlers in Next.js projects
- 🧠 Reflection: Critical patterns like raw body requirement and Edge Runtime incompatibility are easy to miss — encoding them as anti-patterns in common-mistakes.md ensures they surface during implementation

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add one-time payment (non-subscription) webhook flow examples to checkout-sessions.md
