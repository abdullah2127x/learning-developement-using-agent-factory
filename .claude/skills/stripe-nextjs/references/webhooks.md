# Webhooks

## Critical Rules

1. **Always verify signatures** — prevents fake events
2. **Use raw body** — parsed JSON breaks signature verification
3. **Idempotent handlers** — Stripe may send the same event twice
4. **Return 200 quickly** — process heavy work asynchronously
5. **Respond 400 only for invalid signatures** — return 200 for all other errors

## Next.js Route Handler

```typescript
// app/api/webhooks/route.ts
import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { stripe } from "@/lib/stripe";
import { headers } from "next/headers";

// CRITICAL: Disable body parsing — Stripe needs the raw body
export const runtime = "nodejs";  // Edge Runtime cannot use stripe.webhooks.constructEvent

export async function POST(req: NextRequest) {
  const body = await req.text();  // Raw text — NOT req.json()!
  const signature = (await headers()).get("stripe-signature");

  if (!signature) {
    return NextResponse.json({ error: "Missing signature" }, { status: 400 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return NextResponse.json(
      { error: "Invalid signature" },
      { status: 400 }
    );
  }

  // Handle events
  try {
    await handleStripeEvent(event);
  } catch (err) {
    // Log error but return 200 — Stripe retries on non-200
    console.error(`Error handling event ${event.type}:`, err);
  }

  return NextResponse.json({ received: true });
}
```

## Event Handler

```typescript
async function handleStripeEvent(event: Stripe.Event) {
  switch (event.type) {
    // ---- One-Time Payments ----
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      if (session.mode === "payment") {
        await fulfillOrder(session);
      } else if (session.mode === "subscription") {
        await createSubscriptionRecord(session);
      }
      break;
    }

    case "payment_intent.succeeded": {
      const paymentIntent = event.data.object as Stripe.PaymentIntent;
      console.log("Payment succeeded:", paymentIntent.id);
      break;
    }

    case "payment_intent.payment_failed": {
      const paymentIntent = event.data.object as Stripe.PaymentIntent;
      console.error("Payment failed:", paymentIntent.last_payment_error?.message);
      break;
    }

    // ---- Subscription Events ----
    case "invoice.paid": {
      const invoice = event.data.object as Stripe.Invoice;
      await handleInvoicePaid(invoice);
      break;
    }

    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      await handleInvoicePaymentFailed(invoice);
      break;
    }

    case "customer.subscription.created": {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionCreated(subscription);
      break;
    }

    case "customer.subscription.updated": {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionUpdated(subscription);
      break;
    }

    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      await handleSubscriptionDeleted(subscription);
      break;
    }

    // ---- Customer Events ----
    case "customer.updated": {
      const customer = event.data.object as Stripe.Customer;
      // Sync customer data to your DB
      break;
    }

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }
}
```

## Subscription Event Handlers

```typescript
async function createSubscriptionRecord(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.userId;
  if (!userId) throw new Error("No userId in session metadata");

  // Save to database
  await db.subscriptions.upsert({
    where: { userId },
    create: {
      userId,
      stripeCustomerId: session.customer as string,
      stripeSubscriptionId: session.subscription as string,
      status: "active",
    },
    update: {
      stripeCustomerId: session.customer as string,
      stripeSubscriptionId: session.subscription as string,
      status: "active",
    },
  });
}

async function handleInvoicePaid(invoice: Stripe.Invoice) {
  const customerId = invoice.customer as string;
  const subscriptionId = invoice.subscription as string;

  // Renew access for each billing cycle
  await db.subscriptions.updateMany({
    where: { stripeCustomerId: customerId },
    data: {
      status: "active",
      currentPeriodEnd: new Date(invoice.period_end * 1000),
    },
  });
}

async function handleInvoicePaymentFailed(invoice: Stripe.Invoice) {
  const customerId = invoice.customer as string;

  // Notify user
  await sendPaymentFailureEmail(customerId);

  // Check subscription status
  if (invoice.subscription) {
    const subscription = await stripe.subscriptions.retrieve(
      invoice.subscription as string
    );
    if (subscription.status === "past_due") {
      await db.subscriptions.updateMany({
        where: { stripeCustomerId: customerId },
        data: { status: "past_due" },
      });
    }
  }
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  await db.subscriptions.updateMany({
    where: { stripeSubscriptionId: subscription.id },
    data: {
      status: subscription.status,
      priceId: subscription.items.data[0]?.price.id,
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    },
  });
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  await db.subscriptions.updateMany({
    where: { stripeSubscriptionId: subscription.id },
    data: { status: "canceled" },
  });
  // Revoke feature access
  const customerId = subscription.customer as string;
  await revokeUserAccess(customerId);
}
```

## Idempotency

Stripe may send the same event multiple times. Make handlers idempotent:

```typescript
async function handleInvoicePaid(invoice: Stripe.Invoice) {
  // Check if already processed
  const existing = await db.processedEvents.findUnique({
    where: { eventId: invoice.id },
  });
  if (existing) return;  // Already handled

  // ... handle event

  // Mark as processed
  await db.processedEvents.create({
    data: { eventId: invoice.id, processedAt: new Date() },
  });
}
```

## Local Testing with Stripe CLI

```bash
# Install Stripe CLI
# https://docs.stripe.com/stripe-cli

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/api/webhooks

# Outputs your local webhook secret:
# > Ready! Your webhook signing secret is whsec_xxxx

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger invoice.paid
stripe trigger customer.subscription.deleted
```

## Required Webhook Events (Minimal)

Register these events in Stripe Dashboard → Webhooks:

| Event | When | Required? |
|-------|------|-----------|
| `checkout.session.completed` | Customer completes checkout | Yes — provision access |
| `invoice.paid` | Subscription renewal succeeds | Yes — maintain access |
| `invoice.payment_failed` | Payment declines | Yes — notify user |
| `customer.subscription.updated` | Plan changes, trial ends | Yes — sync status |
| `customer.subscription.deleted` | Subscription canceled | Yes — revoke access |
| `payment_intent.succeeded` | One-time payment confirmed | Optional |
| `payment_intent.payment_failed` | One-time payment failed | Optional |

## Webhook Security

```typescript
// In your webhook handler:
// 1. Always use constructEvent (not parse manually)
event = stripe.webhooks.constructEvent(body, signature, secret);

// 2. Never trust unsigned events
if (!signature) return NextResponse.json({}, { status: 400 });

// 3. Use environment variables for the secret
// STRIPE_WEBHOOK_SECRET starts with "whsec_"

// 4. Different secrets for test vs live webhooks
// Test: whsec_test_...
// Live: whsec_...
```
