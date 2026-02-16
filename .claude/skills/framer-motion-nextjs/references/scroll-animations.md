# Scroll Animations

## whileInView (Declarative)

The simplest scroll animation — animate when element enters the viewport:

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
/>
```

### viewport Options

```tsx
<motion.section
  whileInView={{ opacity: 1 }}
  viewport={{
    once: true,             // Only trigger once (no re-animation on scroll back)
    root: scrollRef,        // Custom scrollable ancestor (default: window)
    margin: "0px 0px -100px 0px",  // Shrink/expand detection area
    amount: 0.5,            // 0-1: how much element must be visible
                            // "some" (default) | "all" | number
  }}
/>
```

### Viewport Events

```tsx
<motion.div
  whileInView={{ opacity: 1 }}
  onViewportEnter={(entry) => {
    console.log("Entered viewport", entry?.isIntersecting)
  }}
  onViewportLeave={(entry) => {
    console.log("Left viewport", entry?.intersectionRect)
  }}
/>
```

### whileInView with Variants (Staggered Scroll Reveal)

```tsx
const container = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
}

<motion.ul
  variants={container}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.3 }}
>
  {items.map((i) => (
    <motion.li key={i.id} variants={item}>{i.name}</motion.li>
  ))}
</motion.ul>
```

## useScroll Hook

Returns four MotionValues tracking scroll position and progress:

```tsx
import { useScroll } from "motion/react"

// Page scroll
const { scrollX, scrollY, scrollXProgress, scrollYProgress } = useScroll()

// scrollX / scrollY         → absolute pixel position
// scrollXProgress / scrollYProgress → 0 to 1 normalized progress
```

### Page Scroll Progress

```tsx
"use client"
import { motion, useScroll } from "motion/react"

function ScrollProgressBar() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        transformOrigin: "left",
        position: "fixed",
        top: 0, left: 0, right: 0,
        height: 4,
        backgroundColor: "#3b82f6",
        zIndex: 50,
      }}
    />
  )
}
```

### Element Scroll Progress

Track how far an element has scrolled through the viewport:

```tsx
"use client"
import { useRef } from "react"
import { useScroll, useTransform, motion } from "motion/react"

function RevealSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,                           // Element to track
    offset: ["start end", "end start"],    // [trigger start, trigger end]
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [0, 1])
  const y = useTransform(scrollYProgress, [0, 1], [100, 0])

  return (
    <motion.section ref={ref} style={{ opacity, y }}>
      Content reveals as you scroll
    </motion.section>
  )
}
```

### Container Scroll

Track scroll within a specific scrollable container:

```tsx
function ScrollableContainer() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    container: containerRef,   // The scrollable element
  })

  return (
    <div ref={containerRef} style={{ overflow: "auto", height: 400 }}>
      <motion.div style={{ opacity: scrollYProgress }}>
        Scrollable content
      </motion.div>
    </div>
  )
}
```

### offset Explained

The `offset` array defines when tracking starts and ends:

```tsx
// Format: ["<target> <container>", "<target> <container>"]
// target = the tracked element edge
// container = the viewport/container edge

offset: ["start end", "end start"]
//        ↑ tracking starts when element top hits viewport bottom
//                        ↑ tracking ends when element bottom hits viewport top

// Common offsets:
offset: ["start end", "end start"]       // Full element traverse (default)
offset: ["start start", "end start"]     // From top-aligned to bottom exits top
offset: ["start 0.8", "start 0.2"]       // Between 80% and 20% of viewport
offset: ["start end", "start start"]     // While element enters viewport
```

Edge values: `"start"` (top/left), `"end"` (bottom/right), `"center"`, or a number (0-1).

## useTransform

Maps one MotionValue range to another:

```tsx
import { useTransform } from "motion/react"

// Linear mapping
const opacity = useTransform(scrollYProgress, [0, 1], [0, 1])

// Non-linear mapping
const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 1.2])

// Custom transform function
const color = useTransform(scrollYProgress, (value) =>
  value > 0.5 ? "#ff0000" : "#0000ff"
)

// Clamp behavior (default: values clamp to output range)
const x = useTransform(scrollYProgress, [0, 1], [0, 200], { clamp: false })
```

### Chaining Transforms

```tsx
const { scrollYProgress } = useScroll()
const smoothProgress = useSpring(scrollYProgress, { damping: 20 })
const y = useTransform(smoothProgress, [0, 1], [0, -200])
```

## useInView Hook

Imperative alternative to `whileInView`:

```tsx
import { useInView } from "motion/react"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, {
    once: true,            // Trigger only once
    margin: "-100px",      // Shrink detection area
    amount: "some",        // "some" | "all" | number
    root: containerRef,    // Custom scroll ancestor
  })

  return (
    <div ref={ref} style={{ opacity: isInView ? 1 : 0 }}>
      {isInView ? "Visible!" : "Hidden"}
    </div>
  )
}
```

### useInView + useAnimate

```tsx
import { useAnimate, useInView } from "motion/react"
import { useEffect } from "react"

function AnimatedList() {
  const [scope, animate] = useAnimate()
  const isInView = useInView(scope, { once: true })

  useEffect(() => {
    if (isInView) {
      animate("li", { opacity: 1, y: 0 }, { delay: stagger(0.1) })
    }
  }, [isInView])

  return (
    <ul ref={scope}>
      <li style={{ opacity: 0, y: 20 }} />
      <li style={{ opacity: 0, y: 20 }} />
      <li style={{ opacity: 0, y: 20 }} />
    </ul>
  )
}
```

## Common Scroll Patterns

### Parallax

```tsx
"use client"
function Parallax({ speed = 0.5 }: { speed?: number }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })
  const y = useTransform(scrollYProgress, [0, 1], [-100 * speed, 100 * speed])

  return (
    <div ref={ref} style={{ overflow: "hidden" }}>
      <motion.div style={{ y }}>
        <img src="/hero.jpg" alt="Hero" />
      </motion.div>
    </div>
  )
}
```

### Horizontal Scroll Section

```tsx
"use client"
function HorizontalScroll({ children }: { children: React.ReactNode }) {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({ target: containerRef })
  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-75%"])

  return (
    <section ref={containerRef} style={{ height: "300vh", position: "relative" }}>
      <div style={{ position: "sticky", top: 0, overflow: "hidden", height: "100vh" }}>
        <motion.div style={{ x, display: "flex" }}>
          {children}
        </motion.div>
      </div>
    </section>
  )
}
```

### Scroll-Linked Background Color

```tsx
"use client"
function ColorShift() {
  const { scrollYProgress } = useScroll()
  const backgroundColor = useTransform(
    scrollYProgress,
    [0, 0.33, 0.66, 1],
    ["#ffffff", "#f0f9ff", "#ecfdf5", "#fef3c7"]
  )

  return <motion.div style={{ backgroundColor, minHeight: "100vh" }} />
}
```

### Scroll-Triggered Counter

```tsx
"use client"
function Counter({ target }: { target: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!isInView) return
    let current = 0
    const step = target / 60
    const timer = setInterval(() => {
      current += step
      if (current >= target) {
        setCount(target)
        clearInterval(timer)
      } else {
        setCount(Math.floor(current))
      }
    }, 16)
    return () => clearInterval(timer)
  }, [isInView, target])

  return <span ref={ref}>{count}</span>
}
```

### Section Reveal on Scroll

```tsx
const sectionVariants = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: "easeOut" },
  },
}

function ScrollReveal({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={sectionVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.2 }}
    >
      {children}
    </motion.div>
  )
}
```
