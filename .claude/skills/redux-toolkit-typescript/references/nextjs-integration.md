# Next.js App Router Integration

## Why Per-Request Store

Next.js App Router has unique constraints:

1. **Server handles multiple requests** — a global store would leak state between users
2. **SSR renders twice** (server + client) — store must produce same initial state to avoid hydration errors
3. **SPA routing** persists layout across pages — per-route state needs manual reset
4. **Aggressive caching** — store architecture must not conflict with Next.js caches

## StoreProvider Pattern

### lib/store.ts

```typescript
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import counterReducer from './features/counter/counterSlice';
import { api } from '../services/api';

export const makeStore = () => {
  const store = configureStore({
    reducer: {
      counter: counterReducer,
      [api.reducerPath]: api.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(api.middleware),
  });

  setupListeners(store.dispatch);
  return store;
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
```

### lib/hooks.ts

```typescript
import { useDispatch, useSelector, useStore } from 'react-redux';
import type { AppDispatch, AppStore, RootState } from './store';

export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
```

### app/StoreProvider.tsx

```typescript
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

### app/layout.tsx

```typescript
import StoreProvider from './StoreProvider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <StoreProvider>{children}</StoreProvider>
      </body>
    </html>
  );
}
```

## Server Components vs Client Components

### Critical Rules

| Rule | Why |
|------|-----|
| Server Components CANNOT access Redux | Redux requires React context (client-only) |
| Any component using `useAppSelector`/`useAppDispatch` MUST be `'use client'` | Hooks require client context |
| Server data fetching should NOT use Redux | Use Server Components + `fetch()` instead |
| Redux should only hold mutable, client-side state | Global shared UI state, not server data |

### Pattern: Server Component Fetches, Client Component Gets Redux

```typescript
// app/users/page.tsx (Server Component — fetches data)
import UsersList from './UsersList';

export default async function UsersPage() {
  // Fetch on server — no Redux
  const users = await fetch('https://api.example.com/users').then((r) => r.json());

  // Pass to client component that may use Redux for UI state
  return <UsersList initialUsers={users} />;
}
```

```typescript
// app/users/UsersList.tsx (Client Component — uses Redux)
'use client';

import { useAppSelector, useAppDispatch } from '@/lib/hooks';
import { setFilter, selectFilter } from '@/lib/features/ui/uiSlice';

export default function UsersList({ initialUsers }: { initialUsers: User[] }) {
  const filter = useAppSelector(selectFilter);
  const dispatch = useAppDispatch();

  const filtered = initialUsers.filter((u) => u.role === filter);

  return (
    <div>
      <select onChange={(e) => dispatch(setFilter(e.target.value))}>
        <option value="all">All</option>
        <option value="admin">Admin</option>
      </select>
      {filtered.map((u) => <div key={u.id}>{u.name}</div>)}
    </div>
  );
}
```

## Loading Initial Data from Server

Pass server data to StoreProvider to seed the store:

```typescript
// app/StoreProvider.tsx
'use client';

import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore, AppStore } from '../lib/store';
import { setUser } from '../lib/features/auth/authSlice';

interface Props {
  children: React.ReactNode;
  initialUser?: { id: string; name: string } | null;
}

export default function StoreProvider({ children, initialUser }: Props) {
  const storeRef = useRef<AppStore | null>(null);
  if (!storeRef.current) {
    storeRef.current = makeStore();
    if (initialUser) {
      storeRef.current.dispatch(setUser(initialUser));
    }
  }

  return <Provider store={storeRef.current}>{children}</Provider>;
}
```

```typescript
// app/layout.tsx
import { cookies } from 'next/headers';
import StoreProvider from './StoreProvider';

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  // Fetch user on server
  const user = await getUser();

  return (
    <html>
      <body>
        <StoreProvider initialUser={user}>
          {children}
        </StoreProvider>
      </body>
    </html>
  );
}
```

## Per-Route State Initialization

Store persists across SPA navigation. Reset per-route state with `useRef`:

```typescript
'use client';

import { useRef } from 'react';
import { useAppStore, useAppSelector, useAppDispatch } from '@/lib/hooks';
import { initializeProduct, selectProduct } from '@/lib/features/product/productSlice';

interface Props {
  product: Product;
}

export default function ProductEditor({ product }: Props) {
  const store = useAppStore();
  const initialized = useRef(false);

  // Initialize ONCE per mount (not in useEffect — would cause hydration mismatch)
  if (!initialized.current) {
    store.dispatch(initializeProduct(product));
    initialized.current = true;
  }

  const currentProduct = useAppSelector(selectProduct);
  const dispatch = useAppDispatch();

  return <div>{currentProduct.name}</div>;
}
```

**WARNING**: Do NOT initialize store in `useEffect` — it runs only on client, causing hydration errors.

## RTK Query in Next.js

### Recommended Approach

The Redux team recommends:
- **Server data fetching** → Server Components + `fetch()` (NOT RTK Query)
- **Client-side data fetching** → RTK Query (for data that needs caching, refetching, mutations on the client)

### RTK Query in Client Components

```typescript
// app/posts/PostsList.tsx
'use client';

import { useGetPostsQuery, useAddPostMutation } from '@/lib/services/api';

export default function PostsList() {
  const { data: posts, isLoading, isError } = useGetPostsQuery();
  const [addPost, { isLoading: isAdding }] = useAddPostMutation();

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error loading posts</div>;

  return (
    <div>
      <button onClick={() => addPost({ title: 'New', body: 'Content', userId: 1 })}>
        Add Post
      </button>
      {posts?.map((post) => <div key={post.id}>{post.title}</div>)}
    </div>
  );
}
```

## Caching Considerations

If routes depend on user state, disable Next.js route caching:

```typescript
// app/dashboard/page.tsx
export const dynamic = 'force-dynamic'; // Don't cache this route
```

After mutations, invalidate Next.js cache alongside RTK Query:

```typescript
import { revalidatePath } from 'next/cache';

// In Server Action:
revalidatePath('/posts');
```

## Complete File Structure

```
app/
  layout.tsx              # Wraps with StoreProvider
  StoreProvider.tsx        # 'use client' — Provider + makeStore
  page.tsx                # Server Component
  posts/
    page.tsx              # Server Component (fetch)
    PostsList.tsx          # 'use client' — RTK Query hooks
lib/
  store.ts                # makeStore, AppStore, RootState, AppDispatch
  hooks.ts                # useAppDispatch, useAppSelector, useAppStore
  features/
    counter/
      counterSlice.ts
    auth/
      authSlice.ts
  services/
    api.ts                # createApi base
    postsApi.ts           # injected endpoints
```
