# Checkout Sessions

## Stripe Client Setup

```typescript
// lib/stripe.ts (SERVER ONLY — no 'use client')
import Stripe from "stripe";

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-01-27.acacia",  // Always pin API version
  typescript: true,
});
```

```typescript
// lib/stripe-client.ts (CLIENT ONLY)
import { loadStripe } from "@stripe/stripe-js";

export const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
);
```

## Hosted Checkout (Simplest)

User is redirected to Stripe's hosted payment page.

### Server Action

```typescript
// app/actions/checkout.ts
"use server";
import { stripe } from "@/lib/stripe";
import { redirect } from "next/navigation";

export async function createCheckoutSession(priceId: string, userId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/cancel`,
    metadata: { userId },           // Pass data you need in webhook
    customer_email: "user@email.com", // Pre-fill email
    allow_promotion_codes: true,
  });

  redirect(session.url!);
}
```

### Page Component (Server Component)

```typescript
// app/checkout/page.tsx
import { createCheckoutSession } from "@/app/actions/checkout";

export default function CheckoutPage() {
  return (
    <form
      action={async () => {
        "use server";
        await createCheckoutSession("price_xxx", "user_123");
      }}
    >
      <button type="submit">Buy Now — $20</button>
    </form>
  );
}
```

### Verify Session on Return

```typescript
// app/success/page.tsx
import { stripe } from "@/lib/stripe";
import { redirect } from "next/navigation";

export default async function SuccessPage({
  searchParams,
}: {
  searchParams: { session_id?: string };
}) {
  const { session_id } = searchParams;

  if (!session_id) redirect("/");

  const session = await stripe.checkout.sessions.retrieve(session_id);

  if (session.status !== "complete") redirect("/");

  return (
    <div>
      <h1>Payment Successful!</h1>
      <p>Confirmation sent to {session.customer_details?.email}</p>
    </div>
  );
}
```

## Embedded Checkout

Checkout renders inside your page — users never leave your site.

### Server Action

```typescript
// app/actions/checkout.ts
"use server";
import { stripe } from "@/lib/stripe";
import { headers } from "next/headers";

export async function fetchClientSecret(): Promise<string> {
  const origin = (await headers()).get("origin") ?? process.env.NEXT_PUBLIC_URL!;

  const session = await stripe.checkout.sessions.create({
    ui_mode: "embedded",
    mode: "payment",
    line_items: [{ price: "price_xxx", quantity: 1 }],
    return_url: `${origin}/return?session_id={CHECKOUT_SESSION_ID}`,
  });

  return session.client_secret!;
}
```

### Client Component

```typescript
// components/EmbeddedCheckout.tsx
"use client";
import {
  EmbeddedCheckout,
  EmbeddedCheckoutProvider,
} from "@stripe/react-stripe-js";
import { stripePromise } from "@/lib/stripe-client";
import { fetchClientSecret } from "@/app/actions/checkout";

export function EmbeddedCheckoutForm() {
  return (
    <EmbeddedCheckoutProvider
      stripe={stripePromise}
      options={{ fetchClientSecret }}
    >
      <EmbeddedCheckout />
    </EmbeddedCheckoutProvider>
  );
}
```

### Return Handler

```typescript
// app/return/page.tsx
import { stripe } from "@/lib/stripe";
import { redirect } from "next/navigation";

export default async function ReturnPage({
  searchParams,
}: {
  searchParams: { session_id?: string };
}) {
  const { session_id } = searchParams;

  if (!session_id) redirect("/");

  const session = await stripe.checkout.sessions.retrieve(session_id, {
    expand: ["line_items", "payment_intent"],
  });

  if (session.status === "open") redirect("/checkout");

  if (session.status === "complete") {
    return (
      <section>
        <p>Thank you! Confirmation sent to {session.customer_details?.email}</p>
      </section>
    );
  }
}
```

## Subscription Checkout

Same as payment but `mode: "subscription"`:

```typescript
// Server Action
export async function createSubscriptionCheckout(
  priceId: string,
  customerId?: string
) {
  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_URL}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.NEXT_PUBLIC_URL}/pricing`,
    // Pass existing customer to avoid creating duplicates
    customer: customerId,
    subscription_data: {
      trial_period_days: 14,          // Optional free trial
      metadata: { userId: "user_123" },
    },
    metadata: { userId: "user_123" }, // Available in checkout.session.completed
    allow_promotion_codes: true,
  });

  redirect(session.url!);
}
```

## Checkout Session Configuration Options

```typescript
stripe.checkout.sessions.create({
  mode: "payment",              // "payment" | "subscription" | "setup"
  ui_mode: "hosted",            // "hosted" | "embedded" (default: hosted)

  // Line items
  line_items: [
    {
      price: "price_xxx",       // Price ID from Dashboard
      quantity: 1,
    },
    // OR inline price data (no pre-created price needed)
    {
      price_data: {
        currency: "usd",
        product_data: { name: "T-Shirt" },
        unit_amount: 2000,       // $20.00 in cents
      },
      quantity: 1,
    },
  ],

  // Customer
  customer: "cus_xxx",          // Existing customer ID
  customer_email: "u@email.com", // Pre-fill (creates new customer)
  customer_creation: "always",   // "always" | "if_required"

  // URLs (hosted mode)
  success_url: "https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
  cancel_url: "https://example.com/cancel",

  // Return URL (embedded mode)
  return_url: "https://example.com/return?session_id={CHECKOUT_SESSION_ID}",

  // Payment methods
  payment_method_types: ["card"],  // Default: all enabled types
  allow_promotion_codes: true,

  // Metadata (available in webhooks)
  metadata: {
    userId: "usr_123",
    orderId: "ord_456",
  },

  // Tax
  automatic_tax: { enabled: true },

  // Shipping
  shipping_address_collection: {
    allowed_countries: ["US", "CA", "GB"],
  },

  // Custom fields
  custom_fields: [
    {
      key: "company_name",
      label: { type: "custom", custom: "Company Name" },
      type: "text",
      optional: true,
    },
  ],
});
```

## Retrieve Session After Payment

```typescript
// Retrieve basic session
const session = await stripe.checkout.sessions.retrieve(sessionId);

// Retrieve with expanded objects
const session = await stripe.checkout.sessions.retrieve(sessionId, {
  expand: ["line_items", "customer", "payment_intent", "subscription"],
});

// Key fields
session.status;                    // "open" | "complete" | "expired"
session.payment_status;            // "paid" | "unpaid" | "no_payment_required"
session.customer;                  // Customer ID string (if expand not set)
session.customer_details?.email;   // Customer email
session.metadata;                  // Your custom metadata
session.subscription;              // Subscription ID (if mode: "subscription")
session.payment_intent;            // Payment intent (if mode: "payment")
```
