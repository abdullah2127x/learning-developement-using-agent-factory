# GSAP Core Concepts

## Tweens — The Building Blocks

A **tween** animates one or more properties of one or more targets over time.

### Four Core Methods

```js
// Animate FROM current values TO specified values (most common)
gsap.to('.box', { x: 200, opacity: 1, duration: 1 });

// Animate FROM specified values TO current values
gsap.from('.box', { opacity: 0, y: -50, duration: 0.8 });

// Explicit start AND end values
gsap.fromTo('.box', { scale: 0 }, { scale: 1, duration: 0.6 });

// Instant set (duration: 0)
gsap.set('.box', { transformOrigin: 'center center' });
```

### Essential Tween Properties

| Property | Default | Description |
|----------|---------|-------------|
| `duration` | 0.5 | Seconds |
| `delay` | 0 | Wait before start |
| `ease` | "power1.out" | Rate of change curve |
| `repeat` | 0 | Number of extra iterations (-1 = infinite) |
| `yoyo` | false | Reverse direction on each repeat |
| `stagger` | 0 | Offset between multiple targets |
| `overwrite` | false | Kill conflicting tweens on same target |

### Value Types

```js
// Absolute
gsap.to('.box', { x: 100 });

// Relative (add/subtract from current)
gsap.to('.box', { x: '+=50', rotation: '-=15' });

// Function-based (per-target)
gsap.to('.box', { x: (i, target) => i * 100 });

// Random
gsap.to('.box', { x: 'random(-200, 200)' });
```

### Callbacks

```js
gsap.to('.box', {
  x: 200,
  onStart: () => console.log('started'),
  onUpdate: (self) => console.log('progress'),
  onComplete: () => console.log('done'),
  onRepeat: () => console.log('repeating'),
});
```

---

## Timelines — Sequencing Animations

A timeline is a container that sequences tweens with precise timing control.

### Basic Sequencing

```js
const tl = gsap.timeline();
tl.to('.a', { x: 100, duration: 0.5 })
  .to('.b', { y: 50, duration: 0.3 })   // starts after .a finishes
  .to('.c', { opacity: 0, duration: 0.4 }); // starts after .b finishes
```

### Position Parameter (Timing Control)

The position parameter controls WHERE a tween inserts in the timeline.

```js
tl.to('.a', { x: 100 })
  .to('.b', { y: 50 }, '+=0.5')    // 0.5s gap after previous
  .to('.c', { opacity: 0 }, '-=0.2') // overlap previous by 0.2s
  .to('.d', { scale: 2 }, 2)         // at exactly 2 seconds
  .to('.e', { rotation: 90 }, '<')    // same start as previous tween
  .to('.f', { x: -100 }, '>')        // at end of previous tween
```

| Syntax | Meaning |
|--------|---------|
| `'+=0.5'` | 0.5s after end of timeline |
| `'-=0.3'` | 0.3s before end of timeline (overlap) |
| `3` | At absolute time 3s |
| `'<'` | At start of previous tween |
| `'>'` | At end of previous tween |
| `'<0.5'` | 0.5s after start of previous |
| `'myLabel'` | At a named label |
| `'myLabel+=1'` | 1s after a label |

### Labels

```js
tl.addLabel('intro')
  .to('.a', { x: 100 })
  .addLabel('middle')
  .to('.b', { y: 50 }, 'middle')
  .to('.c', { opacity: 0 }, 'middle+=0.2');
```

### Timeline Defaults

```js
const tl = gsap.timeline({
  defaults: { duration: 0.5, ease: 'power2.out' },
  repeat: -1,
  yoyo: true,
});
```

### Nesting Timelines

```js
function introAnimation() {
  const tl = gsap.timeline();
  return tl.from('.header', { y: -50, opacity: 0 })
           .from('.subtitle', { opacity: 0 }, '-=0.2');
}

function mainAnimation() {
  const tl = gsap.timeline();
  return tl.from('.content', { y: 30, opacity: 0 });
}

// Master timeline
const master = gsap.timeline();
master.add(introAnimation())
      .add(mainAnimation(), '-=0.3');
```

### Playback Control

