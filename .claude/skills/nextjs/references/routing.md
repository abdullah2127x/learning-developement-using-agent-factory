# Routing (App Router)

Next.js uses **file-system based routing**. Folders define route segments; special files define UI.

## Special Files

| File | Purpose | Notes |
|------|---------|-------|
| `page.tsx` | Route UI (makes route publicly accessible) | Required for route to exist |
| `layout.tsx` | Shared wrapper UI, persists across navigations | Root layout required (`<html>`, `<body>`) |
| `loading.tsx` | Loading UI (Suspense boundary) | Wraps page in `<Suspense>` automatically |
| `error.tsx` | Error boundary | Must be `'use client'` |
| `not-found.tsx` | 404 UI | Triggered by `notFound()` |
| `route.ts` | API endpoint (Route Handler) | Cannot coexist with `page.tsx` in same folder |
| `template.tsx` | Like layout but re-mounts on navigation | Use when you need fresh state per navigation |
| `default.tsx` | Fallback for parallel routes | Prevents 404 on unmatched slots |

---

## Pages

```tsx
// app/page.tsx — renders at /
export default function Home() {
  return <h1>Home</h1>
}

// app/about/page.tsx — renders at /about
export default function About() {
  return <h1>About</h1>
}
```

### Page Props

Pages receive `params` and `searchParams` as promises:

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>
}) {
  const { slug } = await params
  const { q } = await searchParams
  // ...
}
```

---

## Layouts

Layouts wrap child routes and **persist across navigations** (no re-render, state preserved).

```tsx
// app/layout.tsx — Root layout (REQUIRED)
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

// app/dashboard/layout.tsx — Nested layout for /dashboard/*
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <nav>Sidebar</nav>
      <main>{children}</main>
    </div>
  )
}
```

### Layout vs Template

- **Layout**: Mounts once, persists. State preserved. Use for sidebars, navs.
- **Template**: Re-mounts on every navigation. Use when you need fresh useEffect/animations per page.

---

## Dynamic Routes

```
app/blog/[slug]/page.tsx       → /blog/hello-world     params: { slug: 'hello-world' }
app/shop/[...slug]/page.tsx    → /shop/a/b/c           params: { slug: ['a', 'b', 'c'] }
app/shop/[[...slug]]/page.tsx  → /shop OR /shop/a/b     params: { slug: undefined | ['a', 'b'] }
```

### generateStaticParams

Pre-render dynamic routes at build time:

```tsx
// app/blog/[slug]/page.tsx
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await getPost(slug)
  return <article>{post.title}</article>
}
```

### dynamicParams

```tsx
export const dynamicParams = true   // (default) serve unknown slugs on-demand
export const dynamicParams = false  // return 404 for slugs not in generateStaticParams
```

---

## Route Groups

Organize routes without affecting URL structure. Wrap folder name in parentheses:

```
app/
├── (marketing)/
│   ├── layout.tsx      ← marketing-specific layout
│   ├── page.tsx         ← /
│   └── about/page.tsx   ← /about
├── (dashboard)/
│   ├── layout.tsx      ← dashboard-specific layout
│   └── settings/page.tsx ← /settings
```

### Multiple Root Layouts

Each route group can have its own `layout.tsx` with `<html>` and `<body>`:

```
app/
├── (marketing)/layout.tsx    ← Root layout for marketing
├── (app)/layout.tsx          ← Root layout for app
```

---

## Parallel Routes

Render multiple pages simultaneously in the same layout using named slots (`@folder`):

```
app/dashboard/
├── layout.tsx
├── page.tsx
├── @analytics/page.tsx    ← slot: analytics
├── @team/page.tsx         ← slot: team
└── @team/default.tsx      ← fallback when team slot unmatched
```

```tsx
// app/dashboard/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode
  analytics: React.ReactNode
  team: React.ReactNode
}) {
  return (
    <div>
      {children}
      {analytics}
      {team}
    </div>
  )
}
```

---

## Intercepting Routes

Intercept a route to show it in a different context (e.g., modal overlay) while preserving the URL.

```
Convention:
(.)folder    — same level
(..)folder   — one level up
(..)(..)folder — two levels up
(...)folder  — from root
```

```
app/
├── feed/
│   ├── page.tsx              ← /feed
│   └── (..)photo/[id]/page.tsx ← intercepts /photo/[id] when navigating from /feed
├── photo/[id]/
│   └── page.tsx              ← /photo/[id] (direct access, full page)
```

---

## Navigation

### Link Component

```tsx
import Link from 'next/link'

<Link href="/about">About</Link>
<Link href={`/blog/${post.slug}`}>{post.title}</Link>
<Link href="/dashboard" prefetch={false}>Dashboard</Link>
```

### useRouter (Client Components)

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function NavigateButton() {
  const router = useRouter()
  return <button onClick={() => router.push('/dashboard')}>Go</button>
}
```

| Method | Purpose |
|--------|---------|
| `router.push(url)` | Navigate to URL (adds to history) |
| `router.replace(url)` | Navigate without adding to history |
| `router.back()` | Go back |
| `router.forward()` | Go forward |
| `router.refresh()` | Re-render current route from server |
| `router.prefetch(url)` | Prefetch route for faster navigation |

### redirect (Server-side)

```tsx
import { redirect } from 'next/navigation'

// In Server Components, Server Actions, Route Handlers
redirect('/login') // throws internally — no code runs after this
```

### usePathname, useSearchParams

```tsx
'use client'
import { usePathname, useSearchParams } from 'next/navigation'

export function Breadcrumb() {
  const pathname = usePathname()       // '/blog/hello'
  const searchParams = useSearchParams() // URLSearchParams
  const query = searchParams.get('q')
}
```
