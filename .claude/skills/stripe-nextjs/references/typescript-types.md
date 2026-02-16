# TypeScript Types

## Stripe Package Types

Stripe's Node.js library ships with full TypeScript types.

```typescript
import Stripe from "stripe";

// All Stripe resource types
Stripe.Checkout.Session
Stripe.Subscription
Stripe.Invoice
Stripe.Customer
Stripe.PaymentIntent
Stripe.Price
Stripe.Product
Stripe.Event
Stripe.BillingPortal.Session
```

## Narrowing Event Types

Use type assertions to access event-specific data:

```typescript
async function handleStripeEvent(event: Stripe.Event) {
  switch (event.type) {
    case "checkout.session.completed": {
      // event.data.object is typed as Stripe.Checkout.Session
      const session = event.data.object as Stripe.Checkout.Session;

      // TypeScript now knows all Checkout.Session fields
      const customerId: string | null = session.customer as string | null;
      const subscriptionId: string | null = session.subscription as string | null;
      const metadata = session.metadata;      // Record<string, string>
      const mode = session.mode;              // "payment" | "subscription" | "setup"
      break;
    }

    case "invoice.paid": {
      const invoice = event.data.object as Stripe.Invoice;
      const customer = invoice.customer;     // string | Stripe.Customer | null
      const subscriptionId = invoice.subscription; // string | Stripe.Subscription | null
      const periodEnd = invoice.period_end;  // Unix timestamp (number)
      break;
    }

    case "customer.subscription.updated":
    case "customer.subscription.created":
    case "customer.subscription.deleted": {
      const subscription = event.data.object as Stripe.Subscription;
      const status = subscription.status;    // Stripe.Subscription.Status
      const items = subscription.items.data; // Stripe.SubscriptionItem[]
      const priceId = items[0]?.price.id;   // string
      break;
    }
  }
}
```

## Subscription Status Type

```typescript
// Stripe.Subscription.Status is a union:
type SubscriptionStatus =
  | "active"
  | "canceled"
  | "incomplete"
  | "incomplete_expired"
  | "past_due"
  | "paused"
  | "trialing"
  | "unpaid";
```

## Expanding Objects (Types)

When you expand nested objects, TypeScript knows the expanded type:

```typescript
// Without expand — nested objects are string IDs
const session = await stripe.checkout.sessions.retrieve(id);
session.customer;       // string | Stripe.Customer | Stripe.DeletedCustomer | null
session.subscription;   // string | Stripe.Subscription | null

// With expand — TypeScript knows the full object
const session = await stripe.checkout.sessions.retrieve(id, {
  expand: ["customer", "subscription"],
});
// Now TypeScript knows the expanded types
const customerEmail = (session.customer as Stripe.Customer).email;
```

## Database Types

```typescript
// types/billing.ts

export interface UserSubscription {
  userId: string;
  stripeCustomerId: string;
  stripeSubscriptionId: string;
  stripePriceId: string;
  status: Stripe.Subscription.Status;
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelAtPeriodEnd: boolean;
  trialEnd: Date | null;
}

export interface PricingPlan {
  id: string;               // Stripe Price ID (price_xxx)
  name: string;
  description: string;
  amount: number;           // In cents
  currency: string;
  interval: "month" | "year";
  features: string[];
}
```

## Stripe API Version

Pin API version in the constructor — this also affects TypeScript types:

```typescript
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-01-27.acacia",  // Match your Dashboard API version
  typescript: true,                  // Enables stricter types
});
```

**Important**: The API version in code must match the version in your Stripe Dashboard webhook settings. Mismatches can cause unexpected type shapes.

## Webhook Secret Types

```typescript
// The webhook secret starts with "whsec_"
const WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET!;
// Type: string

// constructEvent returns Stripe.Event
let event: Stripe.Event;
event = stripe.webhooks.constructEvent(body, signature, WEBHOOK_SECRET);
```

## Handling Expandable Fields

Many Stripe objects have expandable fields that can be either an ID string or a full object:

```typescript
// Generic helper to safely access expandable fields
function getCustomerId(
  customer: string | Stripe.Customer | Stripe.DeletedCustomer | null
): string | null {
  if (!customer) return null;
  if (typeof customer === "string") return customer;
  return customer.id;
}

// Usage
const customerId = getCustomerId(invoice.customer);
```

## Server Action Return Types

```typescript
// types/actions.ts
export type ActionResult<T = void> =
  | { success: true; data: T }
  | { success: false; error: string };

// Usage in Server Action
"use server";
export async function createCheckoutSession(
  priceId: string
): Promise<ActionResult<{ url: string }>> {
  try {
    const session = await stripe.checkout.sessions.create({ /* ... */ });
    return { success: true, data: { url: session.url! } };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : "Unknown error",
    };
  }
}
```

## Price and Product Type Helpers

```typescript
// lib/stripe-plans.ts
export const PLANS = {
  BASIC: {
    name: "Basic",
    priceId: process.env.STRIPE_BASIC_PRICE_ID!,
    amount: 500,   // $5/month
    features: ["5 projects", "10GB storage"],
  },
  PRO: {
    name: "Pro",
    priceId: process.env.STRIPE_PRO_PRICE_ID!,
    amount: 2000,  // $20/month
    features: ["Unlimited projects", "100GB storage", "Priority support"],
  },
} as const;

export type PlanName = keyof typeof PLANS;

export function getPlanByPriceId(priceId: string): PlanName | null {
  const entry = Object.entries(PLANS).find(
    ([, plan]) => plan.priceId === priceId
  );
  return entry ? (entry[0] as PlanName) : null;
}
```
