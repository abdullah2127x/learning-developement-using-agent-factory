# Middleware & Route Protection

## middleware.ts (Basic)

```typescript
// middleware.ts (project root)
export { auth as middleware } from "@/auth";

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

This runs `auth()` on every matched route. Without `authorized` callback, it only attaches session — does NOT block access.

## authorized Callback (Route Protection)

Add to auth config to control access:

```typescript
// auth.ts (or auth.config.ts for edge split)
callbacks: {
  authorized: ({ auth, request: { nextUrl } }) => {
    const isLoggedIn = !!auth?.user;
    const isOnDashboard = nextUrl.pathname.startsWith("/dashboard");
    const isOnAdmin = nextUrl.pathname.startsWith("/admin");
    const isOnAuth = nextUrl.pathname.startsWith("/auth");

    // Protect dashboard
    if (isOnDashboard && !isLoggedIn) {
      return false; // Redirects to sign-in page
    }

    // Protect admin (role check)
    if (isOnAdmin) {
      return auth?.user?.role === "admin";
    }

    // Redirect authenticated users away from auth pages
    if (isOnAuth && isLoggedIn) {
      return Response.redirect(new URL("/dashboard", nextUrl));
    }

    return true;
  },
}
```

### authorized Return Values

| Return | Effect |
|--------|--------|
| `true` | Allow access |
| `false` | Redirect to sign-in page |
| `Response.redirect(url)` | Custom redirect |

## Next.js 16+ (proxy.ts)

Next.js 16 renamed `middleware.ts` to `proxy.ts`:

```typescript
// proxy.ts (project root — Next.js 16+)
export { auth as middleware } from "@/auth";

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

Functionality is identical; only the filename changes.

## Edge-Safe Middleware (with Database Adapter)

When using a database adapter, split config to keep middleware edge-compatible:

```typescript
// auth.config.ts (edge-safe — NO adapter import)
import type { NextAuthConfig } from "next-auth";

export default {
  providers: [],  // Providers listed here for middleware
  callbacks: {
    authorized: ({ auth, request }) => {
      return !!auth?.user;
    },
  },
} satisfies NextAuthConfig;
```

```typescript
// middleware.ts
import NextAuth from "next-auth";
import authConfig from "./auth.config";

export const { auth: middleware } = NextAuth(authConfig);

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

## Matcher Patterns

### Protect All (except static assets)

```typescript
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

### Protect Specific Routes

```typescript
export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*", "/settings/:path*"],
};
```

### Protect Everything Except Public

```typescript
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|auth/signin|auth/error|$).*)",
  ],
};
```

## Server Component Protection

```typescript
// app/dashboard/page.tsx
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function DashboardPage() {
  const session = await auth();

  if (!session?.user) {
    redirect("/auth/signin");
  }

  return <div>Welcome, {session.user.name}</div>;
}
```

### Role-Based Protection

```typescript
import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function AdminPage() {
  const session = await auth();

  if (!session?.user) redirect("/auth/signin");
  if (session.user.role !== "admin") redirect("/unauthorized");

  return <div>Admin Panel</div>;
}
```

## API Route Protection

### Using auth() Wrapper

```typescript
// app/api/protected/route.ts
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export const GET = auth(function GET(req) {
  if (!req.auth) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }
  return NextResponse.json({ data: "secret" });
});
```

### Using auth() Manually

```typescript
// app/api/users/route.ts
import { auth } from "@/auth";
import { NextResponse } from "next/server";

export async function GET() {
  const session = await auth();

  if (!session?.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const users = await getUsers();
  return NextResponse.json(users);
}
```

## Server Action Protection

```typescript
"use server";
import { auth } from "@/auth";

export async function createPost(data: FormData) {
  const session = await auth();
  if (!session?.user) throw new Error("Unauthorized");

  const title = data.get("title") as string;
  await db.post.create({
    data: { title, authorId: session.user.id },
  });
}
```

## Client Component Protection

### Using useSession

```typescript
"use client";
import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";

export function ProtectedComponent() {
  const { data: session, status } = useSession({
    required: true,  // Redirects to sign-in if unauthenticated
    onUnauthenticated() {
      redirect("/auth/signin");
    },
  });

  if (status === "loading") return <div>Loading...</div>;

  return <div>Protected: {session.user.name}</div>;
}
```

### Reusable Auth Guard

```typescript
"use client";
import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { status } = useSession({
    required: true,
    onUnauthenticated() {
      redirect("/auth/signin");
    },
  });

  if (status === "loading") return <div>Loading...</div>;
  return <>{children}</>;
}
```

## Protection Layers Summary

| Layer | Where | How | Best For |
|-------|-------|-----|----------|
| Middleware | Before render | `authorized` callback | Broad route protection |
| Server Component | During render | `auth()` + `redirect()` | Page-level checks |
| API Route | Request handler | `auth()` check | API protection |
| Server Action | Action body | `auth()` check | Mutation protection |
| Client Component | Client-side | `useSession({ required: true })` | UI-level gating |

**Security note**: Do NOT rely solely on middleware for authorization. Always validate in Server Components, API routes, and Server Actions as well. Middleware is a convenience layer, not a security boundary.
