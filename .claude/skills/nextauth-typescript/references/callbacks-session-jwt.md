# Callbacks, Session & JWT

## Callback Execution Order

```
signIn → jwt → session → redirect
```

1. `signIn` — Control whether user can sign in
2. `jwt` — Modify JWT token (runs on every session access)
3. `session` — Modify session object exposed to client
4. `redirect` — Control redirect after sign in/out

## signIn Callback

Control who can sign in:

```typescript
callbacks: {
  signIn: async ({ user, account, profile, email, credentials }) => {
    // Allow all OAuth sign-ins
    if (account?.provider !== "credentials") return true;

    // For credentials, check if email is verified
    const dbUser = await getUserByEmail(user.email!);
    if (!dbUser?.emailVerified) return false;

    return true;
  },
}
```

Return `true` to allow, `false` to deny, or a URL string to redirect.

## jwt Callback

Modify the JWT token. Runs on:
- Initial sign in (`account` + `profile` available)
- Every session access (only `token` available)
- Token update via `update()` trigger

```typescript
callbacks: {
  jwt: async ({ token, user, account, profile, trigger, session }) => {
    // Initial sign in — persist user data to token
    if (user) {
      token.id = user.id;
      token.role = user.role;
    }

    // OAuth — persist access token
    if (account) {
      token.accessToken = account.access_token;
      token.refreshToken = account.refresh_token;
      token.expiresAt = account.expires_at;
    }

    // Manual update trigger (from client useSession().update())
    if (trigger === "update" && session) {
      token.name = session.name;
    }

    return token;
  },
}
```

## session Callback

Shape the session object exposed to `auth()` and `useSession()`:

```typescript
callbacks: {
  session: async ({ session, token, user }) => {
    // JWT strategy — data comes from token
    if (token) {
      session.user.id = token.id as string;
      session.user.role = token.role as string;
    }

    // Database strategy — data comes from user
    // if (user) {
    //   session.user.id = user.id;
    //   session.user.role = user.role;
    // }

    return session;
  },
}
```

## redirect Callback

Control post-auth redirects:

```typescript
callbacks: {
  redirect: async ({ url, baseUrl }) => {
    // Allow relative URLs
    if (url.startsWith("/")) return `${baseUrl}${url}`;
    // Allow same-origin URLs
    if (new URL(url).origin === baseUrl) return url;
    // Default to base URL
    return baseUrl;
  },
}
```

## TypeScript Module Augmentation

Extend default types to include custom fields:

```typescript
// types/next-auth.d.ts
import { DefaultSession, DefaultUser } from "next-auth";
import { DefaultJWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      role: string;
    } & DefaultSession["user"];
  }

  interface User extends DefaultUser {
    role: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    id: string;
    role: string;
    accessToken?: string;
    refreshToken?: string;
    expiresAt?: number;
  }
}
```

**Important**: This file must be included in `tsconfig.json` `include` array.

## Complete Callbacks Example

```typescript
// auth.ts
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import { prisma } from "@/lib/prisma";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub],
  callbacks: {
    signIn: async ({ user, account }) => {
      if (account?.provider === "github") {
        // Check if user is allowed
        const allowed = await prisma.allowedUser.findUnique({
          where: { email: user.email! },
        });
        return !!allowed;
      }
      return true;
    },

    jwt: async ({ token, user, account }) => {
      if (user) {
        // First sign in — look up role from DB
        const dbUser = await prisma.user.findUnique({
          where: { email: user.email! },
          select: { id: true, role: true },
        });
        token.id = dbUser?.id ?? user.id;
        token.role = dbUser?.role ?? "user";
      }
      if (account) {
        token.accessToken = account.access_token;
      }
      return token;
    },

    session: async ({ session, token }) => {
      session.user.id = token.id as string;
      session.user.role = token.role as string;
      return session;
    },
  },
});
```

## Google Token Refresh Rotation

For long-lived access to Google APIs:

```typescript
import Google from "next-auth/providers/google";

export const { handlers, auth } = NextAuth({
  providers: [
    Google({
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
  ],
  callbacks: {
    jwt: async ({ token, account }) => {
      // Initial sign in
      if (account) {
        return {
          ...token,
          accessToken: account.access_token,
          refreshToken: account.refresh_token,
          expiresAt: account.expires_at! * 1000, // Convert to ms
        };
      }

      // Token still valid
      if (Date.now() < (token.expiresAt as number)) {
        return token;
      }

      // Token expired — refresh
      try {
        const response = await fetch("https://oauth2.googleapis.com/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            client_id: process.env.AUTH_GOOGLE_ID!,
            client_secret: process.env.AUTH_GOOGLE_SECRET!,
            grant_type: "refresh_token",
            refresh_token: token.refreshToken as string,
          }),
        });

        const tokens = await response.json();

        if (!response.ok) throw tokens;

        return {
          ...token,
          accessToken: tokens.access_token,
          expiresAt: Date.now() + tokens.expires_in * 1000,
          refreshToken: tokens.refresh_token ?? token.refreshToken,
        };
      } catch (error) {
        console.error("Error refreshing token:", error);
        return { ...token, error: "RefreshTokenError" };
      }
    },
    session: async ({ session, token }) => {
      session.error = token.error as string | undefined;
      return session;
    },
  },
});
```

## Session Update from Client

Trigger JWT callback with `trigger: "update"`:

```typescript
"use client";
import { useSession } from "next-auth/react";

export function ProfileForm() {
  const { data: session, update } = useSession();

  const handleSave = async (name: string) => {
    // This triggers jwt callback with trigger: "update"
    await update({ name });
  };

  return <button onClick={() => handleSave("New Name")}>Update</button>;
}
```

## Session Strategies

### JWT (Default)

```typescript
session: { strategy: "jwt" }
```

- No database required
- Token stored in cookie
- Callbacks: `jwt` → `session`
- `session` callback receives `token` parameter

### Database

```typescript
session: { strategy: "database" }
```

- Requires adapter (Prisma, Drizzle, etc.)
- Session stored in DB
- Callbacks: `session` only (no `jwt` callback)
- `session` callback receives `user` parameter
- Supports server-side session revocation

### Session Configuration

```typescript
session: {
  strategy: "jwt",
  maxAge: 30 * 24 * 60 * 60,  // 30 days (seconds)
  updateAge: 24 * 60 * 60,     // Refresh session every 24 hours
}
```
