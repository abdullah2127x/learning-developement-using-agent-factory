# Route Handlers, Proxy/Middleware & Authentication

## Route Handlers (API Routes)

Create API endpoints using `route.ts` in the `app/` directory.

### Basic Pattern

```tsx
// app/api/hello/route.ts
export async function GET() {
  return Response.json({ message: 'Hello World' })
}
```

### Supported HTTP Methods

```tsx
export async function GET(request: Request) {}
export async function POST(request: Request) {}
export async function PUT(request: Request) {}
export async function PATCH(request: Request) {}
export async function DELETE(request: Request) {}
export async function HEAD(request: Request) {}
export async function OPTIONS(request: Request) {} // Auto-implemented if omitted
```

### Request Handling

```tsx
import { type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  // Query params
  const query = request.nextUrl.searchParams.get('q')

  // Headers
  const auth = request.headers.get('authorization')

  // Cookies
  const token = request.cookies.get('token')

  return Response.json({ query, auth: !!auth })
}

export async function POST(request: Request) {
  // JSON body
  const body = await request.json()

  // FormData body
  const formData = await request.formData()

  return Response.json({ received: true })
}
```

### Dynamic Route Handlers

```tsx
// app/api/users/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const user = await db.user.findUnique({ where: { id } })

  if (!user) return Response.json({ error: 'Not found' }, { status: 404 })
  return Response.json(user)
}
```

### CORS

```tsx
export async function GET(request: Request) {
  return new Response('OK', {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  })
}
```

### Streaming Responses

```tsx
export async function GET() {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      controller.enqueue(encoder.encode('chunk 1\n'))
      await new Promise(r => setTimeout(r, 1000))
      controller.enqueue(encoder.encode('chunk 2\n'))
      controller.close()
    },
  })
  return new Response(stream)
}
```

### Caching Route Handlers

```tsx
// Static (cached at build time) — only GET with no dynamic input
export const revalidate = 3600

export async function GET() {
  const data = await fetch('https://api.example.com/data')
  return Response.json(await data.json())
}
```

### Cookies & Headers via next/headers

```tsx
import { cookies, headers } from 'next/headers'

export async function GET() {
  const cookieStore = await cookies()
  const token = cookieStore.get('token')

  const headersList = await headers()
  const referer = headersList.get('referer')

  return Response.json({ hasToken: !!token, referer })
}
```

---

## Proxy (formerly Middleware)

> **Note**: In Next.js 16+, `middleware.ts` is renamed to `proxy.ts`. Both work currently.

Runs before every matched request. Use for auth checks, redirects, headers, geolocation.

### Setup

Create `proxy.ts` (or `middleware.ts`) at the **project root** (same level as `app/`):

```tsx
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // Check auth
  const token = request.cookies.get('session')
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

### Matcher Patterns

```tsx
export const config = {
  // Single path
  matcher: '/about',

  // Multiple paths
  matcher: ['/about', '/dashboard/:path*'],

  // Regex: exclude static files and API
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],

  // Conditional matching
  matcher: [{
    source: '/api/:path*',
    has: [{ type: 'header', key: 'Authorization' }],
  }],
}
```

### Common Middleware Patterns

**Redirect based on geo/locale:**
```tsx
export function proxy(request: NextRequest) {
  const country = request.geo?.country || 'US'
  if (country === 'DE') {
    return NextResponse.redirect(new URL('/de', request.url))
  }
  return NextResponse.next()
}
```

**Set headers:**
```tsx
export function proxy(request: NextRequest) {
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-request-id', crypto.randomUUID())

  return NextResponse.next({
    request: { headers: requestHeaders },
  })
}
```

**Rate limiting response:**
```tsx
export function proxy(request: NextRequest) {
  if (isRateLimited(request)) {
    return Response.json(
      { error: 'Too many requests' },
      { status: 429 }
    )
  }
  return NextResponse.next()
}
```

### Middleware Best Practices

- Keep middleware **thin** — it runs on every matched request
- Don't do heavy computation or database queries
- Use for: auth redirects, headers, rewrites, geolocation
- Don't use for: data fetching, complex business logic

---

## Authentication Patterns

### Session-Based (Cookies)

```tsx
// lib/auth.ts
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export async function getSession() {
  const cookieStore = await cookies()
  const session = cookieStore.get('session')?.value
  if (!session) return null

  // Verify session (JWT decode, DB lookup, etc.)
  return verifySession(session)
}

export async function requireAuth() {
  const session = await getSession()
  if (!session) redirect('/login')
  return session
}
```

**In a page:**
```tsx
import { requireAuth } from '@/lib/auth'

export default async function DashboardPage() {
  const session = await requireAuth() // Redirects if not authed
  return <h1>Welcome, {session.user.name}</h1>
}
```

**In middleware (protect routes):**
```tsx
export function proxy(request: NextRequest) {
  const session = request.cookies.get('session')
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard')

  if (isProtected && !session) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}
```

### Login/Logout Server Actions

```tsx
'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

export async function login(formData: FormData) {
  const email = formData.get('email') as string
  const password = formData.get('password') as string

  const user = await authenticateUser(email, password)
  if (!user) return { error: 'Invalid credentials' }

  const session = await createSession(user.id)
  const cookieStore = await cookies()
  cookieStore.set('session', session.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 1 week
    path: '/',
  })

  redirect('/dashboard')
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete('session')
  redirect('/login')
}
```

### Auth Libraries

Popular options: **NextAuth.js (Auth.js)**, **Clerk**, **Lucia**, **Supabase Auth**.

Each has its own setup but follows the same pattern:
1. Session check in middleware for protected routes
2. `getSession()` helper for pages/actions
3. Login/logout via Server Actions or API routes
4. Cookie-based session storage (httpOnly, secure)

---

## Webhooks

```tsx
// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers'

export async function POST(request: Request) {
  const body = await request.text()
  const headersList = await headers()
  const signature = headersList.get('stripe-signature')

  try {
    const event = stripe.webhooks.constructEvent(body, signature!, webhookSecret)
    // Process event...
    return Response.json({ received: true })
  } catch (err) {
    return Response.json({ error: 'Invalid signature' }, { status: 400 })
  }
}
```
