# Slices & Reducers

## createSlice

### Basic Slice

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CounterState {
  value: number;
}

const initialState: CounterState = { value: 0 };

const counterSlice = createSlice({
  name: 'counter',
  initialState,   // createSlice infers state type from this
  reducers: {
    increment: (state) => {
      state.value += 1;  // Immer allows "mutation" syntax
    },
    decrement: (state) => {
      state.value -= 1;
    },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
    reset: () => initialState,  // replace entire state
  },
});

export const { increment, decrement, incrementByAmount, reset } = counterSlice.actions;
export default counterSlice.reducer;
```

### Selectors (Co-located)

```typescript
import type { RootState } from '../../store';

// Define selectors alongside the slice
export const selectCount = (state: RootState) => state.counter.value;
export const selectIsPositive = (state: RootState) => state.counter.value > 0;
```

### Union / Discriminated State Types

```typescript
type SliceState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'succeeded'; data: string }
  | { status: 'failed'; error: string };

const initialState: SliceState = { status: 'idle' };

const dataSlice = createSlice({
  name: 'data',
  initialState: initialState as SliceState, // cast needed for union types
  reducers: {
    loadStart: () => ({ status: 'loading' as const }),
    loadSuccess: (_, action: PayloadAction<string>) => ({
      status: 'succeeded' as const,
      data: action.payload,
    }),
    loadFailed: (_, action: PayloadAction<string>) => ({
      status: 'failed' as const,
      error: action.payload,
    }),
  },
});
```

## PayloadAction

Always type action payloads explicitly:

```typescript
import { PayloadAction } from '@reduxjs/toolkit';

reducers: {
  // No payload
  increment: (state) => { state.value += 1; },

  // Simple payload
  setName: (state, action: PayloadAction<string>) => {
    state.name = action.payload;
  },

  // Object payload
  updateUser: (state, action: PayloadAction<{ name: string; email: string }>) => {
    state.name = action.payload.name;
    state.email = action.payload.email;
  },

  // Optional payload (use union)
  toggle: (state, action: PayloadAction<boolean | undefined>) => {
    state.active = action.payload ?? !state.active;
  },
}
```

## Prepare Callbacks

Customize action creator behavior (add meta, generate IDs):

```typescript
import { createSlice, PayloadAction, nanoid } from '@reduxjs/toolkit';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: string;
}

const todosSlice = createSlice({
  name: 'todos',
  initialState: [] as Todo[],
  reducers: {
    addTodo: {
      reducer(state, action: PayloadAction<Todo>) {
        state.push(action.payload);
      },
      prepare(text: string) {
        return {
          payload: {
            id: nanoid(),
            text,
            completed: false,
            createdAt: new Date().toISOString(),
          },
        };
      },
    },
  },
});

// Usage: dispatch(addTodo('Buy milk'))
// Action creator only takes `text`, prepare adds id + timestamp
```

### Prepare with Meta

```typescript
reducers: {
  receivedAll: {
    reducer(state, action: PayloadAction<Page[], string, { currentPage: number }>) {
      state.all = action.payload;
      state.meta = action.meta;
    },
    prepare(payload: Page[], currentPage: number) {
      return { payload, meta: { currentPage } };
    },
  },
}
```

## extraReducers (Builder Pattern)

Handle actions from other slices or createAsyncThunk:

```typescript
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface UsersState {
  entities: User[];
  loading: 'idle' | 'pending' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: UsersState = {
  entities: [],
  loading: 'idle',
  error: null,
};

export const fetchUsers = createAsyncThunk('users/fetchAll', async () => {
  const response = await fetch('/api/users');
  return (await response.json()) as User[];
});

const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    userAdded: (state, action: PayloadAction<User>) => {
      state.entities.push(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = 'pending';
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = 'succeeded';
        state.entities = action.payload;  // action.payload typed as User[]
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = 'failed';
        state.error = action.error.message ?? 'Failed to fetch';
      });
  },
});
```

### Matcher Pattern (Handle Multiple Actions)

```typescript
import { isAnyOf } from '@reduxjs/toolkit';

extraReducers: (builder) => {
  builder
    .addMatcher(
      isAnyOf(fetchUsers.pending, fetchPosts.pending),
      (state) => { state.loading = true; }
    )
    .addMatcher(
      isAnyOf(fetchUsers.rejected, fetchPosts.rejected),
      (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Error';
      }
    );
}
```

### Type Predicate Matchers

```typescript
function isPayloadWithValue(action: UnknownAction):
  action is PayloadAction<{ value: number }> {
  return typeof (action as any).payload?.value === 'number';
}

extraReducers: (builder) => {
  builder.addMatcher(isPayloadWithValue, (state, action) => {
    state.total += action.payload.value; // correctly typed
  });
}
```

## createEntityAdapter

Manage normalized collections of items:

```typescript
import { createEntityAdapter, createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Book {
  id: string;
  title: string;
  author: string;
}

const booksAdapter = createEntityAdapter<Book>({
  // Sort by title
  sortComparer: (a, b) => a.title.localeCompare(b.title),
});

const booksSlice = createSlice({
  name: 'books',
  initialState: booksAdapter.getInitialState({
    // Additional state beyond entities/ids
    loading: false,
  }),
  reducers: {
    bookAdded: booksAdapter.addOne,
    booksReceived: (state, action: PayloadAction<Book[]>) => {
      booksAdapter.setAll(state, action.payload);
    },
    bookUpdated: booksAdapter.updateOne,
    bookRemoved: booksAdapter.removeOne,
  },
});

// Generate typed selectors
export const {
  selectAll: selectAllBooks,
  selectById: selectBookById,
  selectIds: selectBookIds,
  selectEntities: selectBookEntities,
  selectTotal: selectTotalBooks,
} = booksAdapter.getSelectors((state: RootState) => state.books);
```

### Custom ID Field

```typescript
interface Product {
  productId: number;  // not 'id'
  name: string;
}

const productsAdapter = createEntityAdapter({
  selectId: (product: Product) => product.productId,
});
```

## Immer Rules

`createSlice` uses Immer — you can "mutate" state directly:

```typescript
reducers: {
  // MUTATE draft (don't return)
  addItem: (state, action: PayloadAction<Item>) => {
    state.items.push(action.payload);  // mutates draft ✓
  },

  // OR RETURN new state (don't mutate)
  reset: () => initialState,  // returns new state ✓

  // NEVER do both:
  // BAD: state.items.push(item); return state;
}
```

**What you CAN'T do with Immer:**
- Reassign `state` directly: `state = newState` (use `return newState`)
- Mutate primitives: `state = 5` (use `return 5` or wrap in object)
