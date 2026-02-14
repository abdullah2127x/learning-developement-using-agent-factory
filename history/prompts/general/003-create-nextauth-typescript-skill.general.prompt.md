---
id: 003
title: Create NextAuth TypeScript Skill
stage: general
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["nextauth", "auth.js", "typescript", "nextjs", "authentication", "session-management", "skill-creation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/nextauth-typescript/SKILL.md
  - .claude/skills/nextauth-typescript/references/setup-configuration.md
  - .claude/skills/nextauth-typescript/references/providers.md
  - .claude/skills/nextauth-typescript/references/callbacks-session-jwt.md
  - .claude/skills/nextauth-typescript/references/middleware-protection.md
  - .claude/skills/nextauth-typescript/references/database-adapters.md
  - .claude/skills/nextauth-typescript/references/common-mistakes.md
tests:
  - Skill registered and visible in available skills list
---

## Prompt

Using your "skill-creator-pro" skill create a new skill for NextAuth.js authentication in Next.js App Router with TypeScript. I will use it to build complete auth systems from basic credential login to production-ready multi-provider authentication with session management and protected routes. Use context7 skill to study official NextAuth documentation, and common patterns that need to be configure for the current working as mostly parts from the documentation are not much updated. for App Router configuration, providers (Google, GitHub, credentials), session handling, middleware, callbacks, JWT, database adapters, and TypeScript types, then build it so no self assumed knowledge.

## Response snapshot

Created a comprehensive Guide-type skill `nextauth-typescript` with SKILL.md + 6 reference files. Domain discovery used Context7 (`/nextauthjs/next-auth`, 1490 snippets, High reputation) and official documentation pages (authjs.dev) for installation, session management, route protection, v4→v5 migration, and current working patterns. All knowledge sourced from official docs — zero assumed knowledge.

**Skill structure:**
- `SKILL.md` — Mental model (auth.ts→Providers→Callbacks→Session→Middleware→Protection layers), quick start (4-step setup), decision trees (session strategy, provider pattern, edge compatibility), v4→v5 changes table, file structure, production checklist
- `references/setup-configuration.md` — Installation, auth.ts exports (handlers/signIn/signOut/auth), route handler, env var conventions (AUTH_{PROVIDER}_ID auto-detection), trustHost, full config object, edge-safe config split pattern, using auth() everywhere (Server Components, Server Actions, Route Handlers, Client Components via SessionProvider), server actions for sign-in/out
- `references/providers.md` — OAuth providers (GitHub, Google, Discord, Apple, custom OAuth), Credentials provider (basic + Zod validation, limitations), Email/Magic Link provider (Resend), multiple providers setup, custom sign-in page, redirect after sign-in, profile mapping, 80+ built-in providers list
- `references/callbacks-session-jwt.md` — Execution order (signIn→jwt→session→redirect), signIn callback, jwt callback (initial sign-in, session access, update trigger), session callback (JWT vs database params), redirect callback, TypeScript module augmentation (Session/User/JWT types), complete callbacks example, Google token refresh rotation, client session update, strategy comparison
- `references/middleware-protection.md` — middleware.ts basic setup, authorized callback (return values), Next.js 16+ proxy.ts, edge-safe middleware with adapter, matcher patterns, Server Component/API Route/Server Action/Client Component protection, defense-in-depth layers table, security warning
- `references/database-adapters.md` — PrismaAdapter (PostgreSQL + MongoDB schemas), DrizzleAdapter (PostgreSQL schema), auth config with each adapter, session strategy comparison table (JWT vs Database), hybrid JWT + adapter pattern, custom adapter fields
- `references/common-mistakes.md` — 14 anti-patterns with before/after fixes (v4 env vars, getServerSession, missing augmentation, unsync'd callbacks, adapter in middleware, credentials+DB sessions, wrong authorize shape, client signIn, missing matcher, middleware-only auth, wrong cookie prefix, missing SessionProvider, wrong imports, no error handling), v4→v5 migration checklist, debugging table (12 symptoms)

## Outcome

- ✅ Impact: New reusable skill for production-grade authentication with Auth.js v5 in Next.js App Router projects
- 🧪 Tests: Skill registered and visible in skills list
- 📁 Files: 7 files created (1 SKILL.md + 6 references)
- 🔁 Next prompts: Test skill by creating a real auth setup, validate with skill-validator
- 🧠 Reflection: Auth.js v5 documentation is genuinely fragmented — the v4→v5 migration guide and the proxy.ts (Next.js 16+) rename were critical discoveries. The edge-safe config split pattern (auth.config.ts vs auth.ts) for database adapters is non-obvious and would trip up most developers.

## Evaluation notes (flywheel)

- Failure modes observed: None — Context7 library ID resolved correctly, web searches found current patterns
- Graders run and results (PASS/FAIL): PASS — skill registered, all files created, all content from official docs
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Validate skill with skill-validator for quality scoring
