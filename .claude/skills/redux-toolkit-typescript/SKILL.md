---
name: redux-toolkit-typescript
description: |
  Comprehensive guide for building type-safe state management with Redux Toolkit
  and TypeScript in Next.js App Router projects. This skill should be used when
  users need to create Redux stores, typed slices, async thunks, RTK Query API
  layers, cache invalidation, optimistic updates, or integrate Redux with Next.js
  Server/Client Components. Covers createSlice through production-grade RTK Query.
---

# Redux Toolkit + TypeScript for Next.js

Build type-safe state management — from simple slices to production RTK Query APIs.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing store setup, slices, API layers, project structure |
| **Conversation** | User's specific state requirements, data sources, caching needs |
| **Skill References** | Domain patterns from `references/` (RTK docs, Next.js patterns) |
| **User Guidelines** | Naming conventions, directory structure, testing preferences |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

## Mental Model

```
configureStore (one per app, per-request in Next.js)
       ↓
Slices (state + reducers + actions, auto-typed)
       ↓
Async Thunks (side effects with lifecycle actions)
       ↓
RTK Query (data fetching + caching + auto hooks)
       ↓
Typed Hooks (useAppSelector, useAppDispatch, useAppStore)
       ↓
Client Components only ('use client' — Redux needs React context)
```

**Key insight for Next.js App Router**: Redux store must be created **per-request** (not global singleton). Server Components CANNOT access Redux — only Client Components can.

## Quick Start (Next.js App Router)

### 1. Store with makeStore pattern

```typescript
// lib/store.ts
import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './features/counter/counterSlice';

export const makeStore = () => {
  return configureStore({
    reducer: {
      counter: counterReducer,
    },
  });
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
```

### 2. Typed hooks

```typescript
// lib/hooks.ts
import { useDispatch, useSelector, useStore } from 'react-redux';
import type { AppDispatch, AppStore, RootState } from './store';

export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
```

### 3. StoreProvider (Client Component)

```typescript
// app/StoreProvider.tsx
'use client';
import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore, AppStore } from '../lib/store';

export default function StoreProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef<AppStore | null>(null);
  if (!storeRef.current) {
    storeRef.current = makeStore();
  }
  return <Provider store={storeRef.current}>{children}</Provider>;
}
```

### 4. Wrap layout

```typescript
// app/layout.tsx
import StoreProvider from './StoreProvider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html><body>
      <StoreProvider>{children}</StoreProvider>
    </body></html>
  );
}
```

### 5. Basic slice

```typescript
// lib/features/counter/counterSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CounterState { value: number }
const initialState: CounterState = { value: 0 };

export const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    increment: (state) => { state.value += 1; },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
  },
});

export const { increment, incrementByAmount } = counterSlice.actions;
export const selectCount = (state: { counter: CounterState }) => state.counter.value;
export default counterSlice.reducer;
```

## Decision Trees

### Do I need Redux at all? (Next.js App Router)

```
Is the data server-fetched and read-only?
├─ Yes → Use Server Components + fetch (no Redux needed)
│
Is it form/local UI state?
├─ Yes → Use React state / React Hook Form
│
Is it shared across multiple components and mutable?
├─ Yes → Redux is appropriate
│        Use slices for client-side state
│        Use RTK Query for server data that needs client-side caching
│
└─ No → Use React Context or URL search params
```

### createAsyncThunk vs RTK Query?

```
Need server data with caching, auto-refetch, loading states?
├─ Yes → RTK Query (createApi + build.query/mutation)
│        Auto-generated hooks, tag-based cache invalidation
│        See references/rtk-query.md
│
├─ Need custom async logic that modifies slice state?
│  → createAsyncThunk + extraReducers
│    See references/async-thunks.md
│
└─ Simple sync state updates?
   → createSlice reducers only
```

### RTK Query: providesTags / invalidatesTags?

```
Query returns a list?
├─ Yes → providesTags: [{ type: 'Post', id: 'LIST' }, ...items.map(({ id }) => ({ type: 'Post', id }))]
│        Mutation adds item → invalidatesTags: [{ type: 'Post', id: 'LIST' }]
│        Mutation updates item → invalidatesTags: [{ type: 'Post', id: arg.id }]
│        Mutation deletes item → invalidatesTags: [{ type: 'Post', id: arg.id }]
│
└─ Query returns single item?
   → providesTags: [{ type: 'Post', id: arg }]
     Mutation → invalidatesTags: [{ type: 'Post', id: arg.id }]
```

## File Structure (Recommended)

```
lib/
  store.ts                # makeStore + types
  hooks.ts                # useAppDispatch, useAppSelector, useAppStore
  features/
    counter/
      counterSlice.ts     # Slice + selectors + thunks
    posts/
      postsSlice.ts
  services/
    api.ts                # RTK Query createApi (one per base URL)
    postsApi.ts           # If splitting endpoints
app/
  StoreProvider.tsx        # Client Component wrapping Provider
  layout.tsx              # Wraps children with StoreProvider
```

## Production Checklist

- [ ] `makeStore()` function (NOT global store) for Next.js App Router
- [ ] `StoreProvider` as Client Component with `useRef` initialization
- [ ] Typed hooks via `.withTypes<>()` — never use raw `useSelector`/`useDispatch`
- [ ] `PayloadAction<T>` on all reducer actions with payloads
- [ ] `extraReducers` uses builder callback (NOT object notation)
- [ ] RTK Query middleware added: `.concat(api.middleware)`
- [ ] `setupListeners(store.dispatch)` called for refetchOnFocus/refetchOnReconnect
- [ ] One `createApi` per base URL
- [ ] `providesTags` + `invalidatesTags` for automatic cache invalidation
- [ ] Redux only in Client Components (`'use client'`)
- [ ] Per-route state initialized via `useRef` flag (NOT `useEffect`)
- [ ] Server data fetching via Server Components / fetch (not Redux)

## Reference Files

| File | When to Read |
|------|-------------|
| `references/store-setup.md` | configureStore, types, middleware, typed hooks |
| `references/slices-reducers.md` | createSlice, PayloadAction, prepare, extraReducers, entityAdapter |
| `references/async-thunks.md` | createAsyncThunk generics, thunkAPI, error handling, pre-typed thunks |
| `references/rtk-query.md` | createApi, queries, mutations, cache tags, optimistic updates |
| `references/nextjs-integration.md` | makeStore, StoreProvider, SSR, per-route state, RSC limitations |
| `references/common-mistakes.md` | Anti-patterns with fixes, debugging checklist |

Search patterns for large references:
- Store types → `grep -n "RootState\|AppDispatch\|AppStore" references/store-setup.md`
- Thunk generics → `grep -n "createAsyncThunk<" references/async-thunks.md`
- Cache tags → `grep -n "providesTags\|invalidatesTags" references/rtk-query.md`
- Next.js patterns → `grep -n "makeStore\|StoreProvider\|useRef" references/nextjs-integration.md`
