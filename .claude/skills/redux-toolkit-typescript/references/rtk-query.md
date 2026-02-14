# RTK Query

## What It Is

RTK Query is a data fetching and caching library built into Redux Toolkit. It eliminates hand-written data fetching, loading states, caching, and cache invalidation logic.

**Rule of thumb**: One `createApi` per base URL.

## createApi

### Basic Setup

```typescript
// lib/services/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

interface Post {
  id: number;
  title: string;
  body: string;
  userId: number;
}

export const postsApi = createApi({
  reducerPath: 'postsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Post'],
  endpoints: (build) => ({
    // Query: GET request, returns data
    getPosts: build.query<Post[], void>({
      query: () => '/posts',
      providesTags: (result) =>
        result
          ? [
              { type: 'Post', id: 'LIST' },
              ...result.map(({ id }) => ({ type: 'Post' as const, id })),
            ]
          : [{ type: 'Post', id: 'LIST' }],
    }),

    // Query: GET with parameter
    getPost: build.query<Post, number>({
      query: (id) => `/posts/${id}`,
      providesTags: (result, error, id) => [{ type: 'Post', id }],
    }),

    // Mutation: POST request
    addPost: build.mutation<Post, Omit<Post, 'id'>>({
      query: (body) => ({
        url: '/posts',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Post', id: 'LIST' }],
    }),

    // Mutation: PATCH request
    updatePost: build.mutation<Post, Partial<Post> & Pick<Post, 'id'>>({
      query: ({ id, ...patch }) => ({
        url: `/posts/${id}`,
        method: 'PATCH',
        body: patch,
      }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Post', id }],
    }),

    // Mutation: DELETE request
    deletePost: build.mutation<void, number>({
      query: (id) => ({
        url: `/posts/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [{ type: 'Post', id }],
    }),
  }),
});

// Auto-generated hooks
export const {
  useGetPostsQuery,
  useGetPostQuery,
  useAddPostMutation,
  useUpdatePostMutation,
  useDeletePostMutation,
} = postsApi;
```

### Add to Store

```typescript
// lib/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';
import { postsApi } from '../services/api';

