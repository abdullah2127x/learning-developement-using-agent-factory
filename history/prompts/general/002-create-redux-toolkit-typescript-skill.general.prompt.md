---
id: 002
title: Create Redux Toolkit TypeScript Skill
stage: general
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["redux-toolkit", "typescript", "nextjs", "rtk-query", "skill-creation", "state-management"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/redux-toolkit-typescript/SKILL.md
  - .claude/skills/redux-toolkit-typescript/references/store-setup.md
  - .claude/skills/redux-toolkit-typescript/references/slices-reducers.md
  - .claude/skills/redux-toolkit-typescript/references/async-thunks.md
  - .claude/skills/redux-toolkit-typescript/references/rtk-query.md
  - .claude/skills/redux-toolkit-typescript/references/nextjs-integration.md
  - .claude/skills/redux-toolkit-typescript/references/common-mistakes.md
tests:
  - Skill registered and visible in available skills list
---

## Prompt

Using your "skill-creator-pro" skill create a new skill for Redux Toolkit with TypeScript for Next.js projects. I will use it to build type-safe state management from simple slices to complex async thunks with RTK Query. Use context7 skill to study official Redux Toolkit documentation for TypeScript integration, createSlice, createAsyncThunk, RTK Query, and Next.js App Router Redux setup, then build it so no self assumed knowledge.

## Response snapshot

Created a comprehensive Guide-type skill `redux-toolkit-typescript` with SKILL.md + 6 reference files. Domain discovery used Context7 (`/reduxjs/redux-toolkit`, `/websites/redux_js`, `/reduxjs/react-redux`) and official documentation pages (redux.js.org, redux-toolkit.js.org) for TypeScript usage, Next.js integration, RTK Query API, cache invalidation, and optimistic updates. All knowledge sourced from official docs — zero assumed knowledge.

**Skill structure:**
- `SKILL.md` — Mental model (configureStore→Slices→Thunks→RTK Query→Hooks→Client Components), quick start (complete 5-step Next.js setup), decision trees (need Redux?, thunk vs RTK Query, cache tags), production checklist
- `references/store-setup.md` — configureStore, makeStore pattern, RootState/AppDispatch/AppStore types, middleware (.concat/.prepend), typed hooks (.withTypes), setupListeners, TS version requirements
- `references/slices-reducers.md` — createSlice, PayloadAction, union state types, prepare callbacks, extraReducers builder, matcher patterns, createEntityAdapter, Immer rules
- `references/async-thunks.md` — createAsyncThunk generics (return/arg/thunkAPI config), pre-typed thunks (.withTypes), rejectWithValue, thunkAPI properties, .unwrap()/.match() error handling, cancellation, condition callback, pagination/dependent thunks
- `references/rtk-query.md` — createApi, fetchBaseQuery (auth headers, credentials, transforms), queries/mutations, auto-generated hooks, skip/polling, providesTags/invalidatesTags (LIST pattern), optimistic updates (onQueryStarted + undo), pessimistic updates, code splitting (injectEndpoints), reusable tag helpers
- `references/nextjs-integration.md` — Per-request store rationale, makeStore+StoreProvider+layout patterns, Server vs Client Component rules, loading initial data from server, per-route state (useRef init), RTK Query recommendation (client-only), caching considerations, complete file structure
- `references/common-mistakes.md` — 14 anti-patterns with before/after fixes (global store, useEffect init, RSC hooks, untyped hooks, object extraReducers, missing middleware, spread operator, multiple createApi, missing .unwrap(), server data fetching, missing setupListeners, broad cache tags), debugging checklist table

## Outcome

- ✅ Impact: New reusable skill for type-safe Redux Toolkit state management in Next.js App Router projects
- 🧪 Tests: Skill registered and visible in skills list
- 📁 Files: 7 files created (1 SKILL.md + 6 references)
- 🔁 Next prompts: Test skill by creating a real store setup, validate with skill-validator
- 🧠 Reflection: Official Redux docs had a dedicated Next.js guide (redux.js.org/usage/nextjs) which was the most critical source — per-request store and useRef initialization patterns are non-obvious and differ significantly from SPA Redux

## Evaluation notes (flywheel)

- Failure modes observed: None — all Context7 library IDs resolved correctly on first try
- Graders run and results (PASS/FAIL): PASS — skill registered, all files created, all content from official docs
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Validate skill with skill-validator for quality scoring
