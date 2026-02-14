# Store Setup & Typed Hooks

## configureStore

### Basic Setup

```typescript
import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './features/counter/counterSlice';
import todosReducer from './features/todos/todosSlice';

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    todos: todosReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Next.js App Router: makeStore Pattern

**Critical**: In Next.js App Router, the store must be created per-request, not as a global singleton.

```typescript
// lib/store.ts
import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './features/counter/counterSlice';
import { pokemonApi } from '../services/pokemon';

export const makeStore = () => {
  return configureStore({
    reducer: {
      counter: counterReducer,
      [pokemonApi.reducerPath]: pokemonApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(pokemonApi.middleware),
  });
};

// Infer types from makeStore return
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
```

### With combineReducers (for code splitting)

```typescript
import { combineReducers, configureStore } from '@reduxjs/toolkit';

const rootReducer = combineReducers({
  counter: counterReducer,
  todos: todosReducer,
});

export type RootState = ReturnType<typeof rootReducer>;

export const makeStore = () => configureStore({ reducer: rootReducer });
```

## Middleware Configuration

Use `.concat()` and `.prepend()` for proper TypeScript inference (NOT spread operator):

```typescript
export const makeStore = () => {
  return configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware()
        .prepend(customMiddleware)    // runs first
        .concat(api.middleware)       // runs last
        .concat(loggerMiddleware),
  });
};
```

### Custom Middleware (Typed)

```typescript
import { Middleware } from '@reduxjs/toolkit';

const loggerMiddleware: Middleware<{}, RootState> = (store) => (next) => (action) => {
  console.log('dispatching', action);
  const result = next(action);
  console.log('next state', store.getState());
  return result;
};
```

### Disabling Checks in Production

```typescript
export const makeStore = () => {
  return configureStore({
    reducer: rootReducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: false,      // disable if storing non-serializable data
        immutableCheck: false,         // disable for performance in production
      }),
  });
};
```

## Typed Hooks

### Create Once (lib/hooks.ts)

```typescript
import { useDispatch, useSelector, useStore } from 'react-redux';
import type { AppDispatch, AppStore, RootState } from './store';

// Use these throughout your app instead of plain useDispatch/useSelector
export const useAppDispatch = useDispatch.withTypes<AppDispatch>();
export const useAppSelector = useSelector.withTypes<RootState>();
export const useAppStore = useStore.withTypes<AppStore>();
```

### Usage in Components

```typescript
'use client';
import { useAppSelector, useAppDispatch } from '@/lib/hooks';
import { increment, selectCount } from '@/lib/features/counter/counterSlice';

export function Counter() {
  const count = useAppSelector(selectCount);       // typed as number
  const dispatch = useAppDispatch();               // typed AppDispatch

  return (
    <button onClick={() => dispatch(increment())}>
      Count: {count}
    </button>
  );
}
```

### useAppStore (for imperative dispatch)

```typescript
'use client';
import { useRef } from 'react';
import { useAppStore } from '@/lib/hooks';
import { initializeData } from '@/lib/features/data/dataSlice';

export function DataInitializer({ serverData }: { serverData: Data }) {
  const store = useAppStore();
  const initialized = useRef(false);

  if (!initialized.current) {
    store.dispatch(initializeData(serverData));
    initialized.current = true;
  }

  return null;
}
```

## setupListeners

Enable automatic refetching behaviors for RTK Query:

```typescript
import { setupListeners } from '@reduxjs/toolkit/query';

// Call after store creation
export const makeStore = () => {
  const store = configureStore({ /* ... */ });
  setupListeners(store.dispatch);
  return store;
};
```

This enables:
- `refetchOnFocus: true` — refetch when window regains focus
- `refetchOnReconnect: true` — refetch when network reconnects
- `refetchOnMountOrArgChange: true` — refetch when component mounts

## TypeScript Requirements

- Redux Toolkit 2.x requires TypeScript 5.4+
- Redux Toolkit 1.9.x requires TypeScript 4.7+
