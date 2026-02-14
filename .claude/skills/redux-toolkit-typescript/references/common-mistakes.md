# Common Mistakes & Anti-Patterns

## 1. Global Singleton Store in Next.js App Router

```typescript
// BAD: Shared across requests — leaks state between users
export const store = configureStore({ reducer: rootReducer });

// GOOD: Per-request store via makeStore
export const makeStore = () => configureStore({ reducer: rootReducer });
```

## 2. Initializing Store in useEffect

```typescript
// BAD: useEffect runs only on client — causes hydration mismatch
useEffect(() => {
  store.dispatch(initializeData(serverData));
}, []);

// GOOD: Initialize in component body with useRef guard
const initialized = useRef(false);
if (!initialized.current) {
  store.dispatch(initializeData(serverData));
  initialized.current = true;
}
```

## 3. Using Redux in Server Components

```typescript
// BAD: Server Components have no React context
// app/page.tsx (Server Component)
import { useAppSelector } from '@/lib/hooks';
export default function Page() {
  const count = useAppSelector(selectCount); // ERROR: hooks not available
}

// GOOD: Only use Redux in Client Components
// app/Counter.tsx
'use client';
import { useAppSelector } from '@/lib/hooks';
export default function Counter() {
  const count = useAppSelector(selectCount); // ✓
}
```

## 4. Using Plain useSelector/useDispatch

```typescript
// BAD: No type safety
import { useSelector, useDispatch } from 'react-redux';
const count = useSelector((state) => state.counter.value); // state is unknown
const dispatch = useDispatch(); // dispatch won't accept thunks

// GOOD: Pre-typed hooks
import { useAppSelector, useAppDispatch } from '@/lib/hooks';
const count = useAppSelector((state) => state.counter.value); // state is RootState
const dispatch = useAppDispatch(); // typed AppDispatch (handles thunks)
```

## 5. Missing PayloadAction Type

```typescript
// BAD: action.payload is any
reducers: {
  setName: (state, action) => {
    state.name = action.payload; // any — no type safety
  },
}

// GOOD: Explicit PayloadAction<T>
reducers: {
  setName: (state, action: PayloadAction<string>) => {
    state.name = action.payload; // string ✓
  },
}
```

## 6. Object Notation for extraReducers

```typescript
// BAD: Object notation — deprecated, worse TypeScript inference
extraReducers: {
  [fetchUser.fulfilled]: (state, action) => { ... } // action is any
}

// GOOD: Builder callback — full type inference
extraReducers: (builder) => {
  builder.addCase(fetchUser.fulfilled, (state, action) => {
    // action.payload correctly typed
  });
}
```

## 7. Forgetting RTK Query Middleware

```typescript
// BAD: RTK Query won't work (no caching, no polling, no refetching)
const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  // middleware not configured!
});

// GOOD: Always add API middleware
const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});
```

## 8. Spread Operator for Middleware (TypeScript)

```typescript
// BAD: Loses type inference
middleware: (getDefaultMiddleware) => [
  ...getDefaultMiddleware(),
  api.middleware,
  logger,
]

// GOOD: Use .concat() and .prepend()
middleware: (getDefaultMiddleware) =>
  getDefaultMiddleware()
    .concat(api.middleware)
    .concat(logger)
```

## 9. Mutating State Outside Immer

```typescript
// BAD: Direct mutation outside createSlice/createReducer
const newState = state;
newState.items.push(item); // mutates original!

// BAD: Returning AND mutating in a reducer
reducers: {
  addItem: (state, action) => {
    state.items.push(action.payload);
    return state; // NEVER return AND mutate
  },
}

// GOOD: Either mutate (no return) OR return new state (no mutate)
reducers: {
  addItem: (state, action) => {
    state.items.push(action.payload); // mutate draft ✓
  },
  reset: () => initialState, // return new state ✓
}
```

## 10. Multiple createApi for Same Base URL

```typescript
// BAD: Separate caches, separate middleware
const usersApi = createApi({
  reducerPath: 'usersApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (build) => ({ ... }),
});

const postsApi = createApi({
  reducerPath: 'postsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (build) => ({ ... }),
});

// GOOD: One createApi, inject endpoints
const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['User', 'Post'],
  endpoints: () => ({}),
});

const usersApi = api.injectEndpoints({
  endpoints: (build) => ({ ... }),
});
```

## 11. Not Using .unwrap() for Error Handling

```typescript
// BAD: dispatch always resolves (even on rejection)
const result = await dispatch(fetchUser(1));
// result is always a fulfilled action — rejected errors swallowed

// GOOD: unwrap() throws on rejection
try {
  const user = await dispatch(fetchUser(1)).unwrap();
  // user is the fulfilled payload
} catch (err) {
  // err is the rejection payload or SerializedError
}
```

## 12. Server Data Fetching via Redux in App Router

```typescript
// BAD: Using Redux/RTK Query for server-rendered data
// app/posts/page.tsx (Server Component)
// Can't use useGetPostsQuery here — it's a hook!

// GOOD: Fetch in Server Component, Redux for client-side state only
export default async function PostsPage() {
  const posts = await fetch('/api/posts').then((r) => r.json());
  return <PostsList initialPosts={posts} />;
}
```

## 13. Forgetting setupListeners

```typescript
// BAD: refetchOnFocus and refetchOnReconnect won't work
const store = configureStore({ ... });
// No setupListeners call

// GOOD: Enable automatic refetching behaviors
import { setupListeners } from '@reduxjs/toolkit/query';
const store = configureStore({ ... });
setupListeners(store.dispatch);
```

## 14. Incorrect Cache Tag Strategy

```typescript
// BAD: General tag — refetches EVERYTHING on any mutation
getPosts: build.query({
  providesTags: ['Post'],  // too broad
}),
updatePost: build.mutation({
  invalidatesTags: ['Post'], // invalidates ALL post queries
}),

// GOOD: Granular tags with LIST pattern
getPosts: build.query({
  providesTags: (result) => [
    { type: 'Post', id: 'LIST' },
    ...(result ?? []).map(({ id }) => ({ type: 'Post' as const, id })),
  ],
}),
updatePost: build.mutation({
  invalidatesTags: (r, e, { id }) => [{ type: 'Post', id }], // only this item
}),
addPost: build.mutation({
  invalidatesTags: [{ type: 'Post', id: 'LIST' }], // only the list
}),
```

---

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Cannot access store" in Server Component | Using hooks in RSC | Add `'use client'` directive |
| Hydration mismatch | Store init in useEffect | Use `useRef` guard pattern |
| State leaks between users | Global singleton store | Use `makeStore()` pattern |
| Redux hooks return `undefined` | Missing Provider | Wrap with `StoreProvider` |
| RTK Query not caching | Missing middleware | Add `api.middleware` to store |
| Types are `any` | Plain useSelector/useDispatch | Use typed hooks with `.withTypes()` |
| Mutations don't trigger refetch | Missing tags | Add `providesTags` + `invalidatesTags` |
| extraReducers payload is `any` | Object notation | Use builder callback pattern |
| `dispatch(thunk())` returns wrong type | Plain useDispatch | Use `useAppDispatch` with AppDispatch type |
| Middleware type errors | Spread operator | Use `.concat()` / `.prepend()` |
| State not resetting on route change | SPA navigation persists store | Use `useRef` init per route |
| refetchOnFocus not working | Missing setupListeners | Call `setupListeners(store.dispatch)` |
