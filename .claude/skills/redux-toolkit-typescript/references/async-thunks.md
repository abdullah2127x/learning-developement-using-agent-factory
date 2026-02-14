# Async Thunks (createAsyncThunk)

## Basic Usage

```typescript
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';

interface User {
  id: number;
  name: string;
  email: string;
}

// Infers return type (User) and arg type (number) automatically
export const fetchUser = createAsyncThunk(
  'users/fetchById',
  async (userId: number) => {
    const response = await fetch(`/api/users/${userId}`);
    return (await response.json()) as User;
  }
);
```

## Generic Type Parameters

Full control with explicit generics:

```typescript
const fetchUser = createAsyncThunk<
  User,           // Return type of the payload creator
  number,         // Argument type (what you pass to dispatch)
  {
    state: RootState;               // getState() return type
    dispatch: AppDispatch;          // dispatch type
    rejectValue: MyKnownError;      // rejectWithValue() type
    extra: { jwt: string };         // extra argument from configureStore
  }
>('users/fetchById', async (userId, thunkApi) => {
  const { jwt } = thunkApi.extra;
  const response = await fetch(`/api/users/${userId}`, {
    headers: { Authorization: `Bearer ${jwt}` },
  });

  if (!response.ok) {
    return thunkApi.rejectWithValue({
      errorMessage: `HTTP ${response.status}`,
    } satisfies MyKnownError);
  }

  return (await response.json()) as User;
});
```

## Pre-Typed createAsyncThunk

Avoid repeating generic config across thunks:

```typescript
// lib/createAppAsyncThunk.ts
import { createAsyncThunk } from '@reduxjs/toolkit';
import type { RootState, AppDispatch } from './store';

export const createAppAsyncThunk = createAsyncThunk.withTypes<{
  state: RootState;
  dispatch: AppDispatch;
  rejectValue: string;
}>();

// Usage — no need to repeat state/dispatch types
export const fetchPosts = createAppAsyncThunk(
  'posts/fetch',
  async (_, { getState }) => {
    const state = getState();  // typed as RootState
    const response = await fetch('/api/posts');
    return (await response.json()) as Post[];
  }
);
```

## ThunkAPI Properties

The second argument to the payload creator:

```typescript
async (arg, thunkApi) => {
  thunkApi.dispatch;        // AppDispatch — dispatch other actions
  thunkApi.getState();      // RootState — read current state
  thunkApi.extra;           // Extra argument from configureStore({ extra })
  thunkApi.requestId;       // Unique ID for this thunk call
  thunkApi.signal;          // AbortController signal for cancellation
  thunkApi.rejectWithValue(value);  // Return typed rejection
  thunkApi.fulfillWithValue(value); // Return with extra meta
}
```

## Error Handling with rejectWithValue

```typescript
interface ApiError {
  message: string;
  code: number;
}

export const updateUser = createAsyncThunk<
  User,
  Partial<User> & { id: number },
  { rejectValue: ApiError }
>('users/update', async (userData, { rejectWithValue }) => {
  try {
    const response = await fetch(`/api/users/${userData.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      return rejectWithValue(error as ApiError);
    }

    return (await response.json()) as User;
  } catch (err) {
    return rejectWithValue({ message: 'Network error', code: 0 });
  }
});
```

## Handling in extraReducers

```typescript
extraReducers: (builder) => {
  builder
    .addCase(updateUser.pending, (state) => {
      state.updating = true;
      state.error = null;
    })
    .addCase(updateUser.fulfilled, (state, action) => {
      state.updating = false;
      // action.payload is typed as User
      const index = state.entities.findIndex((u) => u.id === action.payload.id);
      if (index !== -1) state.entities[index] = action.payload;
    })
    .addCase(updateUser.rejected, (state, action) => {
      state.updating = false;
      if (action.payload) {
        // Typed rejection (rejectWithValue was called)
        state.error = action.payload.message; // typed as ApiError
      } else {
        // Unhandled error
        state.error = action.error.message ?? 'Unknown error';
      }
    });
}
```

## Error Handling in Components

### Using .unwrap()

```typescript
'use client';
import { useAppDispatch } from '@/lib/hooks';
import { updateUser } from '@/lib/features/users/usersSlice';

function UserForm() {
  const dispatch = useAppDispatch();

  const handleSubmit = async (data: UserFormData) => {
    try {
      const user = await dispatch(updateUser(data)).unwrap();
      // user is typed as User — success!
      toast.success(`Updated ${user.name}`);
    } catch (err) {
      // err is the rejectWithValue payload (ApiError) or SerializedError
      const error = err as ApiError;
      toast.error(error.message);
    }
  };
}
```

### Using .match()

```typescript
const resultAction = await dispatch(updateUser(userData));

if (updateUser.fulfilled.match(resultAction)) {
  // resultAction.payload typed as User
  console.log('Updated:', resultAction.payload.name);
} else if (updateUser.rejected.match(resultAction)) {
  if (resultAction.payload) {
    // resultAction.payload typed as ApiError
    console.error(resultAction.payload.message);
  } else {
    console.error(resultAction.error.message);
  }
}
```

## Cancellation

```typescript
export const fetchLongRunning = createAsyncThunk(
  'data/fetchLong',
  async (_, { signal }) => {
    const response = await fetch('/api/slow', { signal });
    return (await response.json()) as Data;
  }
);

// In component:
const promise = dispatch(fetchLongRunning());
promise.abort(); // cancels the request
// The thunk dispatches a `rejected` action with `action.meta.aborted === true`
```

## Condition Callback (Skip Execution)

```typescript
export const fetchUsers = createAsyncThunk(
  'users/fetch',
  async () => {
    const response = await fetch('/api/users');
    return (await response.json()) as User[];
  },
  {
    condition: (_, { getState }) => {
      const state = getState() as RootState;
      // Don't fetch if already loading
      if (state.users.loading === 'pending') {
        return false; // thunk won't execute
      }
    },
  }
);
```

## Common Patterns

### Fetch with Pagination

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export const fetchPosts = createAsyncThunk<
  PaginatedResponse<Post>,
  { page: number; pageSize: number }
>('posts/fetch', async ({ page, pageSize }) => {
  const response = await fetch(`/api/posts?page=${page}&pageSize=${pageSize}`);
  return (await response.json()) as PaginatedResponse<Post>;
});
```

### Dependent Thunks

```typescript
export const initializeApp = createAsyncThunk(
  'app/initialize',
  async (_, { dispatch }) => {
    const user = await dispatch(fetchCurrentUser()).unwrap();
    await dispatch(fetchUserPreferences(user.id)).unwrap();
    await dispatch(fetchNotifications(user.id)).unwrap();
  }
);
```
