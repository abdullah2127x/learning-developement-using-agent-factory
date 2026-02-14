# Server and Client Components

## The Default: Server Components

Every component in the `app/` directory is a **Server Component** by default. They:

- Run only on the server
- Can be `async` (use `await` directly)
- Can access databases, file system, secrets
- Send zero JavaScript to the client
- Cannot use state, effects, or browser APIs

```tsx
// Server Component (default — no directive needed)
export default async function PostList() {
  const posts = await db.post.findMany() // Direct DB access
  return (
    <ul>
      {posts.map(post => <li key={post.id}>{post.title}</li>)}
    </ul>
  )
}
```

## Client Components

Add `'use client'` at the top of the file to opt in. They:

- Run on both server (SSR) and client (hydration)
- Can use `useState`, `useEffect`, event handlers, browser APIs
- Are part of the JS bundle sent to the client

```tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

## When to Use Which

| Need | Component Type |
|------|---------------|
| Fetch data, access secrets | Server |
| Reduce JS bundle size | Server |
| `useState`, `useEffect` | Client |
| `onClick`, `onChange` | Client |
| Browser APIs (`localStorage`, `window`) | Client |
| Third-party hooks | Client |

**Rule**: Keep the `'use client'` boundary as deep as possible. Only mark interactive leaf components as client.

---

## Composition Patterns

### Pattern 1: Server Parent, Client Child (Most Common)

```tsx
// app/page.tsx (Server)
import LikeButton from './like-button'

export default async function Page() {
  const post = await getPost()
  return (
    <article>
      <h1>{post.title}</h1>
      <LikeButton likes={post.likes} />  {/* Client child */}
    </article>
  )
}
```

```tsx
// app/like-button.tsx (Client)
'use client'
import { useState } from 'react'

export default function LikeButton({ likes }: { likes: number }) {
  const [count, setCount] = useState(likes)
  return <button onClick={() => setCount(c => c + 1)}>{count} likes</button>
}
```

### Pattern 2: Server Component Inside Client Component (Children Slot)

Pass Server Components as `children` to Client Components:

```tsx
// app/modal.tsx (Client)
'use client'
import { useState } from 'react'

export default function Modal({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button onClick={() => setOpen(true)}>Open</button>
      {open && <div className="modal">{children}</div>}
    </>
  )
}
```

```tsx
// app/page.tsx (Server)
import Modal from './modal'
import Cart from './cart' // Server Component

export default function Page() {
  return (
    <Modal>
      <Cart />  {/* Server Component rendered on server, passed as children */}
    </Modal>
  )
}
```

### Pattern 3: Context Providers

Context requires `'use client'`. Wrap provider in a Client Component, use in layout:

```tsx
// app/theme-provider.tsx
'use client'
import { createContext } from 'react'

export const ThemeContext = createContext('light')

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return <ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>
}
```

```tsx
// app/layout.tsx (Server)
import { ThemeProvider } from './theme-provider'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html><body>
      <ThemeProvider>{children}</ThemeProvider>  {/* Provider wraps server content */}
    </body></html>
  )
}
```

**Place providers as deep as possible** — don't wrap the entire `<html>` unnecessarily.

### Pattern 4: Sharing Data Between Server Components

Use `React.cache` to deduplicate fetches across the same request:

```tsx
import { cache } from 'react'

export const getUser = cache(async () => {
  const res = await fetch('https://api.example.com/user')
  return res.json()
})

// Both Server Components call getUser() — only one fetch happens per request
```

### Pattern 5: Sharing Data Across Server and Client

Pass a promise from Server to Client via context, resolve with `use()`:

```tsx
// Server layout: pass promise (don't await)
const userPromise = getUser()
<UserProvider userPromise={userPromise}>{children}</UserProvider>

// Client component: resolve with use()
const user = use(userPromise)
```

---

## Serialization Boundary

Props passed from Server to Client Components must be **serializable**:

| Allowed | Not Allowed |
|---------|-------------|
| Strings, numbers, booleans | Functions (except Server Actions) |
| Arrays, plain objects | Classes, Date objects |
| `null`, `undefined` | DOM nodes, Symbols |
| Server Actions (`'use server'`) | React elements (JSX) — use `children` instead |

---

## Third-Party Components

If a library uses hooks/state but lacks `'use client'`:

```tsx
// app/carousel.tsx — Create a thin wrapper
'use client'
import { Carousel } from 'acme-carousel'
export default Carousel
```

Now use `<Carousel />` freely in Server Components.

---

## Environment Safety

### Preventing Secret Leaks

```tsx
// lib/data.ts
import 'server-only'  // Build error if imported in Client Component

export async function getData() {
  const res = await fetch('...', {
    headers: { authorization: process.env.API_KEY },
  })
  return res.json()
}
```

### Environment Variable Rules

| Prefix | Available In |
|--------|-------------|
| `NEXT_PUBLIC_*` | Server + Client |
| No prefix | Server only (replaced with empty string on client) |

```env
DATABASE_URL=postgres://...       # Server only
NEXT_PUBLIC_APP_URL=https://...   # Available everywhere
```
