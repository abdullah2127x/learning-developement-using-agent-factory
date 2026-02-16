# Next.js App Router Patterns

## Import Strategy

### Server Components (No "use client" Needed)

```tsx
// Use motion/react-client for motion components in Server Components
import * as motion from "motion/react-client"

export default function HeroSection() {
  return (
    <motion.h1
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      Welcome
    </motion.h1>
  )
}
```

This works for **declarative animations only** (animate, initial, whileInView, layout). No hooks, no gestures, no event handlers.

### Client Components (Full API)

```tsx
"use client"
import { motion, AnimatePresence, useScroll, useTransform } from "motion/react"

export default function InteractiveWidget() {
  // Full API available: hooks, gestures, event handlers
  const { scrollYProgress } = useScroll()
  return <motion.div whileHover={{ scale: 1.05 }} />
}
```

### Decision: Which Import?

| Need | Import | Directive |
|------|--------|-----------|
| Static animations (animate, initial, whileInView) | `import * as motion from "motion/react-client"` | None needed |
| Hooks (useScroll, useAnimate, etc.) | `import { ... } from "motion/react"` | `"use client"` |
| Gestures (whileHover, whileTap, drag) | `import { motion } from "motion/react"` | `"use client"` |
| Event handlers (onHoverStart, onTap) | `import { motion } from "motion/react"` | `"use client"` |
| AnimatePresence | `import { AnimatePresence } from "motion/react"` | `"use client"` |

## Component Architecture

### Thin Client Wrapper Pattern

Keep Server Components for data fetching, push animation into thin client wrappers:

```tsx
// components/motion/fade-in.tsx
"use client"
import { motion, type HTMLMotionProps } from "motion/react"

interface FadeInProps extends HTMLMotionProps<"div"> {
  delay?: number
  direction?: "up" | "down" | "left" | "right"
  distance?: number
}

export function FadeIn({
  delay = 0,
  direction = "up",
  distance = 30,
  children,
  ...props
}: FadeInProps) {
  const axis = direction === "left" || direction === "right" ? "x" : "y"
  const value = direction === "right" || direction === "down" ? distance : -distance

  return (
    <motion.div
      initial={{ opacity: 0, [axis]: value }}
      whileInView={{ opacity: 1, [axis]: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      {...props}
    >
      {children}
    </motion.div>
  )
}
```

```tsx
// app/page.tsx — Server Component
import { FadeIn } from "@/components/motion/fade-in"

export default async function Page() {
  const data = await fetchData()  // Server-side data fetching

  return (
    <main>
      <FadeIn>
        <h1>{data.title}</h1>
      </FadeIn>
      <FadeIn delay={0.2} direction="left">
        <p>{data.description}</p>
      </FadeIn>
    </main>
  )
}
```

### Reusable Animation Wrapper Components

```tsx
// components/motion/scroll-reveal.tsx
"use client"
import { motion, type Variants } from "motion/react"

interface ScrollRevealProps {
  children: React.ReactNode
  className?: string
  delay?: number
  once?: boolean
}

export function ScrollReveal({ children, className, delay = 0, once = true }: ScrollRevealProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once, amount: 0.2 }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}
```

```tsx
// components/motion/stagger-list.tsx
"use client"
import { motion } from "motion/react"

interface StaggerListProps {
  children: React.ReactNode[]
  className?: string
  staggerDelay?: number
}

export function StaggerList({ children, className, staggerDelay = 0.08 }: StaggerListProps) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: staggerDelay } },
      }}
    >
      {children.map((child, i) => (
        <motion.div
          key={i}
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 },
          }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}
```

## Page Transitions

### Using template.tsx (Enter Animations Only)

```tsx
// app/template.tsx — re-mounts on every navigation
"use client"
import { motion } from "motion/react"

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  )
}
```

**Limitation**: `template.tsx` only supports enter animations. For exit animations, use AnimatePresence.

### Using AnimatePresence (Enter + Exit)

```tsx
// components/page-transition.tsx
"use client"
import { AnimatePresence, motion } from "motion/react"
import { usePathname } from "next/navigation"

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait" onExitComplete={() => window.scrollTo(0, 0)}>
      <motion.main
        key={pathname}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.25 }}
      >
        {children}
      </motion.main>
    </AnimatePresence>
  )
}
```

```tsx
// app/layout.tsx
import { PageTransition } from "@/components/page-transition"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        <PageTransition>{children}</PageTransition>
      </body>
    </html>
  )
}
```

**Caveat**: Next.js App Router doesn't natively support exit animations for route changes — `AnimatePresence` with `usePathname` may not always detect the old content before unmounting. For reliable exit animations, consider keeping route state in the client.

## SSR & Hydration

### Avoid Hydration Mismatches

```tsx
// BAD: Random values cause hydration mismatch
<motion.div initial={{ x: Math.random() * 100 }} />

// GOOD: Use fixed initial values
<motion.div initial={{ x: 0 }} animate={{ x: targetX }} />

// GOOD: Skip initial animation on server
<motion.div initial={false} animate={{ opacity: 1 }} />
```

