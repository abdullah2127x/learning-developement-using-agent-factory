# Common Mistakes & Anti-Patterns

## 1. Using NEXTAUTH_ Environment Variables (v4 Syntax)

```typescript
// BAD: v4 env vars — silently ignored in v5
NEXTAUTH_SECRET="secret"
NEXTAUTH_URL="http://localhost:3000"

// GOOD: v5 env vars
AUTH_SECRET="secret"
// NEXTAUTH_URL is no longer needed — auto-detected
```

## 2. Using getServerSession (v4 Pattern)

```typescript
// BAD: v4 pattern
import { getServerSession } from "next-auth";
import { authOptions } from "@/app/api/auth/[...nextauth]/route";
const session = await getServerSession(authOptions);

// GOOD: v5 pattern
import { auth } from "@/auth";
const session = await auth();
```

## 3. Missing Module Augmentation

```typescript
// BAD: session.user.id is unknown/error
const session = await auth();
console.log(session?.user?.id); // TypeScript error

// GOOD: Augment the types
// types/next-auth.d.ts
declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role: string;
    } & DefaultSession["user"];
  }
}
```

## 4. Not Syncing jwt and session Callbacks

```typescript
// BAD: Data added to token but not exposed in session
callbacks: {
  jwt: async ({ token, user }) => {
    if (user) token.role = user.role;
    return token;
  },
  // Missing session callback — role never reaches client!
}

// GOOD: Both callbacks in sync
callbacks: {
  jwt: async ({ token, user }) => {
    if (user) token.role = user.role;
    return token;
  },
  session: async ({ session, token }) => {
    session.user.role = token.role as string; // Expose to client
    return session;
  },
}
```

## 5. Database Adapter in Middleware (Edge Runtime Error)

```typescript
// BAD: Importing adapter in middleware crashes Edge Runtime
// middleware.ts
import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma } from "@/lib/prisma"; // Node.js only!

// GOOD: Split config — edge-safe for middleware
// auth.config.ts (no adapter)
export default { providers: [GitHub] } satisfies NextAuthConfig;

// middleware.ts
import NextAuth from "next-auth";
import authConfig from "./auth.config";
export const { auth: middleware } = NextAuth(authConfig);
```

## 6. Credentials Provider with Database Sessions

```typescript
// BAD: Credentials + database strategy — won't work properly
{
  adapter: PrismaAdapter(prisma),
  session: { strategy: "database" },
  providers: [Credentials({ ... })],
}

// GOOD: Credentials must use JWT strategy
{
  adapter: PrismaAdapter(prisma),  // Optional for account storage
  session: { strategy: "jwt" },    // JWT required for Credentials
  providers: [Credentials({ ... })],
}
```

## 7. authorize() Returning Wrong Shape

```typescript
// BAD: Missing required fields or wrong types
authorize: async (credentials) => {
  return { username: "test" }; // Missing id, email

// GOOD: Return proper User object (or null)
authorize: async (credentials) => {
  if (!valid) return null;
  return {
    id: user.id,          // Required: string
    name: user.name,      // Optional
    email: user.email,    // Optional
    image: user.image,    // Optional
  };
}
```

## 8. Client-Side signIn Without Server Action

```typescript
// BAD: Exposes auth flow to client manipulation
"use client";
import { signIn } from "next-auth/react";
// Client-side signIn works but less secure

// BETTER: Server Action (recommended by Auth.js team)
import { signIn } from "@/auth";  // Server-side import!

export function SignInButton() {
  return (
    <form action={async () => {
      "use server";
      await signIn("github");
    }}>
      <button type="submit">Sign in</button>
    </form>
  );
}
```

## 9. Missing middleware.ts Matcher

```typescript
// BAD: No matcher — middleware runs on EVERY request (including static)
export { auth as middleware } from "@/auth";

// GOOD: Exclude static assets
export { auth as middleware } from "@/auth";
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

## 10. Relying Only on Middleware for Authorization

```typescript
// BAD: Only checking in middleware
// middleware.ts — checks auth
// But API routes/server actions have NO protection!

// GOOD: Defense in depth — check everywhere
// middleware.ts — first layer (convenience, redirects)
// Server Component — second layer
const session = await auth();
if (!session) redirect("/signin");

// API Route — third layer
export async function GET() {
  const session = await auth();
  if (!session) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
}

