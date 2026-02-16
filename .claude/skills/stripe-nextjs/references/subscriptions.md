# Subscriptions

## Subscription Flow Overview

```
1. Create checkout session (mode: "subscription")
2. User pays → Stripe creates subscription
3. webhook: checkout.session.completed → store customerId + subscriptionId
4. webhook: invoice.paid → renew access every billing cycle
5. webhook: customer.subscription.deleted → revoke access
```

## Create Subscription Checkout

```typescript
// app/actions/checkout.ts
"use server";
import { stripe } from "@/lib/stripe";
import { redirect } from "next/navigation";
import { auth } from "@/auth";

export async function subscribeToPlan(priceId: string) {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Not authenticated");

  // Check for existing Stripe customer
  const user = await db.user.findUnique({
    where: { id: session.user.id },
    select: { stripeCustomerId: true, email: true },
  });

  const checkoutSession = await stripe.checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?upgraded=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/pricing`,
    customer: user?.stripeCustomerId ?? undefined, // Reuse existing customer
    customer_email: !user?.stripeCustomerId ? user?.email ?? undefined : undefined,
    metadata: { userId: session.user.id },        // Critical for webhook
    subscription_data: {
      metadata: { userId: session.user.id },      // Also on subscription
      trial_period_days: 14,                       // Remove if no trial
    },
    allow_promotion_codes: true,
  });

  redirect(checkoutSession.url!);
}
```

## Database Schema

```typescript
// Prisma schema example
model Subscription {
  id                   String   @id @default(cuid())
  userId               String   @unique
  stripeCustomerId     String   @unique
  stripeSubscriptionId String   @unique
  stripePriceId        String
  status               String   // "active" | "past_due" | "canceled" | "trialing" | "paused"
  currentPeriodStart   DateTime
  currentPeriodEnd     DateTime
  cancelAtPeriodEnd    Boolean  @default(false)
  trialEnd             DateTime?
  createdAt            DateTime @default(now())
  updatedAt            DateTime @updatedAt

  user User @relation(fields: [userId], references: [id])
}
```

## Webhook: Provision & Revoke Access

```typescript
// In your webhook handler:

case "checkout.session.completed": {
  const session = event.data.object as Stripe.Checkout.Session;
  if (session.mode !== "subscription") break;

  const userId = session.metadata?.userId;
  const customerId = session.customer as string;
  const subscriptionId = session.subscription as string;

  // Retrieve the subscription to get period info
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);

  await db.subscription.upsert({
    where: { userId },
    create: {
      userId,
      stripeCustomerId: customerId,
      stripeSubscriptionId: subscriptionId,
      stripePriceId: subscription.items.data[0]?.price.id!,
      status: subscription.status,
      currentPeriodStart: new Date(subscription.current_period_start * 1000),
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
      trialEnd: subscription.trial_end
        ? new Date(subscription.trial_end * 1000)
        : null,
    },
    update: {
      stripeSubscriptionId: subscriptionId,
      status: subscription.status,
      currentPeriodEnd: new Date(subscription.current_period_end * 1000),
    },
  });
  break;
}

case "invoice.paid": {
  const invoice = event.data.object as Stripe.Invoice;
  const subscriptionId = invoice.subscription as string;

  await db.subscription.updateMany({
    where: { stripeSubscriptionId: subscriptionId },
    data: {
      status: "active",
      currentPeriodEnd: new Date(invoice.period_end * 1000),
    },
  });
  break;
}

case "customer.subscription.updated": {
  const sub = event.data.object as Stripe.Subscription;

  await db.subscription.updateMany({
    where: { stripeSubscriptionId: sub.id },
    data: {
      status: sub.status,
      stripePriceId: sub.items.data[0]?.price.id!,
      currentPeriodStart: new Date(sub.current_period_start * 1000),
      currentPeriodEnd: new Date(sub.current_period_end * 1000),
      cancelAtPeriodEnd: sub.cancel_at_period_end,
    },
  });
  break;
}

case "customer.subscription.deleted": {
  const sub = event.data.object as Stripe.Subscription;

  await db.subscription.updateMany({
    where: { stripeSubscriptionId: sub.id },
    data: { status: "canceled" },
  });
  break;
}
```

## Check Subscription Status

```typescript
// lib/subscription.ts
export async function getUserSubscription(userId: string) {
  const subscription = await db.subscription.findUnique({
    where: { userId },
  });

  const isActive =
    subscription?.status === "active" ||
    subscription?.status === "trialing";

  const isPastDue = subscription?.status === "past_due";

  return {
    subscription,
    isActive,
    isPastDue,
    currentPeriodEnd: subscription?.currentPeriodEnd,
  };
}
```

```typescript
// Server Component or Server Action
import { auth } from "@/auth";
import { getUserSubscription } from "@/lib/subscription";

export default async function DashboardPage() {
  const session = await auth();
  const { isActive, currentPeriodEnd } = await getUserSubscription(session!.user.id);

  if (!isActive) return <UpgradePrompt />;

  return (
    <div>
      <p>Subscription active until {currentPeriodEnd?.toLocaleDateString()}</p>
    </div>
  );
}
```

## Subscription Lifecycle States

| Status | Meaning | Access |
|--------|---------|--------|
| `trialing` | In free trial period | Yes |
| `active` | Paid and active | Yes |
| `past_due` | Latest payment failed | Consider blocking |
| `unpaid` | Multiple failures, final invoice uncollectible | Block |
| `canceled` | Deliberately canceled | Block |
| `paused` | Paused (requires billing portal) | Block |
| `incomplete` | Initial payment pending | Block |
| `incomplete_expired` | Initial payment never completed | Block |

## Plan Upgrade / Downgrade

```typescript
// Immediately upgrade (prorated)
export async function upgradePlan(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const subscriptionItemId = subscription.items.data[0]?.id!;

  await stripe.subscriptions.update(subscriptionId, {
    items: [
      {
        id: subscriptionItemId,
        price: newPriceId,
      },
    ],
    proration_behavior: "create_prorations",  // "always_invoice" | "none"
  });
}

// Cancel at period end (graceful)
export async function cancelSubscriptionAtPeriodEnd(subscriptionId: string) {
  await stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  });
}

// Cancel immediately
export async function cancelSubscriptionImmediately(subscriptionId: string) {
  await stripe.subscriptions.cancel(subscriptionId);
}

// Reactivate (before period end)
export async function reactivateSubscription(subscriptionId: string) {
  await stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: false,
  });
}
```

## Free Trial

```typescript
// Via checkout session (most common)
subscription_data: {
  trial_period_days: 14,
}

// Via subscription create (for first subscription only)
await stripe.subscriptions.create({
  customer: customerId,
  items: [{ price: priceId }],
  trial_period_days: 14,
  trial_settings: {
    end_behavior: { missing_payment_method: "create_invoice" },
  },
});
```

**Webhook for trial end**: `customer.subscription.updated` fires when `status` changes from `trialing` → `active` or `past_due`.
