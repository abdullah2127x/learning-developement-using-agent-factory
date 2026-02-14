# GSAP React Integration

## Installation

```bash
npm install gsap @gsap/react
```

## Setup Pattern (Module Level)

```jsx
// lib/gsap.ts — single registration file
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(useGSAP, ScrollTrigger);
export { gsap, useGSAP, ScrollTrigger };
```

```jsx
// components/AnimatedBox.tsx — import from your module
import { gsap, useGSAP } from '@/lib/gsap';
```

---

## useGSAP Hook — Complete Reference

### Signature

```ts
useGSAP(
  callback: (context: gsap.Context, contextSafe: Function) => void | (() => void),
  config?: {
    scope?: React.RefObject<HTMLElement>;
    dependencies?: any[];
    revertOnUpdate?: boolean;
  }
)
```

### How It Works Internally

1. Creates a `gsap.context()` scoped to `scope` ref
2. Runs callback inside that context (using `useIsomorphicLayoutEffect`)
3. All GSAP instances created inside are tracked by the context
4. On unmount (or dep change with `revertOnUpdate`), calls `context.revert()`
5. `revert()` kills and reverts all tracked animations, ScrollTriggers, etc.

### Pattern 1: Run Once on Mount

```jsx
function FadeIn() {
  const container = useRef();

  useGSAP(() => {
    gsap.from('.item', { opacity: 0, y: 20, stagger: 0.1 });
  }, { scope: container });

  return <div ref={container}>...</div>;
}
```

### Pattern 2: Re-run on Dependency Change

```jsx
function AnimatedCounter({ value }) {
  const container = useRef();

  useGSAP(() => {
    gsap.to('.counter', { innerText: value, snap: { innerText: 1 }, duration: 1 });
  }, { dependencies: [value], scope: container });

  return <div ref={container}><span className="counter">0</span></div>;
}
```

### Pattern 3: Full Revert on Update

```jsx
function DynamicLayout({ layout }) {
  const container = useRef();

  useGSAP(() => {
    if (layout === 'grid') {
      gsap.to('.card', { scale: 1, stagger: 0.05 });
    } else {
      gsap.to('.card', { scale: 0.8, stagger: 0.03 });
    }
  }, { dependencies: [layout], scope: container, revertOnUpdate: true });

  return <div ref={container}>...</div>;
}
```

---

## contextSafe — Event Handler Pattern

Animations created OUTSIDE the `useGSAP` callback (click handlers, timeouts, observers) escape the context and won't be cleaned up.

### Method 1: Returned from Hook (for JSX handlers)

```jsx
function InteractiveBox() {
  const container = useRef();
  const { contextSafe } = useGSAP({ scope: container });

  const handleClick = contextSafe(() => {
    gsap.to('.box', { rotation: '+=90', duration: 0.3 });
  });

  const handleHover = contextSafe(() => {
    gsap.to('.box', { scale: 1.1, duration: 0.2 });
  });

  return (
    <div ref={container}>
      <div className="box" onClick={handleClick} onMouseEnter={handleHover} />
    </div>
  );
}
```

### Method 2: Inside Hook (for imperative listeners)

```jsx
function DragResponder() {
  const container = useRef();
  const boxRef = useRef();

  useGSAP((context, contextSafe) => {
    const handlePointerMove = contextSafe((e) => {
      gsap.to(boxRef.current, { x: e.clientX, y: e.clientY, duration: 0.3 });
    });

    window.addEventListener('pointermove', handlePointerMove);
    return () => window.removeEventListener('pointermove', handlePointerMove);
  }, { scope: container });

  return <div ref={container}><div ref={boxRef} className="box" /></div>;
}
```

---

## Refs vs Selector Strings

| Approach | When to Use |
|----------|-------------|
| `scope` + class selectors | Multiple targets, stagger, groups |
| Direct `ref` | Single specific element, conditional targeting |
| `gsap.utils.selector(ref)` | Scoped queries without `useGSAP` scope |

```jsx
// Scope + selectors (preferred for groups)
useGSAP(() => {
  gsap.to('.card', { y: 0, stagger: 0.1 }); // scoped to container
}, { scope: container });

// Direct ref (for single element)
useGSAP(() => {
  gsap.to(titleRef.current, { opacity: 1, duration: 0.5 });
}, { scope: container });
```