// Server Action — fourth layer
export async function createPost() {
  const session = await auth();
  if (!session) throw new Error("Unauthorized");
}
```

## 11. Wrong Cookie Prefix After Migration

```typescript
// BAD: Checking for old cookie name
const hasSession = cookies().get("next-auth.session-token");

// GOOD: v5 uses new cookie prefix
const hasSession = cookies().get("authjs.session-token");
// Or use auth() instead of reading cookies directly
```

## 12. Forgetting SessionProvider

```typescript
// BAD: useSession() returns null/undefined
"use client";
const { data: session } = useSession(); // Always null!

// GOOD: Wrap with SessionProvider in layout
// app/layout.tsx
import { SessionProvider } from "next-auth/react";
export default function Layout({ children }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

## 13. Importing from Wrong Path

```typescript
// BAD: Mixing v4 and v5 imports
import { useSession } from "next-auth/react";     // Client ✓
import { signIn } from "next-auth/react";          // Client (less secure)
import { getServerSession } from "next-auth";      // v4 — wrong!

// GOOD: v5 import patterns
// Server-side (auth.ts exports):
import { auth, signIn, signOut } from "@/auth";

// Client-side (next-auth/react):
import { useSession, signIn, signOut } from "next-auth/react";
import { SessionProvider } from "next-auth/react";
```

## 14. Not Handling Auth Errors

```typescript
// BAD: No error handling on sign in
await signIn("credentials", { email, password });
// If credentials are wrong, user sees default error page

// GOOD: Handle errors with redirect: false
// Client-side
const result = await signIn("credentials", {
  email,
  password,
  redirect: false,
});
if (result?.error) {
  setError("Invalid credentials");
}

// Server-side (Server Action)
import { AuthError } from "next-auth";
try {
  await signIn("credentials", { email, password });
} catch (error) {
  if (error instanceof AuthError) {
    switch (error.type) {
      case "CredentialsSignin":
        return { error: "Invalid credentials" };
      default:
        return { error: "Something went wrong" };
    }
  }
  throw error; // Re-throw non-auth errors
}
```

---

## v4 → v5 Migration Checklist

| Step | v4 | v5 |
|------|-----|-----|
| Package | `next-auth` | `next-auth@beta` |
| Config location | `pages/api/auth/[...nextauth].ts` | `auth.ts` (root) + `app/api/auth/[...nextauth]/route.ts` |
| Config type | `NextAuthOptions` | `NextAuthConfig` |
| Env: secret | `NEXTAUTH_SECRET` | `AUTH_SECRET` |
| Env: URL | `NEXTAUTH_URL` | Remove (auto-detected) |
| Env: providers | Custom names | `AUTH_{PROVIDER}_ID` + `AUTH_{PROVIDER}_SECRET` |
| Session getter | `getServerSession(authOptions)` | `auth()` |
| Middleware | `withAuth` from `next-auth/middleware` | `export { auth as middleware }` from `@/auth` |
| Cookie prefix | `next-auth` | `authjs` |
| OAuth 1.0 | Supported | Removed |
| Adapter packages | `@next-auth/prisma-adapter` | `@auth/prisma-adapter` |
| Min Next.js | 12 | 14 |
| Middleware file | `middleware.ts` | `middleware.ts` (or `proxy.ts` for Next.js 16+) |

---

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `AUTH_SECRET` error in production | Missing env var | Set `AUTH_SECRET` in production env |
| OAuth callback error | Wrong redirect URI | Check provider dashboard callback URL |
| Session is null everywhere | Missing SessionProvider | Wrap app with SessionProvider |
| session.user.id undefined | Missing callbacks | Add jwt + session callbacks to sync data |
| TypeScript errors on session | No module augmentation | Create `types/next-auth.d.ts` |
| Edge Runtime crash | Adapter in middleware | Split into auth.config.ts + auth.ts |
| Credentials always return null | authorize() logic | Check return value — must return User or null |
| Infinite redirect loop | Middleware protecting sign-in page | Exclude auth routes from matcher |
| Old cookies causing issues | v4 → v5 migration | Clear `next-auth.*` cookies, use `authjs.*` |
| `useSession` always loading | No SessionProvider | Add SessionProvider to root layout |
| CSRF token mismatch | Stale page | Refresh page, check AUTH_SECRET consistency |
| Account linking fails | Different emails | Use same email across providers or handle in signIn callback |
