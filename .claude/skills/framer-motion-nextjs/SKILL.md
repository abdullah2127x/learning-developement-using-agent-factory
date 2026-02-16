---
name: framer-motion-nextjs
description: |
  Comprehensive guide for building animations with Motion (Framer Motion) in Next.js
  App Router with TypeScript. This skill should be used when users need to create
  motion components, variants, gesture animations, scroll-triggered effects, layout
  animations, shared element transitions, exit animations, page transitions, or
  production-ready animation patterns with accessibility support.
---

# Framer Motion + Next.js Animation Guide

## Mental Model

```
motion component → animate prop (WHAT to animate)
                 → transition prop (HOW to animate: spring/tween/inertia)
                 → variants (named states + orchestration)
                 → gestures (whileHover/whileTap/whileDrag)
                 → scroll (whileInView / useScroll)
                 → layout (layout prop / layoutId shared transitions)
                 → exit (AnimatePresence + exit prop)
```

## Package & Import (Motion v11+)

```bash
npm install motion
```

```tsx
// Standard React
import { motion, AnimatePresence } from "motion/react"

// Next.js App Router — optimized (no "use client" needed)
import * as motion from "motion/react-client"

// Hooks (always from "motion/react")
import { useAnimate, useScroll, useTransform, useMotionValue,
         useSpring, useInView, useReducedMotion, stagger } from "motion/react"
```

**Key**: `motion/react-client` exports motion components that work without `"use client"` directive. Hooks still need a client component.

## Quick Decision Trees

### Which Animation Approach?

```
Simple prop change?     → animate={{ opacity: 1 }}
Multiple named states?  → variants={{ visible: {...}, hidden: {...} }}
Imperative/sequence?    → useAnimate() hook
Scroll-linked value?    → useScroll() + useTransform()
Gesture response?       → whileHover / whileTap / whileDrag
Enter/exit DOM?         → AnimatePresence + exit prop
Layout reflow?          → layout prop or layoutId
```

### Which Transition Type?

```
Smooth physical feel?   → type: "spring" (default for transforms)
Precise timing?         → type: "tween" + duration + ease
Gesture deceleration?   → type: "inertia"
Multi-step?             → keyframes array in animate
```

### Next.js Component Boundary?

```
Static animation (no interaction)?  → import * as motion from "motion/react-client"
Interactive (gestures, hooks)?      → "use client" + import { motion } from "motion/react"
Page transitions?                   → Client layout wrapper with AnimatePresence
```

## Core Props Reference

| Prop | Purpose | Example |
|------|---------|---------|
| `animate` | Target state | `animate={{ opacity: 1, x: 0 }}` |
| `initial` | Starting state (or `false` to skip) | `initial={{ opacity: 0 }}` |
| `exit` | Leave state (needs AnimatePresence) | `exit={{ opacity: 0 }}` |
| `transition` | Timing/physics | `transition={{ type: "spring", damping: 20 }}` |
| `variants` | Named animation states | `variants={{ open: {...}, closed: {...} }}` |
| `whileHover` | Hover target | `whileHover={{ scale: 1.05 }}` |
| `whileTap` | Press target | `whileTap={{ scale: 0.95 }}` |
| `whileDrag` | Drag target | `whileDrag={{ backgroundColor: "#f00" }}` |
| `whileInView` | Viewport target | `whileInView={{ opacity: 1 }}` |
| `whileFocus` | Focus target | `whileFocus={{ borderColor: "#00f" }}` |
| `layout` | Animate layout changes | `layout` or `layout="position"` |
| `layoutId` | Shared element transition | `layoutId="hero-image"` |
| `drag` | Enable dragging | `drag` or `drag="x"` |
| `viewport` | InView options | `viewport={{ once: true, amount: 0.5 }}` |
| `custom` | Data for dynamic variants | `custom={index}` |

## File Structure (Next.js App Router)

```
components/
├── motion/                    # Animation building blocks
│   ├── fade-in.tsx           # Reusable fade-in wrapper
│   ├── stagger-list.tsx      # Staggered list animation
│   ├── page-transition.tsx   # Page transition wrapper
│   └── scroll-reveal.tsx     # Scroll-triggered reveal
├── ui/                        # UI components using motion
│   └── animated-card.tsx
lib/
└── motion/
    └── variants.ts           # Shared variant definitions
app/
└── layout.tsx                # AnimatePresence for page transitions
```

## Production Checklist

- [ ] All motion components in client components (`"use client"`) or use `motion/react-client`
- [ ] `AnimatePresence` wraps conditionally rendered elements
- [ ] `key` prop on elements inside AnimatePresence
- [ ] `useReducedMotion` respected for large/parallax animations
- [ ] `viewport={{ once: true }}` for one-shot scroll reveals (performance)
- [ ] `layoutScroll` on scrollable parents of layout-animated children
- [ ] No layout animations in Edge Runtime or Server Components
- [ ] `will-change` not manually set (Motion handles it)
- [ ] Exit animations use `mode="wait"` when sequential transitions needed

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing animation patterns, CSS transitions to replace, component structure |
| **Conversation** | User's specific animation requirements, interaction patterns |
| **Skill References** | Domain patterns from `references/` (API docs, examples, best practices) |
| **User Guidelines** | Performance budgets, accessibility requirements, browser support |

Ensure all required context is gathered before implementing.

## Reference Files

| File | When to Read |
|------|--------------|
| `references/motion-components.md` | Core animate/initial/exit/transition/variants API |
| `references/gestures-interactions.md` | Hover, tap, drag, focus, pan gestures |
| `references/scroll-animations.md` | useScroll, whileInView, parallax, scroll progress |
| `references/layout-animations.md` | layout prop, layoutId, AnimatePresence, page transitions |
| `references/hooks-utilities.md` | useAnimate, useMotionValue, useTransform, useSpring, stagger |
| `references/nextjs-patterns.md` | Client boundaries, SSR, page transitions, performance, a11y |
