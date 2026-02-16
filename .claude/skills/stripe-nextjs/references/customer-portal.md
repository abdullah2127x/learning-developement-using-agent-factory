# Customer Portal

## What It Does

The Stripe Customer Portal lets customers manage their own billing without you building UI:
- View invoices and payment history
- Update payment methods
- Cancel or upgrade/downgrade subscriptions
- Update billing information

## Setup (One-Time in Dashboard)

Before using the portal, configure it in **Stripe Dashboard → Billing → Customer Portal**:
- Enable/disable plan switching
- Set cancellation policies
- Configure which features are visible
- Add your product branding

## Create Portal Session (Server Action)

```typescript
// app/actions/billing.ts
"use server";
import { stripe } from "@/lib/stripe";
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export async function createBillingPortalSession() {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Not authenticated");

  const subscription = await db.subscription.findUnique({
    where: { userId: session.user.id },
    select: { stripeCustomerId: true },
  });

  if (!subscription?.stripeCustomerId) {
    throw new Error("No Stripe customer found");
  }

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: subscription.stripeCustomerId,
    return_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  });

  redirect(portalSession.url);
}
```

## Billing Page (Server Component)

```typescript
// app/billing/page.tsx
import { auth } from "@/auth";
import { getUserSubscription } from "@/lib/subscription";
import { createBillingPortalSession } from "@/app/actions/billing";
import { redirect } from "next/navigation";

export default async function BillingPage() {
  const session = await auth();
  if (!session?.user) redirect("/signin");

  const { subscription, isActive } = await getUserSubscription(session.user.id);

  return (
    <div>
      <h1>Billing</h1>

      {isActive ? (
        <div>
          <p>Plan: {subscription?.stripePriceId}</p>
          <p>
            Renews:{" "}
            {subscription?.currentPeriodEnd?.toLocaleDateString()}
          </p>
          {subscription?.cancelAtPeriodEnd && (
            <p className="text-yellow-600">Cancels at end of period</p>
          )}

          <form action={createBillingPortalSession}>
            <button type="submit">Manage Billing</button>
          </form>
        </div>
      ) : (
        <div>
          <p>No active subscription</p>
          <a href="/pricing">View Plans</a>
        </div>
      )}
    </div>
  );
}
```

## Portal Route Handler (Alternative to Server Action)

If you need a URL to redirect to (e.g., from email links):

```typescript
// app/api/billing-portal/route.ts
import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { auth } from "@/auth";

export async function GET(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.redirect(new URL("/signin", req.url));
  }

  const subscription = await db.subscription.findUnique({
    where: { userId: session.user.id },
  });

  if (!subscription?.stripeCustomerId) {
    return NextResponse.redirect(new URL("/pricing", req.url));
  }

  const portalSession = await stripe.billingPortal.sessions.create({
    customer: subscription.stripeCustomerId,
    return_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  });

  return NextResponse.redirect(portalSession.url);
}
```

## Portal Deep Links

Direct users to specific portal flows:

```typescript
// Update payment method directly
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  flow_data: {
    type: "payment_method_update",
  },
});

// Cancel subscription directly
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  flow_data: {
    type: "subscription_cancel",
    subscription_cancel: {
      subscription: subscriptionId,
    },
  },
});

// Upgrade plan confirm
const portalSession = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: `${process.env.NEXT_PUBLIC_URL}/billing`,
  flow_data: {
    type: "subscription_update_confirm",
    subscription_update_confirm: {
      subscription: subscriptionId,
      items: [
        {
          id: subscriptionItemId,
          price: newPriceId,
          quantity: 1,
        },
      ],
    },
  },
});
```

## Handle Portal Events via Webhooks

After customers use the portal, Stripe fires webhook events. Handle these the same as other subscription events:

| Portal Action | Webhook Event |
|---------------|---------------|
| Update payment method | `customer.updated` |
| Cancel subscription | `customer.subscription.updated` (cancel_at_period_end: true) |
| Immediately cancel | `customer.subscription.deleted` |
| Upgrade plan | `customer.subscription.updated` + `invoice.paid` |
| Downgrade plan | `customer.subscription.updated` |
| Pay overdue invoice | `invoice.paid` |

Your existing webhook handler already covers these — no extra code needed.

## Create Customer Without Checkout

Sometimes you need to create a Stripe customer before they subscribe (e.g., on user registration):

```typescript
export async function createStripeCustomer(userId: string, email: string) {
  const customer = await stripe.customers.create({
    email,
    metadata: { userId },
  });

  await db.user.update({
    where: { id: userId },
    data: { stripeCustomerId: customer.id },
  });

  return customer.id;
}
```
