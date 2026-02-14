# ScrollTrigger in React

## Setup

```jsx
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);
```

---

## Core Concepts

ScrollTrigger links animations to scroll position. Two modes:

1. **Toggle-based**: play/pause/reverse based on scroll position
2. **Scrub-based**: animation progress directly tied to scroll position

---

## Basic Pattern in React

```jsx
function ScrollReveal() {
  const container = useRef();

  useGSAP(() => {
    gsap.from('.reveal', {
      opacity: 0,
      y: 60,
      duration: 0.8,
      stagger: 0.2,
      scrollTrigger: {
        trigger: '.reveal-section',
        start: 'top 80%',     // trigger top hits 80% of viewport
        end: 'bottom 20%',
        toggleActions: 'play none none reverse',
      }
    });
  }, { scope: container });

  return <div ref={container}>...</div>;
}
```

---

## Config Properties Reference

### Position & Trigger

| Property | Type | Description |
|----------|------|-------------|
| `trigger` | Element/string | Element whose position triggers animation |
| `start` | string | When to start — `"[trigger position] [viewport position]"` |
| `end` | string | When to end — same format as start |
| `endTrigger` | Element/string | Different element for calculating end position |

**Position values**: `top`, `center`, `bottom`, `px`, `%`, or function.

```js
start: 'top center'      // trigger's top hits viewport center
start: 'top 80%'         // trigger's top hits 80% from viewport top
start: 'top+=100 center' // trigger's top + 100px hits center
start: () => innerHeight * 0.5  // dynamic function
```

### Animation Control

| Property | Type | Description |
|----------|------|-------------|
| `scrub` | boolean/number | Link progress to scroll. Number = smoothing seconds |
| `pin` | boolean/Element | Pin trigger element during active range |
| `pinSpacing` | boolean/string | Add spacing for pinned element |
| `snap` | number/array/object | Snap to progress values |
| `toggleActions` | string | `"enter leave enterBack leaveBack"` |
| `toggleClass` | string/object | Toggle CSS class |

### toggleActions

Four states: `onEnter`, `onLeave`, `onEnterBack`, `onLeaveBack`
Four actions: `play`, `pause`, `resume`, `reverse`, `restart`, `reset`, `complete`, `none`

```js
toggleActions: 'play pause resume reverse'  // common pattern
toggleActions: 'play none none reverse'     // play once, reverse on scroll back
toggleActions: 'restart none none reverse'  // restart each time
```

### Scrub Modes

```js
scrub: true     // instant link to scrollbar
scrub: 0.5      // 0.5s smoothing (recommended)
scrub: 1        // 1s smoothing (smooth, slight lag)
```

### Snap

```js
snap: 0.1            // snap to nearest 10% increment
snap: [0, 0.25, 0.5, 0.75, 1]  // snap to specific progress values
snap: 'labels'        // snap to timeline labels
snap: {
  snapTo: 'labels',
  duration: { min: 0.2, max: 0.8 },
  delay: 0.1,
  ease: 'power1.inOut'
}
```

### Callbacks

```js
ScrollTrigger.create({
  trigger: '.section',
  onEnter: (self) => {},        // scrolling down past start
  onLeave: (self) => {},        // scrolling down past end
  onEnterBack: (self) => {},    // scrolling up past end
  onLeaveBack: (self) => {},    // scrolling up past start
  onUpdate: (self) => {         // every scroll frame
    self.progress;    // 0–1
    self.direction;   // 1 (down) or -1 (up)
    self.isActive;    // boolean
    self.getVelocity(); // px/second
  },
  onRefresh: (self) => {},      // after position recalculation
});
```

---

## Pinning Pattern

```jsx
function PinnedSection() {
  const container = useRef();

  useGSAP(() => {
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: '.pinned-section',
        pin: true,
        start: 'top top',
        end: '+=200%',    // pin for 2x viewport height of scrolling
        scrub: 1,
      }
    });

    tl.from('.step-1', { opacity: 0, y: 50 })
      .from('.step-2', { opacity: 0, y: 50 })
      .from('.step-3', { opacity: 0, y: 50 });
  }, { scope: container });

  return <div ref={container}>...</div>;
}
```

---

## Batch Pattern (Staggered Reveals)

```jsx
useGSAP(() => {
  ScrollTrigger.batch('.card', {
    onEnter: (batch) => {
      gsap.from(batch, {
        opacity: 0,
        y: 40,
        stagger: 0.1,
        duration: 0.6,
      });
    },
    start: 'top 85%',
  });
}, { scope: container });
```

---

## Responsive with matchMedia

```jsx
useGSAP(() => {
  const mm = gsap.matchMedia();

  mm.add('(min-width: 768px)', () => {
    // Desktop: horizontal scroll
    gsap.to('.panels', {
      xPercent: -100 * (panels.length - 1),
      ease: 'none',
      scrollTrigger: {
        trigger: '.panels-container',
        pin: true,
        scrub: 1,
        end: () => '+=' + document.querySelector('.panels-container').offsetWidth,
      }
    });
  });

  mm.add('(max-width: 767px)', () => {
    // Mobile: vertical stack with reveals
    gsap.from('.panel', {
      opacity: 0,
      y: 30,
      stagger: 0.2,
      scrollTrigger: { trigger: '.panels-container', start: 'top 80%' }
    });
  });
}, { scope: container });
```

---

## Refresh After DOM Changes

```jsx
// After dynamic content loads (lazy images, async data)
useEffect(() => {
  if (dataLoaded) {
    ScrollTrigger.refresh();
  }
}, [dataLoaded]);
```

---

## Debugging ScrollTrigger

```js
scrollTrigger: {
  markers: true,  // shows start/end markers (DEV ONLY)
  // markers: { startColor: 'green', endColor: 'red', fontSize: '12px' }
}
```

**Remove `markers: true` before production.**

```js
// Inspect all active ScrollTriggers
ScrollTrigger.getAll().forEach(st => console.log(st.vars));
```

---

## React-Specific Gotchas

### 1. ScrollTrigger with Dynamic Lists

```jsx
// Problem: adding items doesn't recalculate positions
// Solution: refresh after items change
useGSAP(() => {
  gsap.from('.item', {
    y: 30, opacity: 0, stagger: 0.1,
    scrollTrigger: { trigger: '.list', start: 'top 80%' }
  });
  // Refresh after animations are set up
  ScrollTrigger.refresh();
}, { dependencies: [items.length], scope: container, revertOnUpdate: true });
```

### 2. Pin Inside Flex/Grid Container

Pinning changes element positioning. Inside flex/grid, this can break layout.

```jsx
// Wrap pinned section in a non-flex container
<div className="pin-wrapper" style={{ overflow: 'hidden' }}>
  <div className="pinned-content">...</div>
</div>
```

### 3. Route Changes (SPA)

```jsx
// In your route layout or page component
useEffect(() => {
  return () => {
    ScrollTrigger.getAll().forEach(st => st.kill());
    ScrollTrigger.refresh();
  };
}, []);
```

But with `useGSAP`, this is handled automatically — context revert kills associated ScrollTriggers.
