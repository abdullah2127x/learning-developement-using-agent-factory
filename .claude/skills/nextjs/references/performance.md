# Performance, SEO & Optimization

## Images (next/image)

```tsx
import Image from 'next/image'

// With known dimensions
<Image src="/hero.jpg" alt="Hero" width={1200} height={600} priority />

// Fill container
<Image src="/hero.jpg" alt="Hero" fill className="object-cover" />

// External images — must configure in next.config
<Image src="https://cdn.example.com/photo.jpg" alt="" width={400} height={300} />
```

### next.config.js for external images

```js
module.exports = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com' },
    ],
  },
}
```

### Key Props

| Prop | Purpose |
|------|---------|
| `priority` | Preload (use for above-the-fold LCP image) |
| `fill` | Fill parent container (parent needs `position: relative`) |
| `sizes` | Responsive size hints (e.g., `"(max-width: 768px) 100vw, 50vw"`) |
| `placeholder="blur"` | Show blur placeholder while loading |
| `quality` | 1-100 (default 75) |
| `loading="lazy"` | Default behavior — use `priority` to override |

---

## Fonts (next/font)

Zero layout shift, self-hosted, no external requests:

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

### Local Fonts

```tsx
import localFont from 'next/font/local'

const myFont = localFont({
  src: './fonts/MyFont.woff2',
  display: 'swap',
})
```

### Variable Fonts with Tailwind

```tsx
const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

// In layout:
<html className={inter.variable}>

// In tailwind.config.js:
fontFamily: { sans: ['var(--font-inter)'] }
```

---

## Metadata & SEO

### Static Metadata

```tsx
// app/layout.tsx or app/page.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'My App',
  description: 'A description of my app',
  openGraph: {
    title: 'My App',
    description: 'A description',
    images: ['/og-image.png'],
  },
}
```

### Dynamic Metadata

```tsx
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { images: [post.coverImage] },
  }
}
```

### Template Titles

```tsx
// app/layout.tsx — applies to all child pages
export const metadata: Metadata = {
  title: {
    template: '%s | My App',   // %s replaced by child page title
    default: 'My App',
  },
}

// app/about/page.tsx
export const metadata: Metadata = {
  title: 'About',  // Renders as "About | My App"
}
```

### Sitemap & Robots

```tsx
// app/sitemap.ts
export default async function sitemap() {
  const posts = await getPosts()
  return [
    { url: 'https://example.com', lastModified: new Date() },
    ...posts.map(post => ({
      url: `https://example.com/blog/${post.slug}`,
      lastModified: post.updatedAt,
    })),
  ]
}

// app/robots.ts
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: '/api/' },
    sitemap: 'https://example.com/sitemap.xml',
  }
}
```

---

## Bundle Size Optimization

### 1. Keep 'use client' Boundaries Deep

```
BAD:  Mark entire page as 'use client'
GOOD: Mark only the interactive button/form component
```

### 2. Dynamic Imports (Lazy Loading)

```tsx
import dynamic from 'next/dynamic'

// Only load heavy component when needed
const HeavyChart = dynamic(() => import('./chart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Skip SSR for client-only components
})
```

### 3. Tree Shaking

Import specific functions, not entire libraries:

```tsx
// BAD
import _ from 'lodash'
_.debounce(...)

// GOOD
import debounce from 'lodash/debounce'
debounce(...)
```

### 4. Analyze Bundle

```bash
ANALYZE=true next build  # with @next/bundle-analyzer configured
```

```js
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
module.exports = withBundleAnalyzer({ /* config */ })
```

---

## Static vs Dynamic Rendering

| Rendering | When | Cache |
|-----------|------|-------|
| **Static** | No dynamic data, no request-time info | Cached at build time |
| **Dynamic** | Uses `cookies()`, `headers()`, `searchParams`, uncached fetch | Rendered per request |

### Force Static/Dynamic

```tsx
export const dynamic = 'force-static'   // Always static
export const dynamic = 'force-dynamic'  // Always dynamic
export const dynamic = 'auto'           // Default — Next.js decides
```

---

## Script Optimization

```tsx
import Script from 'next/script'

// Load after page is interactive (default)
<Script src="https://analytics.example.com/script.js" strategy="afterInteractive" />

// Load before page hydration
<Script src="/critical.js" strategy="beforeInteractive" />

// Load in web worker (offload from main thread)
<Script src="/heavy-analytics.js" strategy="worker" />

// Lazy load when idle
<Script src="/non-critical.js" strategy="lazyOnload" />
```

---

## Core Web Vitals Tips

| Metric | Optimize With |
|--------|---------------|
| **LCP** | `priority` on hero image, avoid layout shifts, stream content |
| **FID/INP** | Keep client JS minimal, use Server Components, `dynamic()` imports |
| **CLS** | `next/image` (explicit dimensions), `next/font` (no FOUT), fixed containers |

---

## Production Config

```js
// next.config.js
module.exports = {
  // Strict mode for catching issues
  reactStrictMode: true,

  // Output standalone for Docker
  output: 'standalone',

  // Compress responses
  compress: true,

  // Security headers
  async headers() {
    return [{
      source: '/:path*',
      headers: [
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
      ],
    }]
  },

  // Redirects
  async redirects() {
    return [
      { source: '/old-page', destination: '/new-page', permanent: true },
    ]
  },
}
```