```js
const tl = gsap.timeline({ paused: true });
tl.play();        // forward from current position
tl.pause();       // freeze
tl.reverse();     // play backward
tl.restart();     // jump to start and play
tl.seek(1.5);     // jump to 1.5s
tl.progress(0.5); // jump to 50%
tl.timeScale(2);  // 2x speed
```

---

## Easing

Easing controls the *rate of change* — it's what makes animation feel natural.

### Categories

| Category | Feel | Use For |
|----------|------|---------|
| `power1`–`power4` | Subtle → dramatic | General motion |
| `back` | Overshoot | Playful entrances |
| `elastic` | Springy | Attention-grabbing |
| `bounce` | Bouncy | Physical realism |
| `expo` | Sharp acceleration | Dramatic reveals |
| `sine` | Gentle | Subtle, natural |
| `circ` | Circular curve | Smooth transitions |
| `steps(n)` | Stepped | Sprite sheets, clocks |

### Directional Variants

- `.out` (default) — fast start, slow end → best for entrances
- `.in` — slow start, fast end → best for exits
- `.inOut` — slow start, slow end → best for transitions

```js
gsap.to('.box', { x: 200, ease: 'power2.out' });     // smooth entrance
gsap.to('.box', { x: 200, ease: 'elastic.out(1, 0.3)' }); // springy
gsap.to('.box', { x: 200, ease: 'back.out(1.7)' });  // overshoot
```

### Global Default

```js
gsap.defaults({ ease: 'power2.out', duration: 0.6 });
```

---

## Stagger — Animating Groups

Offset animation start times across multiple targets.

```js
// Simple: 0.1s between each
gsap.from('.item', { y: 30, opacity: 0, stagger: 0.1 });

// Advanced stagger object
gsap.from('.grid-item', {
  scale: 0,
  stagger: {
    each: 0.1,       // time between each
    from: 'center',   // origin: 'start', 'end', 'center', 'edges', 'random', or index
    grid: [4, 8],     // row x col grid layout
    ease: 'power2.in',
    axis: 'x',        // stagger along x-axis only
  }
});
```

---

## Utility Methods (Most Useful)

```js
// Scope selectors to a container (critical for React)
const q = gsap.utils.selector(containerRef);
gsap.to(q('.box'), { x: 100 });

// Convert to array
const boxes = gsap.utils.toArray('.box');

// Wrap values (cycling)
const colors = gsap.utils.wrap(['red', 'green', 'blue']);
colors(0); // 'red', colors(3); // 'red' (wraps)

// Clamp values
const clamped = gsap.utils.clamp(0, 100, 150); // 100

// Map one range to another
const mapped = gsap.utils.mapRange(0, 1, 0, 100, 0.5); // 50

// Snap to increment
const snapped = gsap.utils.snap(5, 13); // 15

// Interpolate between values
gsap.utils.interpolate('red', 'blue', 0.5); // purple
gsap.utils.interpolate(0, 100, 0.5); // 50

// Distribute values (great for stagger-like effects)
gsap.utils.distribute({ base: 0, amount: 100, ease: 'power2' });

// Pipe functions
const transform = gsap.utils.pipe(
  gsap.utils.clamp(0, 100),
  gsap.utils.snap(5)
);
transform(87); // 85
```

---

## Plugin Registration

Register plugins ONCE at module level, outside any component:

```js
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Flip } from 'gsap/Flip';
import { Draggable } from 'gsap/Draggable';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, Flip, Draggable, useGSAP);
```

### Available Plugins (Free)

| Plugin | Purpose |
|--------|---------|
| ScrollTrigger | Scroll-driven animations |
| Flip | Animate layout changes |
| Draggable | Make elements draggable |
| Observer | Watch for user interactions (scroll, touch, pointer) |
| MotionPathPlugin | Animate along SVG/custom paths |
| TextPlugin | Animate text content changes |
| EasePack | Additional easing functions |

### Premium Plugins (Club GSAP)

| Plugin | Purpose |
|--------|---------|
| SplitText | Animate individual characters/words/lines |
| MorphSVGPlugin | Morph between SVG shapes |
| DrawSVGPlugin | Animate SVG stroke drawing |
| ScrollSmoother | Smooth scrolling wrapper |
| GSDevTools | Visual animation debugging |
