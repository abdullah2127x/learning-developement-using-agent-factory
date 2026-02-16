# Common Mistakes & Anti-Patterns

## 1. Parsing the Body Before Signature Verification

```typescript
// BAD: JSON.parse() corrupts the raw body
export async function POST(req: NextRequest) {
  const body = await req.json();  // WRONG — breaks signature!
  stripe.webhooks.constructEvent(JSON.stringify(body), signature, secret);
}

// GOOD: Always use req.text() for raw body
export async function POST(req: NextRequest) {
  const body = await req.text();  // Raw string required
  stripe.webhooks.constructEvent(body, signature, secret);
}
```

## 2. Exposing Secret Key to Client

```typescript
// BAD: NEXT_PUBLIC_ prefix exposes key to browser
NEXT_PUBLIC_STRIPE_SECRET_KEY="sk_live_..."  // NEVER DO THIS

// GOOD: Server-only key
STRIPE_SECRET_KEY="sk_live_..."  // No NEXT_PUBLIC_ prefix
// Only used in Server Components, Server Actions, Route Handlers
```

## 3. Trusting Success URL Instead of Webhooks

```typescript
// BAD: Provisioning access on redirect — can be faked
// app/success/page.tsx
export default async function SuccessPage() {
  // User navigated here — don't trust this for provisioning!
  await db.user.update({ data: { isPremium: true } });  // WRONG
}

// GOOD: Only provision from verified webhook events
// 1. success_url is just for UX (thank you page)
// 2. All provisioning happens in webhook handler
// Webhook: checkout.session.completed → provision access
```

## 4. Not Handling Idempotency

```typescript
// BAD: Processing the same event twice → double provisioning
case "invoice.paid": {
  await provisionAccess(customerId);  // Could run twice!
  break;
}

// GOOD: Track processed events or use upsert
case "invoice.paid": {
  await db.subscription.updateMany({  // updateMany is idempotent
    where: { stripeCustomerId: customerId },
    data: { status: "active" },       // Setting same value twice is fine
  });
  break;
}
```

## 5. Returning Non-200 for Handled Errors

```typescript
// BAD: Stripe retries on non-200, causing infinite retries
try {
  await handleWebhookEvent(event);
} catch (err) {
  return NextResponse.json({ error: err.message }, { status: 500 });  // Stripe retries!
}

// GOOD: Return 200 for business logic errors, 400 only for invalid signatures
try {
  await handleWebhookEvent(event);
} catch (err) {
  console.error("Webhook processing error:", err);
  // Log the error but acknowledge receipt to prevent retries
}
return NextResponse.json({ received: true });  // Always 200 after valid signature
```

## 6. Using Edge Runtime for Webhook Handler

```typescript
// BAD: Edge Runtime doesn't support stripe.webhooks.constructEvent
export const runtime = "edge";  // REMOVE THIS

// GOOD: Must use Node.js runtime
export const runtime = "nodejs";  // Or just omit (default is nodejs)
```

## 7. Not Pinning Stripe API Version

```typescript
// BAD: "latest" can break your app when Stripe updates
const stripe = new Stripe(key, { apiVersion: "latest" });

// GOOD: Pin to specific version
const stripe = new Stripe(key, { apiVersion: "2025-01-27.acacia" });
// Check your Stripe Dashboard API version and keep them in sync
```

## 8. Creating Duplicate Stripe Customers

```typescript
// BAD: Creates new customer every checkout → same user has multiple records
await stripe.checkout.sessions.create({
  customer_email: user.email,  // Creates new customer each time
});

// GOOD: Reuse existing customer ID
await stripe.checkout.sessions.create({
  customer: user.stripeCustomerId ?? undefined,
  customer_email: !user.stripeCustomerId ? user.email : undefined,
});
```

## 9. Not Storing Customer ID After First Checkout

```typescript
// BAD: No customer ID stored → can't use billing portal
// webhook: checkout.session.completed
// Missing: save session.customer to database

// GOOD: Always save customerId in webhook
case "checkout.session.completed": {
  const session = event.data.object as Stripe.Checkout.Session;
  const userId = session.metadata?.userId;

  await db.user.update({
    where: { id: userId },
    data: { stripeCustomerId: session.customer as string },  // SAVE THIS
  });
}
```

## 10. Using webhook Endpoint in Dev Without Stripe CLI

```typescript
// BAD: Testing webhooks by manually hitting the endpoint
// Events won't have valid signatures

// GOOD: Use Stripe CLI for local testing
// stripe listen --forward-to localhost:3000/api/webhooks
// This gives you a local webhook secret (whsec_xxx) for testing
```

## 11. Handling Subscription Changes Only on deleted Event

```typescript
// BAD: Only listening for deletion — misses plan changes, pausing
switch (event.type) {
  case "customer.subscription.deleted":
    await revokeAccess();
}
// Misses: past_due, paused, plan upgrades/downgrades

// GOOD: Handle the full lifecycle
case "customer.subscription.updated": {
  const sub = event.data.object as Stripe.Subscription;
  if (["active", "trialing"].includes(sub.status)) {
    await grantAccess(sub);
  } else {
    await updateStatus(sub);
  }
  break;
}
```

## 12. Missing Metadata for Webhook-to-User Mapping

```typescript
// BAD: Can't identify the user in webhook
await stripe.checkout.sessions.create({
  mode: "subscription",
  line_items: [...],
  success_url: "...",
  // No metadata — how do you know which user completed checkout?
});

// GOOD: Always pass userId in metadata
await stripe.checkout.sessions.create({
  mode: "subscription",
  metadata: { userId: session.user.id },          // On checkout session
  subscription_data: {
    metadata: { userId: session.user.id },          // On subscription too
  },
  ...
});
```

---

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Webhook signature fails | Using `req.json()` instead of `req.text()` | Use `await req.text()` for raw body |
| Webhook fails in Edge Runtime | `stripe.webhooks.constructEvent` not supported | Set `export const runtime = "nodejs"` |
| `sk_live_` key in client bundle | `NEXT_PUBLIC_` prefix on secret key | Remove `NEXT_PUBLIC_` prefix |
| Portal fails "No customer found" | Customer ID not saved after checkout | Save `session.customer` in checkout.session.completed webhook |
| Users get duplicate subscriptions | Creating new customer each checkout | Reuse `stripeCustomerId` from DB |
| Access not revoked on cancel | Only handling `deleted`, not portal cancels | Handle `customer.subscription.updated` for `cancel_at_period_end` |
| Stripe retries webhook forever | Returning 500 on business errors | Return 200 after valid signature verification, even on errors |
| Wrong event types in webhook | API version mismatch | Match `apiVersion` in code to Dashboard webhook version |
| `session.customer` is null | No customer created | Use `customer_email` or `customer_creation: "always"` |
| Trial not detected | Not checking `trialing` status | Include `trialing` in "active" checks |
| `metadata` is null in webhook | Didn't pass metadata in session | Add `metadata: { userId }` to checkout session |
