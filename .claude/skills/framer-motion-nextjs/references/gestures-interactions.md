# Gestures & Interactions

## Gesture Animation Props

Motion provides gesture-specific animation props that animate while a gesture is active:

| Prop | Gesture | Fires When |
|------|---------|------------|
| `whileHover` | Pointer hover | Pointer enters element |
| `whileTap` | Press/click | Pointer pressed on element |
| `whileFocus` | Focus | Element receives focus |
| `whileDrag` | Drag | Element is being dragged |
| `whileInView` | Scroll into view | Element enters viewport |

All gesture props accept animation targets or variant names:

```tsx
// Direct target
<motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} />

// Variant names
<motion.button
  variants={{ hover: { scale: 1.05 }, tap: { scale: 0.95 } }}
  whileHover="hover"
  whileTap="tap"
/>
```

## Hover

```tsx
<motion.div
  whileHover={{ scale: 1.1, backgroundColor: "#f0f0f0" }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
/>
```

### Hover Events

```tsx
<motion.a
  whileHover={{ scale: 1.05 }}
  onHoverStart={(event, info) => {
    console.log("Hover started", info.point)
  }}
  onHoverEnd={(event, info) => {
    console.log("Hover ended")
  }}
/>
```

### Hover with Children

```tsx
// Parent hover triggers child animation via variants
const parent = {
  rest: {},
  hover: { scale: 1.02 },
}
const arrow = {
  rest: { x: 0 },
  hover: { x: 5 },
}

<motion.a variants={parent} initial="rest" whileHover="hover">
  <span>Learn more</span>
  <motion.span variants={arrow}>→</motion.span>
</motion.a>
```

## Tap (Press)

```tsx
<motion.button
  whileTap={{ scale: 0.9, rotate: 3 }}
/>
```

### Tap Events

```tsx
<motion.button
  onTap={(event, info) => {
    console.log("Tapped at", info.point)
  }}
  onTapStart={(event, info) => {
    console.log("Tap started")
  }}
  onTapCancel={(event, info) => {
    console.log("Tap cancelled — pointer left element")
  }}
/>
```

**Note**: `onTap` is different from `onClick` — it correctly handles touch events and cancels if pointer moves off the element before release.

## Focus

```tsx
<motion.input
  whileFocus={{
    scale: 1.02,
    borderColor: "#3b82f6",
    boxShadow: "0 0 0 3px rgba(59, 130, 246, 0.3)",
  }}
/>
```

## Drag

### Basic Drag

```tsx
// Drag in all directions
<motion.div drag />

// Constrain to single axis
<motion.div drag="x" />
<motion.div drag="y" />
```

### Drag Constraints

```tsx
// Pixel constraints
<motion.div
  drag
  dragConstraints={{ top: -100, right: 100, bottom: 100, left: -100 }}
/>

// Ref-based constraints (constrain within parent)
function DragBox() {
  const constraintsRef = useRef(null)

  return (
    <div ref={constraintsRef} style={{ width: 400, height: 400 }}>
      <motion.div drag dragConstraints={constraintsRef} />
    </div>
  )
}
```

### Drag Configuration

```tsx
<motion.div
  drag
  dragElastic={0.2}           // 0 = strict, 1 = full elastic (default: 0.35)
  dragMomentum={true}         // Enable momentum after release (default: true)
  dragTransition={{           // Controls momentum behavior
    bounceStiffness: 600,
    bounceDamping: 20,
  }}
  dragSnapToOrigin={true}     // Snap back to origin on release
  dragPropagation             // Allow drag to propagate to parent
  dragListener={true}         // Toggle drag listening
/>
```

### Drag Events

```tsx
<motion.div
  drag
  onDrag={(event, info) => {
    console.log("Dragging:", info.point, info.delta, info.offset, info.velocity)
  }}
  onDragStart={(event, info) => {
    console.log("Drag started at", info.point)
  }}
  onDragEnd={(event, info) => {
    console.log("Drag ended with velocity", info.velocity)
  }}
  onDirectionLock={(axis) => {
    console.log("Locked to", axis)  // "x" or "y"
  }}
/>
```

### Drag with whileDrag

```tsx
<motion.div
  drag
  whileDrag={{
    scale: 1.1,
    backgroundColor: "#ef4444",
    cursor: "grabbing",
  }}
  style={{ cursor: "grab" }}
/>
```

### Drag + Layout for Reorderable Lists

```tsx
import { Reorder } from "motion/react"

function ReorderableList() {
  const [items, setItems] = useState(["Item 1", "Item 2", "Item 3"])

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item} value={item}>
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```

## Pan

Pan events fire when the pointer moves after pointerdown, without enabling drag:

```tsx
<motion.div
  onPan={(event, info) => {
    console.log("Pan:", info.point, info.delta, info.offset, info.velocity)
  }}
  onPanStart={(event, info) => {}}
  onPanEnd={(event, info) => {}}
/>
```

## Event Info Object

All gesture callbacks receive `(event, info)` where `info` contains:

```typescript
interface PanInfo {
  point: { x: number; y: number }      // Absolute position
  delta: { x: number; y: number }      // Distance since last event
  offset: { x: number; y: number }     // Distance from start
  velocity: { x: number; y: number }   // Current velocity
}
```

## Common Patterns

### Interactive Card

```tsx
<motion.div
  whileHover={{ y: -4, boxShadow: "0 10px 30px rgba(0,0,0,0.12)" }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
>
  <h3>Card Title</h3>
  <p>Card content</p>
</motion.div>
```

### Magnetic Button

```tsx
function MagneticButton({ children }: { children: React.ReactNode }) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  function handleMouse(e: React.MouseEvent) {
    const rect = e.currentTarget.getBoundingClientRect()
    x.set(e.clientX - rect.left - rect.width / 2)
    y.set(e.clientY - rect.top - rect.height / 2)
  }

  function reset() {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.button
      style={{ x, y }}
      onMouseMove={handleMouse}
      onMouseLeave={reset}
      transition={{ type: "spring", stiffness: 150, damping: 15 }}
    >
      {children}
    </motion.button>
  )
}
```

### Swipe to Dismiss

```tsx
function SwipeToDismiss({ children, onDismiss }: {
  children: React.ReactNode
  onDismiss: () => void
}) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (Math.abs(info.offset.x) > 100) {
          onDismiss()
        }
      }}
      animate={{ x: 0 }}
    >
      {children}
    </motion.div>
  )
}
```

### Toggle Switch

```tsx
function Toggle({ isOn, onToggle }: { isOn: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      style={{
        width: 50, height: 28, borderRadius: 14,
        background: isOn ? "#3b82f6" : "#d1d5db",
        display: "flex", padding: 2, cursor: "pointer",
        justifyContent: isOn ? "flex-end" : "flex-start",
      }}
    >
      <motion.div
        layout
        transition={{ type: "spring", stiffness: 700, damping: 30 }}
        style={{ width: 24, height: 24, borderRadius: 12, background: "#fff" }}
      />
    </button>
  )
}
```
