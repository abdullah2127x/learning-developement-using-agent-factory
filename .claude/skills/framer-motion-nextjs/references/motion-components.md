# Motion Components & Core Animation API

## The motion Component

Every HTML and SVG element has a `motion` counterpart that accepts animation props:

```tsx
import { motion } from "motion/react"

// Any HTML element
<motion.div />
<motion.span />
<motion.button />
<motion.img />
<motion.input />
<motion.nav />
<motion.section />

// SVG elements
<motion.svg />
<motion.path />
<motion.circle />
<motion.rect />
```

Use them exactly like normal elements — they accept all standard HTML/SVG attributes plus animation props.

## animate Prop

The primary animation prop. When values change, the component animates to the new target:

```tsx
// Simple animation
<motion.div animate={{ opacity: 1, x: 0 }} />

// Multiple properties
<motion.div animate={{ opacity: 1, scale: 1.2, rotate: 90 }} />

// Animatable CSS properties
<motion.div
  animate={{
    x: 100,              // translateX
    y: 50,               // translateY
    scale: 1.5,          // scale
    rotate: 180,         // rotate (degrees)
    opacity: 1,
    borderRadius: "50%",
    backgroundColor: "#ff0000",
    width: "200px",
    height: "200px",
  }}
/>
```

### Supported Value Types

```tsx
// Numbers
animate={{ x: 100, opacity: 0.5, rotate: 360 }}

// Strings with units
animate={{ width: "100%", height: "50vh", borderRadius: "12px" }}

// Colors (hex, rgb, hsl)
animate={{ backgroundColor: "#ff0000", color: "rgb(0, 255, 0)" }}

// Keyframes (array = multi-step)
animate={{ x: [0, 100, 50, 100] }}
animate={{ scale: [1, 1.5, 1], rotate: [0, 180, 360] }}
```

## initial Prop

Sets the starting state. Animation plays from `initial` → `animate`:

```tsx
// Fade in from left
<motion.div
  initial={{ opacity: 0, x: -50 }}
  animate={{ opacity: 1, x: 0 }}
/>

// Skip enter animation
<motion.div initial={false} animate={{ opacity: 0 }} />

// Use variant name
<motion.div initial="hidden" animate="visible" />

// Multiple variant names
<motion.div initial={["hidden", "small"]} animate={["visible", "large"]} />
```

## exit Prop

Animates when removed from the DOM. **Requires** `AnimatePresence` parent:

```tsx
import { motion, AnimatePresence } from "motion/react"

<AnimatePresence>
  {isVisible && (
    <motion.div
      key="modal"                    // key is required
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}  // plays on removal
    />
  )}
</AnimatePresence>
```

## transition Prop

Controls HOW the animation plays — timing, physics, easing:

```tsx
// Spring (default for transforms)
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>

// Tween (duration-based)
<motion.div
  animate={{ opacity: 1 }}
  transition={{ type: "tween", duration: 0.5, ease: "easeInOut" }}
/>

// Per-property transitions
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { type: "spring", stiffness: 300 },
    opacity: { duration: 0.3 },
  }}
/>
```

### Transition Types

#### Spring (Physics-Based)

```tsx
transition={{
  type: "spring",
  stiffness: 100,    // Higher = snappier (default: 100)
  damping: 10,       // Higher = less oscillation (default: 10)
  mass: 1,           // Higher = slower (default: 1)
  velocity: 0,       // Initial velocity
  restSpeed: 0.1,    // Stop threshold speed
  restDelta: 0.01,   // Stop threshold distance
}}

// Duration-based spring (easier to control)
transition={{
  type: "spring",
  duration: 0.8,     // Approximate duration
  bounce: 0.25,      // 0 = no bounce, 1 = maximum bounce
}}
```

#### Tween (Duration-Based)

```tsx
transition={{
  type: "tween",
  duration: 0.5,            // seconds
  ease: "easeInOut",        // named easing
  // or cubic bezier:
  ease: [0.42, 0, 0.58, 1],
  // or custom function:
  ease: (t) => t * t,
}}
```

