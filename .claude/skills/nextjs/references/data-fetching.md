# Data Fetching, Caching & Revalidation

## Fetching Data in Server Components

Server Components can be `async` — fetch data directly:

```tsx
export default async function Page() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  return <PostList posts={posts} />
}
```

### Direct Database Access

```tsx
import { db } from '@/lib/db'

export default async function Page() {
  const users = await db.user.findMany()
  return <UserTable users={users} />
}
```

---

## Fetch Caching

**Default**: `fetch` requests are NOT cached (changed in Next.js 15).

### Opt-in Caching

```tsx
// Cache indefinitely (until manually revalidated)
const data = await fetch('https://...', { cache: 'force-cache' })

// Cache with time-based revalidation (seconds)
const data = await fetch('https://...', { next: { revalidate: 3600 } })

// No cache (always fresh — this is the default)
const data = await fetch('https://...', { cache: 'no-store' })
```

### Tag-Based Caching

Tag fetches for granular on-demand invalidation:

```tsx
const data = await fetch('https://...', {
  next: { tags: ['posts'] }
})
```

---

## Revalidation Strategies

### Time-Based (ISR)

```tsx
// Re-fetch at most every 60 seconds
const data = await fetch('https://...', { next: { revalidate: 60 } })
```

Or at the page/layout level:

```tsx
export const revalidate = 60  // Revalidate all fetches in this segment every 60s
```

### On-Demand: revalidateTag

```tsx
'use server'
import { revalidateTag } from 'next/cache'

export async function updatePost() {
  await db.post.update(...)
  revalidateTag('posts', 'max')  // stale-while-revalidate (recommended)
}
```

### On-Demand: updateTag (Server Actions only)

For read-your-own-writes (immediate invalidation):

```tsx
'use server'
import { updateTag } from 'next/cache'

export async function createPost(formData: FormData) {
  const post = await db.post.create(...)
  updateTag('posts')           // Immediately expire — user sees new data
  redirect(`/posts/${post.id}`)
}
```

### On-Demand: revalidatePath

Revalidate all data for an entire route:

```tsx
'use server'
import { revalidatePath } from 'next/cache'

export async function updateProfile() {
  await db.user.update(...)
  revalidatePath('/profile')   // Revalidate entire /profile page
}
```

### Comparison

| API | Where | Behavior |
|-----|-------|----------|
| `revalidateTag('x', 'max')` | Server Actions, Route Handlers | Stale-while-revalidate |
| `updateTag('x')` | Server Actions only | Immediate expire (read-your-writes) |
| `revalidatePath('/path')` | Server Actions, Route Handlers | Revalidate entire route |
| `refresh()` from `next/cache` | Server Actions | Re-render current route client-side |

---

## use cache Directive (Cache Components)

Cache entire functions/components beyond just `fetch`:

```tsx
import { cacheTag } from 'next/cache'

export async function getProducts() {
  'use cache'
  cacheTag('products')

  const products = await db.query('SELECT * FROM products')
  return products
}
```

Works with database queries, file system operations, and any server-side computation.

---

## Streaming with Suspense

Stream parts of the page as they become ready:

```tsx
import { Suspense } from 'react'

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<LoadingSkeleton />}>
        <SlowDataComponent />  {/* Streams in when ready */}
      </Suspense>
      <Suspense fallback={<ChartPlaceholder />}>
        <AnalyticsChart />     {/* Independent stream */}
      </Suspense>
    </div>
  )
}
```

### loading.tsx (Automatic Suspense)

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <div className="animate-pulse">Loading dashboard...</div>
}
```

Automatically wraps `page.tsx` in `<Suspense fallback={<Loading />}>`.

---

## Streaming Data to Client Components

Pass a promise from Server to Client, resolve with `use()`:

```tsx
// Server Component
import { Suspense } from 'react'
import UserProfile from './user-profile'
import { getUser } from '@/lib/data'

export default function Page() {
  const userPromise = getUser() // Don't await — pass the promise
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  )
}
```

```tsx
// Client Component
'use client'
import { use } from 'react'

export default function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise)  // Suspends until resolved
  return <p>{user.name}</p>
}
```

---

## Static Generation (generateStaticParams)

Pre-render dynamic routes at build time:

```tsx
export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json())
  return posts.map((post: { slug: string }) => ({ slug: post.slug }))
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  // ...
}
```

### ISR (Incremental Static Regeneration)

Combine `generateStaticParams` with `revalidate`:

```tsx
export const revalidate = 3600 // Regenerate every hour

export async function generateStaticParams() { /* ... */ }

export default async function Page({ params }) { /* ... */ }
```

---

## Pages Router Data Fetching (Legacy)

For `pages/` directory projects:

| Function | Runs | Use Case |
|----------|------|----------|
| `getServerSideProps` | Every request (SSR) | Dynamic data, auth-gated pages |
| `getStaticProps` | Build time (SSG) | Blog posts, docs, marketing pages |
| `getStaticPaths` | Build time | Dynamic routes with SSG |
| `getInitialProps` | Server or client | Legacy — avoid in new code |

```tsx
// pages/posts/[id].tsx
export async function getStaticPaths() {
  const posts = await getPosts()
  return {
    paths: posts.map(p => ({ params: { id: p.id } })),
    fallback: 'blocking',
  }
}

export async function getStaticProps({ params }) {
  const post = await getPost(params.id)
  return { props: { post }, revalidate: 60 }
}
```

**Recommendation**: Use App Router for new projects. Pages Router is maintained but not the focus of new features.