export const makeStore = () => {
  const store = configureStore({
    reducer: {
      [postsApi.reducerPath]: postsApi.reducer,
      // other reducers...
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(postsApi.middleware),
  });

  setupListeners(store.dispatch);
  return store;
};
```

## Using Query Hooks

### Basic Query

```typescript
'use client';
import { useGetPostsQuery } from '@/lib/services/api';

export function PostsList() {
  const { data: posts, isLoading, isError, error, refetch } = useGetPostsQuery();

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {JSON.stringify(error)}</div>;

  return (
    <div>
      {posts?.map((post) => (
        <div key={post.id}>{post.title}</div>
      ))}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

### Query with Parameters

```typescript
function PostDetail({ postId }: { postId: number }) {
  const { data: post, isLoading } = useGetPostQuery(postId);
  // Refetches automatically when postId changes
}
```

### Skip Query (Conditional Fetching)

```typescript
const { data } = useGetPostQuery(postId, {
  skip: !postId,  // don't fetch until postId exists
});

// Or with skipToken
import { skipToken } from '@reduxjs/toolkit/query/react';
const { data } = useGetPostQuery(postId ?? skipToken);
```

### Polling

```typescript
const { data } = useGetPostsQuery(undefined, {
  pollingInterval: 30000,  // refetch every 30 seconds
});
```

### Query Hook Return Values

```typescript
const {
  data,              // The actual response data (undefined until loaded)
  currentData,       // Data for current args (undefined during arg change)
  error,             // Error object if request failed
  isLoading,         // true on first load (no cached data)
  isFetching,        // true whenever a request is in-flight
  isSuccess,         // true if last request succeeded
  isError,           // true if last request failed
  isUninitialized,   // true before the first request
  refetch,           // Function to force re-fetch
} = useGetPostQuery(id);
```

## Using Mutation Hooks

```typescript
'use client';
import { useAddPostMutation, useUpdatePostMutation, useDeletePostMutation } from '@/lib/services/api';

export function PostActions() {
  const [addPost, { isLoading: isAdding }] = useAddPostMutation();
  const [updatePost, { isLoading: isUpdating }] = useUpdatePostMutation();
  const [deletePost] = useDeletePostMutation();

  const handleAdd = async () => {
    try {
      const newPost = await addPost({
        title: 'New Post',
        body: 'Content',
        userId: 1,
      }).unwrap();
      console.log('Created:', newPost);
    } catch (err) {
      console.error('Failed:', err);
    }
  };

  const handleUpdate = async (id: number) => {
    await updatePost({ id, title: 'Updated Title' }).unwrap();
  };

  const handleDelete = async (id: number) => {
    await deletePost(id).unwrap();
  };

  return (
    <button onClick={handleAdd} disabled={isAdding}>
      {isAdding ? 'Adding...' : 'Add Post'}
    </button>
  );
}
```

## Cache Invalidation (Tags)

### Tag Types

```typescript
tagTypes: ['Post', 'User', 'Comment'],
```

### providesTags (Queries — what cache entries exist)

```typescript
// List endpoint — provides LIST tag + individual item tags
getPosts: build.query<Post[], void>({
  query: () => '/posts',
  providesTags: (result) =>
    result
      ? [
          { type: 'Post', id: 'LIST' },
          ...result.map(({ id }) => ({ type: 'Post' as const, id })),
        ]
      : [{ type: 'Post', id: 'LIST' }],
}),

// Single item endpoint
getPost: build.query<Post, number>({
  query: (id) => `/posts/${id}`,
  providesTags: (result, error, id) => [{ type: 'Post', id }],
}),
```

### invalidatesTags (Mutations — what cache entries to refresh)

```typescript
// CREATE → invalidate LIST (refetch all posts)
addPost: build.mutation({
  invalidatesTags: [{ type: 'Post', id: 'LIST' }],
}),

// UPDATE → invalidate specific item
updatePost: build.mutation({
  invalidatesTags: (result, error, { id }) => [{ type: 'Post', id }],
}),

// DELETE → invalidate specific item + LIST
deletePost: build.mutation({
  invalidatesTags: (result, error, id) => [
    { type: 'Post', id },
    { type: 'Post', id: 'LIST' },
  ],
}),
```

### Invalidation Rules

| invalidatesTags | Affects |
|---|---|
| `['Post']` | ALL Post cache entries (general + specific IDs) |
| `[{ type: 'Post', id: 'LIST' }]` | Only list queries, not individual getPost(id) |
| `[{ type: 'Post', id: 5 }]` | Only cache for Post with id=5 |

### Reusable Helper

```typescript
function providesList<R extends { id: string | number }[], T extends string>(
  resultsWithIds: R | undefined,
  tagType: T,
) {
  return resultsWithIds
    ? [
        { type: tagType, id: 'LIST' as const },
        ...resultsWithIds.map(({ id }) => ({ type: tagType, id })),
      ]
    : [{ type: tagType, id: 'LIST' as const }];
}

// Usage
getPosts: build.query<Post[], void>({
  query: () => '/posts',
  providesTags: (result) => providesList(result, 'Post'),
}),
```

## Optimistic Updates

Update cache immediately, undo on failure:

```typescript
updatePost: build.mutation<Post, Partial<Post> & Pick<Post, 'id'>>({
  query: ({ id, ...patch }) => ({
    url: `/posts/${id}`,
    method: 'PATCH',
    body: patch,
  }),
  async onQueryStarted({ id, ...patch }, { dispatch, queryFulfilled }) {
    // Optimistic update — apply immediately
    const patchResult = dispatch(
      postsApi.util.updateQueryData('getPost', id, (draft) => {
        Object.assign(draft, patch);
      }),
    );
    try {
      await queryFulfilled;
    } catch {
      // Undo on failure
      patchResult.undo();
    }
  },
  invalidatesTags: (result, error, { id }) => [{ type: 'Post', id }],
}),
```

## Pessimistic Updates

Wait for server response before updating cache:

```typescript
addPost: build.mutation<Post, Omit<Post, 'id'>>({
  query: (body) => ({
    url: '/posts',
    method: 'POST',
    body,
  }),
  async onQueryStarted(arg, { dispatch, queryFulfilled }) {
    try {
      const { data: newPost } = await queryFulfilled;
      // Insert into list cache after server confirms
      dispatch(
        postsApi.util.updateQueryData('getPosts', undefined, (draft) => {
          draft.push(newPost);
        }),
      );
    } catch {}
  },
}),
```

## fetchBaseQuery Configuration

### With Auth Headers

```typescript
const baseQuery = fetchBaseQuery({
  baseUrl: '/api',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.token;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});
```

### With Credentials (Cookies)

```typescript
const baseQuery = fetchBaseQuery({
  baseUrl: '/api',
  credentials: 'include',
});
```

### Transform Response

```typescript
getUsers: build.query<User[], void>({
  query: () => '/users',
  transformResponse: (response: { data: User[] }) => response.data,
  transformErrorResponse: (response: { status: number }) => response.status,
}),
```

## Code Splitting (Injecting Endpoints)

Split API definitions across files:

```typescript
// lib/services/api.ts (base)
export const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Post', 'User'],
  endpoints: () => ({}),  // empty — endpoints injected later
});

// lib/services/postsApi.ts
import { api } from './api';

export const postsApi = api.injectEndpoints({
  endpoints: (build) => ({
    getPosts: build.query<Post[], void>({
      query: () => '/posts',
    }),
  }),
});

export const { useGetPostsQuery } = postsApi;

// lib/services/usersApi.ts
import { api } from './api';

export const usersApi = api.injectEndpoints({
  endpoints: (build) => ({
    getUsers: build.query<User[], void>({
      query: () => '/users',
    }),
  }),
});

export const { useGetUsersQuery } = usersApi;
```

Store only needs the base api:
```typescript
reducer: { [api.reducerPath]: api.reducer },
middleware: (gDM) => gDM().concat(api.middleware),
```
