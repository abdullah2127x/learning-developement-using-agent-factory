# Layout Animations & AnimatePresence

## layout Prop

Automatically animates an element when its layout (position/size) changes:

```tsx
// Animate all layout changes
<motion.div layout />

// Animate only position (not size)
<motion.div layout="position" />

// Animate only size (not position)
<motion.div layout="size" />
```

When any re-render causes the element to move or resize, Motion smoothly animates the change.

### Expanding Card Example

```tsx
"use client"
import { useState } from "react"
import { motion } from "motion/react"

function ExpandableCard() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <motion.div
      layout
      onClick={() => setIsOpen(!isOpen)}
      style={{
        width: isOpen ? 400 : 200,
        height: isOpen ? 300 : 100,
        borderRadius: 12,
        background: "#3b82f6",
        cursor: "pointer",
      }}
    >
      <motion.h3 layout="position">Title</motion.h3>
      {isOpen && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Details</motion.p>}
    </motion.div>
  )
}
```

### Layout Transition Control

```tsx
<motion.div
  layout
  transition={{
    layout: { type: "spring", stiffness: 300, damping: 30 },
  }}
/>
```

### Layout Performance

```tsx
// Only measure when this dependency changes (optimization)
<motion.nav layout layoutDependency={isOpen} />

// Required on scrollable parents of layout-animated children
<motion.div layoutScroll style={{ overflow: "scroll" }}>
  <motion.div layout />
</motion.div>

// Required on position:fixed parents
<motion.div layoutRoot style={{ position: "fixed" }}>
  <motion.div layout />
</motion.div>
```

### Layout Callbacks

```tsx
<motion.div
  layout
  onLayoutAnimationStart={() => console.log("Layout animation started")}
  onLayoutAnimationComplete={() => console.log("Layout animation done")}
/>
```

## layoutId (Shared Element Transitions)

Animate between two different elements that share the same `layoutId`:

```tsx
// Tab underline that slides between tabs
function Tabs() {
  const [activeTab, setActiveTab] = useState(0)

  return (
    <nav style={{ display: "flex", gap: 8 }}>
      {["Home", "About", "Contact"].map((tab, i) => (
        <button key={tab} onClick={() => setActiveTab(i)} style={{ position: "relative" }}>
          {tab}
          {activeTab === i && (
            <motion.div
              layoutId="tab-underline"
              style={{
                position: "absolute",
                bottom: -2, left: 0, right: 0,
                height: 2,
                background: "#3b82f6",
              }}
            />
          )}
        </button>
      ))}
    </nav>
  )
}
```

### Shared Layout: Card to Modal

```tsx
"use client"
import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"

function CardList() {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  return (
    <>
      {items.map((item) => (
        <motion.div
          key={item.id}
          layoutId={`card-${item.id}`}
          onClick={() => setSelectedId(item.id)}
          style={{ cursor: "pointer", borderRadius: 12, padding: 16 }}
        >
          <motion.h3 layoutId={`title-${item.id}`}>{item.title}</motion.h3>
        </motion.div>
      ))}

      <AnimatePresence>
        {selectedId && (
          <motion.div
            layoutId={`card-${selectedId}`}
            style={{
              position: "fixed", inset: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
              zIndex: 50,
            }}
          >
            <motion.h3 layoutId={`title-${selectedId}`}>
              {items.find((i) => i.id === selectedId)?.title}
            </motion.h3>
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              Full content here
            </motion.p>
            <button onClick={() => setSelectedId(null)}>Close</button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
```

## LayoutGroup

Namespace `layoutId` to prevent conflicts between separate groups:

```tsx
import { LayoutGroup } from "motion/react"

// Without LayoutGroup, both "underline" layoutIds conflict
// With LayoutGroup, each group has its own namespace

<LayoutGroup id="sidebar">
  <TabRow items={sidebarTabs} />
</LayoutGroup>

<LayoutGroup id="main">
  <TabRow items={mainTabs} />
</LayoutGroup>
```

## AnimatePresence

Enables exit animations when elements are removed from the React tree:

```tsx
import { AnimatePresence, motion } from "motion/react"

<AnimatePresence>
  {isVisible && (
    <motion.div
      key="unique-key"                    // REQUIRED inside AnimatePresence
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    />
  )}
</AnimatePresence>
```

### AnimatePresence Modes

```tsx
// "sync" (default): Enter and exit happen simultaneously
<AnimatePresence>
  {items.map(item => <motion.div key={item.id} exit={{ opacity: 0 }} />)}
</AnimatePresence>

// "wait": Exit completes before enter begins (one child at a time)
<AnimatePresence mode="wait">
  <motion.div key={currentPage} exit={{ opacity: 0 }} />
</AnimatePresence>

// "popLayout": Exiting element removed from layout flow immediately
<AnimatePresence mode="popLayout">
  {items.map(item => (
    <motion.li layout key={item.id} exit={{ opacity: 0 }} />
  ))}
</AnimatePresence>
```

**Important for `popLayout`**: Direct children that are custom components must use `React.forwardRef`.

### onExitComplete

```tsx
<AnimatePresence onExitComplete={() => {
  console.log("All exit animations finished")
  // Good place to scroll to top, clean up state, etc.
}}>
  {/* ... */}
</AnimatePresence>
```

### initial Prop on AnimatePresence

```tsx
// Skip initial animation on first render
<AnimatePresence initial={false}>
  <motion.div
    key={page}
    initial={{ x: 300 }}
    animate={{ x: 0 }}
    exit={{ x: -300 }}
  />
</AnimatePresence>
```

## Page Transitions (Next.js App Router)

### Template-Based Approach

```tsx
// app/template.tsx — re-mounts on every navigation
"use client"
import { motion } from "motion/react"

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}
```

**Note**: `template.tsx` re-mounts on every route change (unlike `layout.tsx`), making it ideal for page enter animations. However, it cannot do exit animations because Next.js unmounts immediately.

### AnimatePresence Page Transitions

For full enter + exit transitions, create a client wrapper:

```tsx
// components/page-transition.tsx
"use client"
import { AnimatePresence, motion } from "motion/react"
import { usePathname } from "next/navigation"

export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

```tsx
// app/layout.tsx
import { PageTransition } from "@/components/page-transition"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <nav>{/* navigation */}</nav>
        <PageTransition>{children}</PageTransition>
      </body>
    </html>
  )
}
```

### Slide Page Transition

```tsx
"use client"
import { AnimatePresence, motion } from "motion/react"
import { usePathname } from "next/navigation"

const pageVariants = {
  initial: { opacity: 0, x: 50 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -50 },
}

export function SlideTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={{ type: "tween", duration: 0.3, ease: "easeInOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

## Common Patterns

### Animated List (Add/Remove Items)

```tsx
"use client"
function AnimatedList() {
  const [items, setItems] = useState([...])

  return (
    <ul>
      <AnimatePresence>
        {items.map((item) => (
          <motion.li
            key={item.id}
            layout
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            {item.name}
            <button onClick={() => removeItem(item.id)}>Remove</button>
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  )
}
```

### Notification Toast

```tsx
<AnimatePresence>
  {notifications.map((notification) => (
    <motion.div
      key={notification.id}
      layout
      initial={{ opacity: 0, y: -50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
    >
      {notification.message}
    </motion.div>
  ))}
</AnimatePresence>
```

### Accordion

```tsx
"use client"
function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div>
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileTap={{ scale: 0.98 }}
      >
        {title}
        <motion.span
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.span>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            style={{ overflow: "hidden" }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
```
