# Hooks & Utilities

## useAnimate

Imperative animation control — animate any element, create sequences, and control playback:

```tsx
"use client"
import { useAnimate, stagger } from "motion/react"

function Component() {
  const [scope, animate] = useAnimate()

  async function handleClick() {
    // Animate the scope element
    await animate(scope.current, { scale: 1.2 }, { duration: 0.3 })

    // Animate children using CSS selectors (scoped to scope ref)
    await animate("li", { opacity: 1, y: 0 }, { delay: stagger(0.1) })
  }

  return (
    <ul ref={scope}>
      <li style={{ opacity: 0, transform: "translateY(20px)" }} />
      <li style={{ opacity: 0, transform: "translateY(20px)" }} />
      <li style={{ opacity: 0, transform: "translateY(20px)" }} />
      <button onClick={handleClick}>Animate</button>
    </ul>
  )
}
```

### Animation Sequences

```tsx
const [scope, animate] = useAnimate()

useEffect(() => {
  const controls = animate([
    // [selector/element, target, options]
    [scope.current, { opacity: 1 }, { duration: 0.3 }],
    ["h1", { y: 0 }, { duration: 0.5, at: "<" }],     // "<" = start with previous
    ["p", { opacity: 1 }, { duration: 0.3, at: "+0.2" }], // "+0.2" = 0.2s after previous ends
    ["button", { scale: 1 }, { duration: 0.2, at: 0.8 }], // absolute time
  ])

  return () => controls.stop()
}, [])
```

### Playback Controls

```tsx
const [scope, animate] = useAnimate()

useEffect(() => {
  const controls = animate(scope.current, { x: 100 }, { duration: 2 })

  controls.speed = 0.5       // Slow motion
  controls.time = 0          // Seek to start
  controls.pause()           // Pause
  controls.play()            // Resume
  controls.stop()            // Stop and cleanup
  controls.cancel()          // Cancel without committing

  return () => controls.stop()
}, [])
```

### Animate Function Signature

```tsx
// Element animation
animate(element, keyframes, options?)

// Selector animation (scoped to scope ref)
animate("li", keyframes, options?)

// Sequence animation
animate([
  [target, keyframes, options],
  [target, keyframes, options],
])

// Value animation
animate(0, 100, {
  duration: 1,
  onUpdate: (latest) => console.log(latest),
})
```

## useMotionValue

Create reactive animation values that don't trigger re-renders:

```tsx
"use client"
import { useMotionValue, motion } from "motion/react"

function Component() {
  const x = useMotionValue(0)

  return <motion.div style={{ x }} drag="x" />
}
```

### Manual Updates

```tsx
const x = useMotionValue(0)

// Set instantly (no animation)
x.set(100)

// Get current value
const current = x.get()

// Jump to value (reset velocity to 0)
x.jump(200)
```

### Key Principle

MotionValues update **outside React's render cycle** — changing them doesn't cause re-renders. This makes them performant for continuous animations like drag and scroll.

## useMotionValueEvent

Subscribe to MotionValue events without manual cleanup:

```tsx
import { useMotionValueEvent, useMotionValue } from "motion/react"

function Component() {
  const x = useMotionValue(0)

  useMotionValueEvent(x, "change", (latest) => {
    console.log("x changed to", latest)
  })

  useMotionValueEvent(x, "animationStart", () => {
    console.log("Animation started on x")
  })

  useMotionValueEvent(x, "animationComplete", () => {
    console.log("Animation complete on x")
  })

  return <motion.div style={{ x }} drag="x" />
}
```

Available events: `"change"`, `"animationStart"`, `"animationComplete"`, `"animationCancel"`

## useTransform

Derive new MotionValues from existing ones:

```tsx
import { useMotionValue, useTransform, motion } from "motion/react"

function Component() {
  const x = useMotionValue(0)

  // Range mapping: as x goes from -200→200, opacity goes from 0→1→0
  const opacity = useTransform(x, [-200, 0, 200], [0, 1, 0])

  // Scale from drag
  const scale = useTransform(x, [-200, 200], [0.5, 1.5])

  // Custom function
  const backgroundColor = useTransform(x, (value) =>
    value > 0 ? "#22c55e" : "#ef4444"
  )

  return (
    <motion.div drag="x" style={{ x, opacity, scale, backgroundColor }} />
  )
}
```

### Multiple Input Values

```tsx
const x = useMotionValue(0)
const y = useMotionValue(0)

// Combine multiple motion values
const rotate = useTransform([x, y], ([latestX, latestY]) =>
  latestX * 0.1 + latestY * 0.1
)
```

