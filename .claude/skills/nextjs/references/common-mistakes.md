# Common Mistakes & Anti-Patterns

## Critical Mistakes

### 1. Marking Everything as 'use client'

```tsx
// BAD — entire page is client, no SSR benefits
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetch('/api/data').then(...) }, [])
  return <div>{data?.title}</div>
}

// GOOD — Server Component fetches data, Client only for interactivity
export default async function Page() {
  const data = await getData() // Server fetch
  return (
    <div>
      <h1>{data.title}</h1>
      <LikeButton /> {/* Only this is 'use client' */}
    </div>
  )
}
```

### 2. Fetching Data in Client Components When Server Would Work

```tsx
// BAD — unnecessary client-side fetch
'use client'
export default function UserList() {
  const [users, setUsers] = useState([])
  useEffect(() => {
    fetch('/api/users').then(r => r.json()).then(setUsers)
  }, [])
  return <ul>{users.map(...)}</ul>
}

// GOOD — direct server fetch, zero client JS
export default async function UserList() {
  const users = await db.user.findMany()
  return <ul>{users.map(...)}</ul>
}
```

### 3. Exposing Secrets to the Client

```tsx
// BAD — API_KEY accessible on client
const res = await fetch('https://api.com', {
  headers: { Authorization: process.env.API_KEY } // undefined on client!
})

// GOOD — use server-only module
import 'server-only'
export async function getData() {
  return fetch('...', { headers: { Authorization: process.env.API_KEY } })
}
```

### 4. Not Validating Server Action Inputs

```tsx
// BAD — trusting raw FormData
export async function createPost(formData: FormData) {
  'use server'
  await db.post.create({
    data: { title: formData.get('title') as string } // No validation!
  })
}

// GOOD — validate with Zod
export async function createPost(formData: FormData) {
  'use server'
  const result = schema.safeParse({ title: formData.get('title') })
  if (!result.success) return { errors: result.error.flatten() }
  await db.post.create({ data: result.data })
}
```

### 5. redirect() After Other Code

```tsx
// BAD — code after redirect never runs (redirect throws)
export async function action() {
  'use server'
  redirect('/posts')
  revalidatePath('/posts') // NEVER REACHED

  // GOOD — revalidate BEFORE redirect
  revalidatePath('/posts')
  redirect('/posts')
}
```

---

## Moderate Mistakes

### 6. Not Using loading.tsx

```
// BAD — page hangs while data loads (no feedback)
app/dashboard/page.tsx  ← slow async fetch, white screen

// GOOD — add loading skeleton
app/dashboard/loading.tsx  ← shown immediately while page loads
app/dashboard/page.tsx
```

### 7. Fat Middleware/Proxy

```tsx
// BAD — database query in middleware (runs on EVERY request)
export async function proxy(request: NextRequest) {
  const user = await db.user.findUnique({ where: { id: getIdFromToken(request) } })
  if (!user.isAdmin) return NextResponse.redirect(...)
}

// GOOD — lightweight check in middleware, full check in page
export function proxy(request: NextRequest) {
  const token = request.cookies.get('session')
  if (!token) return NextResponse.redirect(new URL('/login', request.url))
  return NextResponse.next()
}
```

### 8. Importing Server Components Into Client Components

```tsx
// BAD — this DOESN'T work
'use client'
import ServerComponent from './server-component' // Becomes client component!

// GOOD — pass as children
'use client'
export function ClientWrapper({ children }) {
  return <div onClick={...}>{children}</div>
}

// In a Server Component:
<ClientWrapper>
  <ServerComponent />  {/* Rendered on server, passed as children */}
</ClientWrapper>
```

### 9. Missing Error Boundaries

```tsx
// BAD — unhandled error crashes entire page
app/dashboard/page.tsx  ← throws error → white screen

// GOOD — error boundary catches it
app/dashboard/error.tsx  ← graceful error UI
app/dashboard/page.tsx
```

```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### 10. Using useRouter for Simple Links

```tsx
// BAD — unnecessary JS for navigation
'use client'
const router = useRouter()
<button onClick={() => router.push('/about')}>About</button>

// GOOD — semantic, accessible, prefetched
import Link from 'next/link'
<Link href="/about">About</Link>
```

---

## Subtle Mistakes

### 11. Forgetting Await on params/searchParams (Next.js 15+)

```tsx
// BAD — params is a Promise now!
export default function Page({ params }) {
  const slug = params.slug // ERROR: params is a Promise
}

// GOOD
export default async function Page({ params }) {
  const { slug } = await params
}
```

### 12. Duplicate Fetches Across Components

```tsx
// PROBLEM — same fetch in layout + page = 2 requests?
// Actually OK — Next.js + React automatically deduplicates identical fetch() calls
// within the same render. But for DB queries, use React.cache:

import { cache } from 'react'
export const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } })
})
```

### 13. Route Handler + Page in Same Folder

```
// BAD — route.ts conflicts with page.tsx
app/api/route.ts
app/api/page.tsx  ← can't coexist!

// GOOD — separate API from pages
app/api/users/route.ts
app/users/page.tsx
```

### 14. Context Provider Too High

```tsx
// BAD — wraps entire app, prevents static optimization
<html>
  <body>
    <AllProvidersEver>     {/* Huge client boundary */}
      {children}
    </AllProvidersEver>
  </body>
</html>

// GOOD — wrap only where needed
<html>
  <body>
    <nav><ThemeProvider><ThemeToggle /></ThemeProvider></nav>
    {children}  {/* Can still be Server Components */}
  </body>
</html>
```

---

## Debugging Checklist

1. **Build errors**: Run `next build` locally before deploying
2. **Hydration mismatch**: Check for browser-only code in Server Components (Date, Math.random, window)
3. **Missing data**: Is `await` missing on `params`/`searchParams`? (v15+)
4. **Slow page**: Add `loading.tsx`, check for waterfall fetches (use parallel `Promise.all`)
5. **Stale data**: Check caching — did you `revalidateTag`/`revalidatePath` after mutation?
6. **404 on dynamic route**: Is `page.tsx` present? Is `generateStaticParams` returning the slug?
7. **Server Action not working**: Is `'use server'` directive present? Is it async?
8. **Bundle too large**: Run bundle analyzer, check `'use client'` boundaries
9. **Environment variable undefined**: Missing `NEXT_PUBLIC_` prefix for client usage?
10. **Middleware not running**: Check `matcher` config, file location (project root)

---

## Pages Router → App Router Migration Tips

| Pages Router | App Router Equivalent |
|-------------|----------------------|
| `pages/index.tsx` | `app/page.tsx` |
| `pages/_app.tsx` | `app/layout.tsx` |
| `pages/_document.tsx` | `app/layout.tsx` (root) |
| `pages/api/hello.ts` | `app/api/hello/route.ts` |
| `getServerSideProps` | Async Server Component |
| `getStaticProps` | Async Server Component + `revalidate` |
| `getStaticPaths` | `generateStaticParams` |
| `useRouter` (pages) | `useRouter` from `next/navigation` |
| `next/head` | `export const metadata` or `generateMetadata` |