Named easings: `"linear"`, `"easeIn"`, `"easeOut"`, `"easeInOut"`, `"circIn"`, `"circOut"`, `"circInOut"`, `"backIn"`, `"backOut"`, `"backInOut"`, `"anticipate"`

#### Inertia

```tsx
// Decelerates based on velocity (used after drag)
transition={{
  type: "inertia",
  velocity: 200,
  power: 0.8,      // Deceleration multiplier
  min: 0,          // Minimum value
  max: 300,        // Maximum value
  bounceStiffness: 500,
  bounceDamping: 10,
}}
```

### Repeat & Delay

```tsx
transition={{
  repeat: Infinity,           // or number of repeats
  repeatType: "reverse",      // "loop" | "reverse" | "mirror"
  repeatDelay: 0.5,           // seconds between repeats
  delay: 0.2,                 // initial delay
}}
```

### Keyframe Timing

```tsx
// Keyframes with custom timing
<motion.div
  animate={{ x: [0, 100, 50, 100] }}
  transition={{
    duration: 2,
    ease: ["easeIn", "easeOut", "easeInOut"],  // one per segment
    times: [0, 0.3, 0.7, 1],                   // normalized timestamps
  }}
/>
```

## Variants

Named animation states with orchestration:

```tsx
const variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
}

<motion.div
  variants={variants}
  initial="hidden"
  animate="visible"
/>
```

### Variant Propagation

Parent variants propagate to children automatically:

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",     // "beforeChildren" | "afterChildren"
      staggerChildren: 0.1,       // delay between each child
      delayChildren: 0.3,         // delay before first child
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

<motion.ul variants={container} initial="hidden" animate="visible">
  <motion.li variants={item} />   {/* No need for initial/animate */}
  <motion.li variants={item} />
  <motion.li variants={item} />
</motion.ul>
```

### Dynamic Variants (custom Prop)

```tsx
const variants = {
  hidden: { opacity: 0 },
  visible: (index: number) => ({
    opacity: 1,
    transition: { delay: index * 0.1 },
  }),
}

{items.map((item, i) => (
  <motion.div
    key={item.id}
    custom={i}               // passed to variant function
    variants={variants}
    initial="hidden"
    animate="visible"
  />
))}
```

### Prevent Inheritance

```tsx
// Stop child from inheriting parent variant changes
<motion.div inherit={false} />
```

## style Prop (Independent Transforms)

```tsx
// Motion supports independent transform values in style
<motion.div
  style={{
    x: 100,          // translateX
    y: 50,           // translateY
    z: 0,            // translateZ
    rotate: 45,      // rotate (degrees)
    rotateX: 0,
    rotateY: 0,
    rotateZ: 0,
    scale: 1.5,
    scaleX: 1,
    scaleY: 1,
    skewX: 0,
    skewY: 0,
  }}
/>

// Custom transform order
<motion.div
  style={{ x: 0, rotate: 180 }}
  transformTemplate={({ x, rotate }) =>
    `rotate(${rotate}deg) translateX(${x}px)`
  }
/>
```

## Common Patterns

### Fade In

```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.5 }}
/>
```

### Slide In from Left

```tsx
<motion.div
  initial={{ opacity: 0, x: -100 }}
  animate={{ opacity: 1, x: 0 }}
  transition={{ type: "spring", damping: 20 }}
/>
```

### Scale Pulse

```tsx
<motion.div
  animate={{ scale: [1, 1.05, 1] }}
  transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
/>
```

### Rotate In

```tsx
<motion.div
  initial={{ opacity: 0, rotate: -10, scale: 0.95 }}
  animate={{ opacity: 1, rotate: 0, scale: 1 }}
  transition={{ type: "spring", stiffness: 200 }}
/>
```

### Staggered List

```tsx
const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
}
const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

<motion.ul variants={container} initial="hidden" animate="visible">
  {items.map((i) => (
    <motion.li key={i.id} variants={item}>{i.name}</motion.li>
  ))}
</motion.ul>
```
