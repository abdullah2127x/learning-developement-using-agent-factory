---
name: nextjs
description: |
  Comprehensive guide for building fullstack Next.js applications with App Router.
  This skill should be used when users need to create pages, layouts, API routes,
  server actions, authentication, middleware, data fetching, caching, or deploy
  production Next.js apps. Covers Server/Client Components, routing, performance,
  and fullstack architecture patterns from beginner to production-grade.
---

# Next.js Fullstack Development

Build production-grade fullstack web applications with Next.js App Router.

## What This Skill Does

- Creates pages, layouts, route handlers, and server actions
- Implements Server and Client Component patterns with proper boundaries
- Builds API endpoints, form handling, and data mutations
- Configures caching, revalidation, and performance optimization
- Sets up middleware/proxy, authentication, and session handling
- Provides architecture patterns for scalable fullstack Next.js apps

## What This Skill Does NOT Do

- Handle infrastructure/DevOps (Docker, Kubernetes, CI/CD pipelines)
- Replace database-specific skills (Prisma, Drizzle, MongoDB)
- Create mobile applications (use React Native)
- Manage DNS, SSL, or domain configuration

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Next.js version, App Router vs Pages Router, existing patterns, TypeScript usage |
| **Conversation** | Feature type (page, API, auth, data mutation), rendering needs |
| **Skill References** | Patterns from `references/` — routing, components, data, API, production |
| **User Guidelines** | Styling system (Tailwind, CSS Modules), state management, testing approach |

---

## Mental Model: How Next.js Works

```
Request → Proxy/Middleware (edge) → Route Match → Render Pipeline
                                                    ├── Server Component (RSC Payload)
                                                    ├── Client Component (JS bundle)
                                                    └── Route Handler (API response)
→ Response (HTML stream / JSON / redirect)
```

**Key insights:**
- **Server Components** are the default. They run on the server, produce RSC Payload, and send zero JS to the client.
- **Client Components** (`'use client'`) add interactivity. They hydrate on the client after initial HTML render.
- **Server Actions** (`'use server'`) are RPC-style functions called from forms/events, executing on the server.
- **Layouts** persist across navigations (no re-render). **Pages** re-render on each navigation.
- **Caching** is opt-in for `fetch`. Use `revalidateTag`/`revalidatePath` for on-demand invalidation.

---

## Decision Trees

### What file do I create?

```
Need UI for a route?           → page.tsx
Need shared wrapper UI?        → layout.tsx
Need loading skeleton?         → loading.tsx
Need error boundary?           → error.tsx ('use client')
Need 404 page?                 → not-found.tsx
Need API endpoint?             → route.ts (in app/api/...)
Need server-side logic on requests? → proxy.ts (project root)
Need SEO metadata?             → export metadata or generateMetadata in page/layout
```

### Server or Client Component?

```
Needs state, effects, event handlers, browser APIs?  → Client ('use client')
Needs to fetch data, use secrets, reduce JS bundle?  → Server (default)
Third-party lib using useState/useEffect internally? → Wrap in Client Component
```

### How to handle data?

```
Read data for page render?     → async Server Component with fetch/db query
Mutate data (create/update/delete)?  → Server Action ('use server')
Need API for external consumers?     → Route Handler (route.ts)
Need real-time data?           → Route Handler with streaming or WebSocket
```

---

## Quick Start

```bash
npx create-next-app@latest my-app --typescript --tailwind --app --src-dir
cd my-app && npm run dev
```

### Minimal App Structure

```
src/app/
├── layout.tsx          # Root layout (required) — <html> + <body>
├── page.tsx            # Home page (/)
├── globals.css         # Global styles
├── blog/
│   ├── page.tsx        # /blog
│   └── [slug]/
│       └── page.tsx    # /blog/:slug
├── api/
│   └── hello/
│       └── route.ts    # GET /api/hello
└── actions.ts          # Server Actions ('use server')
```

---

## Core Patterns at a Glance

| Pattern | Reference File |
|---------|---------------|
| Routing, layouts, pages, dynamic routes, route groups | `references/routing.md` |
| Server Components, Client Components, composition | `references/components.md` |
| Data fetching, caching, revalidation, streaming | `references/data-fetching.md` |
| Server Actions, forms, mutations, optimistic UI | `references/server-actions.md` |
| Route Handlers (API), middleware/proxy, auth | `references/api-and-middleware.md` |
| Performance, SEO, images, fonts, bundle optimization | `references/performance.md` |
| Common mistakes, anti-patterns, debugging | `references/common-mistakes.md` |

---

## Production Checklist

- [ ] Root layout has `<html lang="...">` and `<body>` tags
- [ ] `'use client'` only on components that truly need interactivity
- [ ] Server Actions validate input (use Zod) and handle errors
- [ ] Sensitive data (API keys, tokens) only in server-side code
- [ ] `server-only` package used for modules with secrets
- [ ] Environment variables: `NEXT_PUBLIC_` prefix only for client-safe values
- [ ] Caching strategy defined: `revalidateTag`/`revalidatePath` after mutations
- [ ] `loading.tsx` for async pages, `error.tsx` for error boundaries
- [ ] Images use `next/image` with proper `width`/`height` or `fill`
- [ ] Fonts use `next/font` for zero layout shift
- [ ] Metadata/OpenGraph configured via `generateMetadata`
- [ ] Proxy/middleware only for auth checks, redirects, headers (keep thin)
- [ ] No `markers: true` or debug logs in production
- [ ] Tested with `next build` — no build errors or warnings

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/routing.md` | Pages, layouts, dynamic routes, route groups, parallel/intercepting routes, navigation |
| `references/components.md` | Server vs Client Components, composition, context, third-party libs, environment safety |
| `references/data-fetching.md` | fetch caching, revalidation, streaming, Suspense, use cache, ISR |
| `references/server-actions.md` | Forms, mutations, useActionState, optimistic updates, redirect, cookies |
| `references/api-and-middleware.md` | Route Handlers, proxy/middleware, auth patterns, CORS, cookies, headers |
| `references/performance.md` | Images, fonts, metadata, bundle size, lazy loading, static generation |
| `references/common-mistakes.md` | Anti-patterns, debugging, migration gotchas, Pages Router differences |