### Clamping

```tsx
// By default, output values are clamped to the output range
const opacity = useTransform(progress, [0, 1], [0, 1])

// Disable clamping to allow values outside the output range
const y = useTransform(progress, [0, 1], [0, -200], { clamp: false })
```

## useSpring

Create a spring-animated MotionValue:

```tsx
import { useSpring, useMotionValue, motion } from "motion/react"

function Component() {
  const x = useMotionValue(0)

  // springX smoothly follows x with spring physics
  const springX = useSpring(x, {
    stiffness: 300,
    damping: 20,
    mass: 0.5,
  })

  return <motion.div style={{ x: springX }} />
}
```

### From a Number

```tsx
const springValue = useSpring(0, { stiffness: 100, damping: 30 })

// Later:
springValue.set(100)  // Animates to 100 with spring physics
```

### Smooth Scroll Progress

```tsx
const { scrollYProgress } = useScroll()
const smoothProgress = useSpring(scrollYProgress, {
  stiffness: 100,
  damping: 30,
  restDelta: 0.001,
})
```

## useInView

Track whether an element is in the viewport:

```tsx
import { useRef } from "react"
import { useInView } from "motion/react"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, {
    once: true,                // Only detect first entry
    margin: "-100px",          // Shrink viewport detection
    amount: "some",            // "some" | "all" | 0-1
    root: containerRef,        // Custom scroll ancestor
  })

  return (
    <div ref={ref} style={{ opacity: isInView ? 1 : 0 }}>
      Content
    </div>
  )
}
```

## useReducedMotion

Respect user's reduced motion preference:

```tsx
import { useReducedMotion } from "motion/react"

function Component() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      animate={shouldReduceMotion
        ? { opacity: 1 }                           // Simple fade only
        : { opacity: 1, x: 0, scale: 1 }           // Full animation
      }
      initial={shouldReduceMotion
        ? { opacity: 0 }
        : { opacity: 0, x: -100, scale: 0.8 }
      }
    />
  )
}
```

### For Parallax / Large Motions

```tsx
function ParallaxImage() {
  const shouldReduceMotion = useReducedMotion()
  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 1], [0, -200])

  return (
    <motion.img
      style={{ y: shouldReduceMotion ? 0 : y }}
      src="/hero.jpg"
      alt="Hero"
    />
  )
}
```

### For Auto-playing Media

```tsx
function BackgroundVideo() {
  const shouldReduceMotion = useReducedMotion()
  return <video autoPlay={!shouldReduceMotion} loop muted />
}
```

## stagger

Creates staggered delays for child animations:

```tsx
import { stagger } from "motion/react"

// With variants
const container = {
  visible: {
    transition: {
      delayChildren: stagger(0.1),          // 0.1s between each child
    },
  },
}

// With stagger options
const containerReverse = {
  visible: {
    transition: {
      delayChildren: stagger(0.1, {
        from: "last",       // "first" | "last" | "center" | number (index)
      }),
    },
  },
}

// With useAnimate
const [scope, animate] = useAnimate()
animate("li", { opacity: 1 }, { delay: stagger(0.05) })
animate("li", { opacity: 1 }, { delay: stagger(0.05, { from: "center" }) })
```

## Reusable Variant Library

```tsx
// lib/motion/variants.ts

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.5 } },
}

export const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
}

export const fadeInLeft = {
  hidden: { opacity: 0, x: -30 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.5, ease: "easeOut" } },
}

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1, transition: { type: "spring", stiffness: 200 } },
}

export const staggerContainer = (staggerDelay = 0.1) => ({
  hidden: {},
  visible: { transition: { staggerChildren: staggerDelay } },
})

export const slideIn = (direction: "left" | "right" | "up" | "down", distance = 50) => {
  const axis = direction === "left" || direction === "right" ? "x" : "y"
  const value = direction === "right" || direction === "down" ? distance : -distance
  return {
    hidden: { opacity: 0, [axis]: value },
    visible: { opacity: 1, [axis]: 0, transition: { type: "spring", damping: 20 } },
  }
}
```

Usage:

```tsx
import { fadeInUp, staggerContainer } from "@/lib/motion/variants"

<motion.ul variants={staggerContainer(0.08)} initial="hidden" whileInView="visible">
  {items.map((item) => (
    <motion.li key={item.id} variants={fadeInUp}>{item.name}</motion.li>
  ))}
</motion.ul>
```