### Lazy Motion (Reduce Bundle Size)

```tsx
// For apps where not every page uses animations
import { LazyMotion, domAnimation, m } from "motion/react"

// Wrap the app (or a section) with LazyMotion
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <LazyMotion features={domAnimation}>
      {children}
    </LazyMotion>
  )
}

// Use m.div instead of motion.div (tree-shakeable)
function Component() {
  return <m.div animate={{ opacity: 1 }} />
}
```

`domAnimation` includes: `animate`, `exit`, `variants`, `whileInView`, `whileHover`, `whileTap`, `whileFocus`, `whileDrag`, `drag`, `layout`, `layoutId`.

For full features including `AnimatePresence`, use `domMax`:

```tsx
import { LazyMotion, domMax } from "motion/react"
```

## Performance

### Animate Transform Properties

```tsx
// GOOD: GPU-accelerated (no layout thrash)
animate={{ x: 100, y: 50, scale: 1.2, rotate: 45, opacity: 0.5 }}

// AVOID: Causes layout recalculation
animate={{ width: "200px", height: "100px", top: "50px", left: "100px" }}
// Exception: layout prop handles these via FLIP
```

### Use MotionValues for Continuous Updates

```tsx
// GOOD: MotionValues update outside React — no re-renders
const x = useMotionValue(0)
<motion.div style={{ x }} />

// BAD: State causes re-render on every frame
const [x, setX] = useState(0)
<motion.div animate={{ x }} />
```

### viewport={{ once: true }}

```tsx
// GOOD: Stops observing after first trigger
<motion.div whileInView={{ opacity: 1 }} viewport={{ once: true }} />

// CONSIDER: Only use once:false when re-trigger is intentional
```

### layoutDependency

```tsx
// GOOD: Only measure layout when isOpen changes
<motion.div layout layoutDependency={isOpen} />

// DEFAULT: Measures on every render (can be expensive)
<motion.div layout />
```

## Accessibility

### Always Respect Reduced Motion

```tsx
// Global approach: In your root layout
"use client"
import { MotionConfig } from "motion/react"

export function AnimationProvider({ children }: { children: React.ReactNode }) {
  return (
    <MotionConfig reducedMotion="user">
      {children}
    </MotionConfig>
  )
}
```

`reducedMotion` options:
- `"user"` — Respect OS setting (animations become instant)
- `"never"` — Always animate (default)
- `"always"` — Always reduce motion

### Per-Component Approach

```tsx
import { useReducedMotion } from "motion/react"

function HeroAnimation() {
  const prefersReduced = useReducedMotion()

  if (prefersReduced) {
    return <div style={{ opacity: 1 }}>Content</div>  // No animation
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 100, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", duration: 1 }}
    >
      Content
    </motion.div>
  )
}
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `import { motion } from "motion/react"` in Server Component | Build error — hooks need client | Use `import * as motion from "motion/react-client"` or add `"use client"` |
| `whileHover` in Server Component | Gestures need event listeners (client) | Move to client component |
| `animate={{ width }}` with state on every frame | Re-renders every frame | Use `useMotionValue` + `useTransform` |
| Missing `key` on AnimatePresence children | Exit animations won't play | Always add unique `key` |
| `layout` on element inside non-`layoutScroll` scrollable | Layout position jumps | Add `layoutScroll` to scrollable parent |
| `Math.random()` in `initial` | Hydration mismatch | Use deterministic values or `initial={false}` |
| Large `whileInView` animations without `viewport={{ once: true }}` | Continuous IntersectionObserver overhead | Add `once: true` for one-shot animations |
| Setting `will-change` manually | Motion manages this automatically | Remove manual `will-change` |
| `motion.div` with `position: fixed` children that use `layout` | Layout calculations wrong | Use `layoutRoot` on fixed container |
| Not wrapping AnimatePresence `popLayout` custom components in `forwardRef` | Exit animations fail | Use `React.forwardRef` on direct children |

## TypeScript

### Motion Component Props

```tsx
import { type HTMLMotionProps, type SVGMotionProps } from "motion/react"

// HTML element props
type DivMotionProps = HTMLMotionProps<"div">
type ButtonMotionProps = HTMLMotionProps<"button">

// SVG element props
type PathMotionProps = SVGMotionProps<"path">

// Custom component with motion props
interface AnimatedCardProps extends HTMLMotionProps<"div"> {
  title: string
  delay?: number
}

function AnimatedCard({ title, delay = 0, ...motionProps }: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      {...motionProps}
    >
      <h3>{title}</h3>
    </motion.div>
  )
}
```

### Variant Typing

```tsx
import { type Variants } from "motion/react"

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  hover: { scale: 1.02, boxShadow: "0 10px 30px rgba(0,0,0,0.1)" },
}
```

### MotionValue Typing

```tsx
import { type MotionValue } from "motion/react"

interface ParallaxProps {
  offset: MotionValue<number>
  children: React.ReactNode
}
```