---

## React 18 Strict Mode

React 18 mounts → unmounts → remounts components in dev mode. Without cleanup:

```
Mount: animation starts
Unmount: animation NOT killed (leak)
Remount: NEW animation starts → now TWO competing animations
```

With `useGSAP`:

```
Mount: animation starts, tracked by context
Unmount: context.revert() kills animation, reverts DOM
Remount: fresh animation starts cleanly
```

**This is why `useGSAP` is mandatory, not optional.**

---

## Server-Side Rendering (Next.js)

`useGSAP` internally uses `useIsomorphicLayoutEffect` — safe for SSR.

### App Router (React Server Components)

```jsx
'use client'; // Required at top of file

import { useRef } from 'react';
import { gsap, useGSAP } from '@/lib/gsap';

export function AnimatedSection() {
  const container = useRef();
  useGSAP(() => { /* animations */ }, { scope: container });
  return <section ref={container}>...</section>;
}
```

### Key Rules for SSR

1. Add `'use client'` to any file using `useGSAP`
2. Never access `window`/`document` at module level — only inside `useGSAP`
3. ScrollTrigger normalizes scroll — safe for SSR since it only runs client-side
4. `gsap.registerPlugin()` at module level is safe (GSAP checks for `window` internally)

---

## TypeScript Integration

```tsx
import { useRef } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

interface AnimatedCardProps {
  delay?: number;
  children: React.ReactNode;
}

function AnimatedCard({ delay = 0, children }: AnimatedCardProps) {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from(container.current!, {
      opacity: 0,
      y: 30,
      duration: 0.6,
      delay,
    });
  }, { scope: container, dependencies: [delay] });

  return <div ref={container}>{children}</div>;
}
```

### Typing contextSafe

```tsx
const { contextSafe } = useGSAP({ scope: container });

const handleClick = contextSafe<React.MouseEvent>(() => {
  gsap.to('.box', { scale: 1.2 });
});
```

---

## Coordinating with React State

GSAP animates DOM directly. React state changes trigger re-renders. They can conflict.

### Pattern: State Drives Animation Trigger, Not Values

```jsx
function Toggle({ isOpen }) {
  const container = useRef();

  useGSAP(() => {
    gsap.to('.panel', {
      height: isOpen ? 'auto' : 0,
      opacity: isOpen ? 1 : 0,
      duration: 0.4,
    });
  }, { dependencies: [isOpen], scope: container });

  return <div ref={container}><div className="panel">Content</div></div>;
}
```

### Anti-Pattern: Don't Set State From GSAP Callbacks During Render

```jsx
// BAD — causes render loop
useGSAP(() => {
  gsap.to('.box', { x: 100, onComplete: () => setAnimating(false) });
  setAnimating(true); // triggers re-render during layout effect
});

// GOOD — defer state update
useGSAP(() => {
  gsap.to('.box', {
    x: 100,
    onStart: () => requestAnimationFrame(() => setAnimating(true)),
    onComplete: () => requestAnimationFrame(() => setAnimating(false)),
  });
});
```

---

## Animating Component Entrance/Exit

GSAP doesn't manage mount/unmount — React does. For exit animations, you must delay unmounting.

### Simple Pattern: Animate Before Remove

```jsx
function AnimatedItem({ item, onRemove }) {
  const el = useRef();
  const { contextSafe } = useGSAP({ scope: el });

  const handleRemove = contextSafe(() => {
    gsap.to(el.current, {
      opacity: 0,
      y: -20,
      duration: 0.3,
      onComplete: () => onRemove(item.id),
    });
  });

  return <div ref={el}><button onClick={handleRemove}>Remove</button></div>;
}
```

### With Flip for Layout Transitions

```jsx
import { Flip } from 'gsap/Flip';

function ReorderableList({ items }) {
  const container = useRef();

  useGSAP(() => {
    // Runs after items change
    const state = Flip.getState('.item');
    // React re-renders with new order...
    Flip.from(state, { duration: 0.5, ease: 'power2.out', stagger: 0.05 });
  }, { dependencies: [items], scope: container });

  return (
    <div ref={container}>
      {items.map(item => <div key={item.id} className="item">{item.name}</div>)}
    </div>
  );
}
```
