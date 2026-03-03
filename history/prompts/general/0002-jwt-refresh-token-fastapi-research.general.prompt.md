---
id: 0002
title: JWT Refresh Token FastAPI Research
stage: general
date: 2026-03-03
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: AbdullahQureshi
command: research
labels: ["jwt", "refresh-token", "fastapi", "security", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/0002-jwt-refresh-token-fastapi-research.general.prompt.md
tests:
  - none
---

## Prompt

Research the latest and best practices for implementing JWT refresh tokens in FastAPI applications in 2025-2026.

Search for:
1. FastAPI JWT refresh token best practices 2025/2026
2. Token rotation pattern for refresh tokens
3. python-jose vs PyJWT vs authlib for JWT in FastAPI
4. Secure refresh token storage (DB vs Redis)
5. FastAPI official recommendations for token refresh

I need to know:
- What's the recommended library for JWT now (python-jose is unmaintained, what's the replacement?)
- Best pattern: opaque refresh tokens stored in DB vs JWT refresh tokens
- Token rotation: should old refresh tokens be invalidated on use?
- Should refresh tokens be in httpOnly cookies or response body?
- Any security considerations (token family, reuse detection)

Provide concrete recommendations with code patterns if possible.

## Response snapshot

Comprehensive research delivered covering 7 major areas:

1. **JWT Library**: PyJWT is the official FastAPI recommendation (replaces python-jose). joserfc by Authlib author is the future-proof alternative with full JOSE compliance. FastAPI tutorial updated via PR #11589.

2. **Opaque vs JWT Refresh Tokens**: Opaque tokens recommended. Refresh tokens always require server-side lookup for revocation, negating JWT's stateless advantage. Consensus: JWT access tokens + opaque refresh tokens.

3. **Token Rotation**: Always rotate. Implement token family tracking with reuse detection. If a revoked token is reused, revoke the entire family (signals token theft).

4. **Storage**: PostgreSQL for most apps. Redis as optimization at scale (10K+ concurrent users). Hybrid approach for high-scale production.

5. **Delivery**: httpOnly secure cookies for browser clients (XSS immune). Response body for mobile/API clients. Path-scope cookies to /auth endpoints only.

6. **Password Hashing**: pwdlib[argon2] replaces passlib[bcrypt] (passlib unmaintained, broken with bcrypt 5.0.0).

7. **Security**: Token family reuse detection, SHA-256 hashing before storage, SameSite=Strict, constant-time comparison, timing attack prevention.

Complete code patterns provided for: database schema, SQLAlchemy model, token rotation logic, reuse detection, FastAPI endpoints with cookie handling, login/refresh/logout flows.

## Outcome

- Impact: Research artifact for JWT auth implementation decisions
- Tests: N/A (research task)
- Files: PHR created
- Next prompts: Implement JWT refresh token system based on research findings
- Reflection: python-jose to PyJWT migration is now official. The token family pattern for reuse detection is well-established across the ecosystem.

## Evaluation notes (flywheel)

- Failure modes observed: joserfc adoption is still low in tutorials despite being the most complete library; most guides still reference python-jose
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Build a reference implementation using PyJWT + opaque refresh tokens + token families
