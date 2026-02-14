---
name: nextauth-typescript
description: |
  Comprehensive guide for building authentication systems with Auth.js (NextAuth.js v5)
  and TypeScript in Next.js App Router projects. This skill should be used when
  users need to configure auth providers (Google, GitHub, Credentials), session
  management, JWT/database strategies, middleware route protection, database adapters,
  TypeScript type augmentation, or production-ready auth flows.
---

# NextAuth.js (Auth.js v5) + TypeScript for Next.js App Router

## Mental Model

```
auth.ts (config) → Providers → Callbacks → Session Strategy
       ↓                                        ↓
Route Handler (API)                    JWT or Database
       ↓                                        ↓
middleware.ts (protection)          Adapter (Prisma/Drizzle)
       ↓
Server Components → auth()
Client Components → useSession()
```

**Key concept**: Auth.js v5 exports a single `auth()` function that works everywhere — Server Components, Route Handlers, middleware, and Server Actions.

## Quick Start (4 Steps)

### 1. Install + Secret

```bash
npm install next-auth@beta
npx auth secret   # generates AUTH_SECRET in .env.local
```

### 2. auth.ts (root config)

```typescript
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub],
});
```

### 3. Route Handler

```typescript
// app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/auth";
export const { GET, POST } = handlers;
```

### 4. Environment Variables

```env
AUTH_SECRET="generated-secret"
AUTH_GITHUB_ID="your-client-id"
AUTH_GITHUB_SECRET="your-client-secret"
```

**Convention**: OAuth providers auto-detect `AUTH_{PROVIDER}_ID` and `AUTH_{PROVIDER}_SECRET`.

## Decision Trees

### Which Session Strategy?

```
Need server-side session revocation? → database strategy + adapter
  └─ No → JWT strategy (default, no DB needed)
Need to store extra data in session? → JWT + callbacks to extend token
Need multi-device logout? → database strategy
```

### Which Provider Pattern?

```
Social login only? → OAuth providers (Google, GitHub, etc.)
Email/password? → Credentials provider + own DB validation
Magic links? → Email provider + adapter
Multiple providers? → Array of providers + account linking
```

### Edge Runtime Compatible?

```
Using database adapter? → Split config:
  auth.config.ts (edge-safe, no adapter) → middleware
  auth.ts (full config with adapter) → everything else
No adapter (JWT only)? → Single auth.ts works everywhere
```

## Critical v5 Changes (from v4)

| v4 | v5 |
|----|-----|
| `NEXTAUTH_SECRET` | `AUTH_SECRET` |
| `NEXTAUTH_URL` | Auto-detected (remove it) |
| `getServerSession(authOptions)` | `auth()` (no args) |
| `NextAuthOptions` | `NextAuthConfig` |
| Cookie prefix `next-auth` | `authjs` |
| `pages/api/auth/[...nextauth].ts` | `app/api/auth/[...nextauth]/route.ts` |
| `middleware.ts` (Next.js 16+) | `proxy.ts` |

## File Structure

```
├── auth.ts                          # Main config (providers, callbacks, adapter)
├── auth.config.ts                   # Edge-safe config (optional, for middleware)
├── middleware.ts                     # Route protection (or proxy.ts for Next.js 16+)
├── app/
│   ├── api/auth/[...nextauth]/
│   │   └── route.ts                 # { GET, POST } = handlers
│   ├── layout.tsx                   # SessionProvider wrapper
│   └── dashboard/
│       └── page.tsx                 # Protected page
├── components/
│   ├── sign-in.tsx                  # Server Component sign-in
│   └── user-menu.tsx                # Client Component with useSession
├── lib/
│   └── auth-utils.ts                # Helper functions
└── .env.local                       # AUTH_SECRET, AUTH_*_ID, AUTH_*_SECRET
```

## Production Checklist

- [ ] `AUTH_SECRET` set in production (generated via `npx auth secret`)
- [ ] `NEXTAUTH_URL` removed (v5 auto-detects)
- [ ] OAuth redirect URIs configured in provider dashboards
- [ ] Session callback extends session with needed fields (id, role)
- [ ] JWT callback stores needed data in token
- [ ] TypeScript module augmentation for Session/JWT types
- [ ] Middleware protects all private routes
- [ ] CSRF protection enabled (default in v5)
- [ ] Database adapter configured if using database sessions
- [ ] Edge-safe config split if using adapter + middleware
- [ ] Error pages customized (`pages: { error: '/auth/error' }`)
- [ ] Sign-in/sign-out use server actions (not client-side fetch)

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing auth patterns, database setup, middleware, protected routes |
| **Conversation** | User's provider needs, session strategy, protection requirements |
| **Skill References** | Auth patterns from `references/` (providers, callbacks, adapters) |
| **User Guidelines** | Project conventions, security requirements, deployment target |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

## Reference Files

| File | Content | Search Pattern |
|------|---------|----------------|
| `references/setup-configuration.md` | auth.ts config, env vars, route handler, trust host | `grep -i "auth.ts\|NextAuth\|handlers\|AUTH_SECRET"` |
| `references/providers.md` | OAuth, Credentials, Email providers, custom providers | `grep -i "provider\|credentials\|google\|github\|authorize"` |
| `references/callbacks-session-jwt.md` | JWT/session callbacks, module augmentation, token refresh | `grep -i "callback\|jwt\|session\|augment\|declare module"` |
| `references/middleware-protection.md` | middleware.ts, proxy.ts, authorized callback, route guards | `grep -i "middleware\|proxy\|authorized\|protect\|matcher"` |
| `references/database-adapters.md` | Prisma, Drizzle, MongoDB adapters, session strategies | `grep -i "adapter\|prisma\|drizzle\|database\|schema"` |
| `references/common-mistakes.md` | Anti-patterns, v4→v5 gotchas, debugging checklist | `grep -i "mistake\|error\|wrong\|fix\|debug"` |
