# Production Patterns

## Reusable Hooks

### useAnimateOnMount

```tsx
import { useRef } from 'react';
import { gsap, useGSAP } from '@/lib/gsap';

interface UseAnimateOnMountOptions {
  from?: gsap.TweenVars;
  duration?: number;
  delay?: number;
  ease?: string;
}

export function useAnimateOnMount(options: UseAnimateOnMountOptions = {}) {
  const ref = useRef<HTMLDivElement>(null);
  const { from = { opacity: 0, y: 20 }, duration = 0.6, delay = 0, ease = 'power2.out' } = options;

  useGSAP(() => {
    gsap.from(ref.current!, { ...from, duration, delay, ease });
  }, { scope: ref });

  return ref;
}

// Usage
function Card() {
  const ref = useAnimateOnMount({ delay: 0.2 });
  return <div ref={ref}>Content</div>;
}
```

### useTimeline

```tsx
import { useRef } from 'react';
import { gsap, useGSAP } from '@/lib/gsap';

export function useTimeline(config?: gsap.TimelineVars) {
  const tl = useRef<gsap.core.Timeline>();
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    tl.current = gsap.timeline(config);
  }, { scope: container });

  return { tl, container };
}

// Usage
function SteppedAnimation() {
  const { tl, container } = useTimeline({ paused: true });

  const { contextSafe } = useGSAP({ scope: container });
  const play = contextSafe(() => tl.current?.play());

  useGSAP(() => {
    tl.current
      ?.from('.step-1', { opacity: 0, y: 20 })
      .from('.step-2', { opacity: 0, y: 20 }, '-=0.2')
      .from('.step-3', { opacity: 0, y: 20 }, '-=0.2');
  }, { scope: container });

  return (
    <div ref={container}>
      <button onClick={play}>Play</button>
      <div className="step-1">Step 1</div>
      <div className="step-2">Step 2</div>
      <div className="step-3">Step 3</div>
    </div>
  );
}
```

### useScrollReveal

```tsx
import { useRef } from 'react';
import { gsap, useGSAP, ScrollTrigger } from '@/lib/gsap';

interface ScrollRevealOptions {
  from?: gsap.TweenVars;
  start?: string;
  stagger?: number;
  selector?: string;
}

export function useScrollReveal(options: ScrollRevealOptions = {}) {
  const container = useRef<HTMLDivElement>(null);
  const {
    from = { opacity: 0, y: 40 },
    start = 'top 80%',
    stagger = 0.1,
    selector = '.reveal'
  } = options;

  useGSAP(() => {
    gsap.from(selector, {
      ...from,
      stagger,
      duration: 0.7,
      scrollTrigger: {
        trigger: container.current,
        start,
        toggleActions: 'play none none reverse',
      }
    });
  }, { scope: container });

  return container;
}

// Usage
function FeatureSection() {
  const ref = useScrollReveal({ stagger: 0.15 });
  return (
    <section ref={ref}>
      <h2 className="reveal">Features</h2>
      <div className="reveal">Feature 1</div>
      <div className="reveal">Feature 2</div>
    </section>
  );
}
```

### useHoverAnimation

```tsx
export function useHoverAnimation(
  animateIn: gsap.TweenVars = { scale: 1.05, duration: 0.3 },
  animateOut: gsap.TweenVars = { scale: 1, duration: 0.3 }
) {
  const ref = useRef<HTMLDivElement>(null);
  const { contextSafe } = useGSAP({ scope: ref });

  const onEnter = contextSafe(() => gsap.to(ref.current!, animateIn));
  const onLeave = contextSafe(() => gsap.to(ref.current!, animateOut));

  return { ref, onMouseEnter: onEnter, onMouseLeave: onLeave };
}
```

---

## Animation Architecture for Large Apps

### Project Structure

```
src/
├── lib/
│   └── gsap.ts              # Single registration point
├── animations/
│   ├── hooks/                # Reusable animation hooks
│   │   ├── useAnimateOnMount.ts
│   │   ├── useScrollReveal.ts
│   │   ├── useTimeline.ts
│   │   └── useHoverAnimation.ts
│   ├── presets.ts            # Shared animation configs
│   └── index.ts              # Barrel export
├── components/
│   ├── AnimatedSection.tsx   # Uses hooks internally
│   └── ScrollRevealGroup.tsx
└── pages/
```

### Animation Presets

```ts
// animations/presets.ts
export const presets = {
  fadeUp: { opacity: 0, y: 30, duration: 0.6, ease: 'power2.out' },
  fadeDown: { opacity: 0, y: -30, duration: 0.6, ease: 'power2.out' },
  scaleIn: { scale: 0.8, opacity: 0, duration: 0.5, ease: 'back.out(1.7)' },
  slideLeft: { x: -100, opacity: 0, duration: 0.7, ease: 'power3.out' },
  slideRight: { x: 100, opacity: 0, duration: 0.7, ease: 'power3.out' },
} as const;

export type AnimationPreset = keyof typeof presets;
```

### Composition Pattern: AnimatedGroup Component

```tsx
import { useRef, Children, cloneElement } from 'react';
import { gsap, useGSAP } from '@/lib/gsap';
import { presets, AnimationPreset } from '@/animations/presets';

interface AnimatedGroupProps {
  preset?: AnimationPreset;
  stagger?: number;
  children: React.ReactNode;
  scroll?: boolean;
}

export function AnimatedGroup({ preset = 'fadeUp', stagger = 0.1, children, scroll = false }: AnimatedGroupProps) {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const vars: gsap.TweenVars = {
      ...presets[preset],
      stagger,
    };

    if (scroll) {
      vars.scrollTrigger = {
        trigger: container.current,
        start: 'top 80%',
        toggleActions: 'play none none reverse',
      };
    }

    gsap.from('.animated-child', vars);
  }, { scope: container });

  return (
    <div ref={container}>
      {Children.map(children, child =>
        cloneElement(child as React.ReactElement, {
          className: `${(child as React.ReactElement).props.className || ''} animated-child`.trim()
        })
      )}
    </div>
  );
}
```

---

## Performance Optimization

### 1. Animate Transform Properties (GPU-Accelerated)

```js
// FAST — composited by GPU (transform + opacity)
gsap.to('.box', { x: 100, y: 50, rotation: 45, scale: 1.2, opacity: 0.5 });

// SLOW — triggers layout recalculation
gsap.to('.box', { width: 200, height: 100, top: 50, left: 100 });
```

**Rule**: Prefer `x/y` over `left/top`, `scale` over `width/height`.

### 2. Use will-change Sparingly

```css
/* Apply to elements GSAP will animate, remove when done */
.will-animate { will-change: transform, opacity; }
```

```js
gsap.to('.box', {
  x: 100,
  onStart: () => el.style.willChange = 'transform',
  onComplete: () => el.style.willChange = 'auto',
});
```

### 3. Limit Active ScrollTriggers

```jsx
// Instead of individual ScrollTriggers per item:
// Use ScrollTrigger.batch for groups
ScrollTrigger.batch('.card', {
  onEnter: batch => gsap.from(batch, { opacity: 0, y: 30, stagger: 0.1 }),
});
```

### 4. Avoid Animating During Layout

```jsx
// Use useGSAP (runs useLayoutEffect timing) — not useEffect
// This prevents visible flash of unstyled content
useGSAP(() => {
  gsap.set('.hidden-initially', { autoAlpha: 0 }); // immediate hide
  gsap.to('.hidden-initially', { autoAlpha: 1, delay: 0.3 }); // then animate in
}, { scope: container });
```

### 5. Lazy Plugin Loading

```jsx
// Only load ScrollTrigger when needed
const ScrollSection = lazy(() => import('./ScrollSection'));

// ScrollSection.tsx
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);
```

### 6. Kill Unnecessary Animations

```jsx
useGSAP(() => {
  const anim = gsap.to('.loader', { rotation: 360, repeat: -1 });
  // Kill when no longer needed (e.g., data loaded)
  return () => anim.kill();
}, { scope: container });
```

---

## Page Transition Pattern

```tsx
// layouts/AnimatedLayout.tsx
import { useRef, useCallback } from 'react';
import { gsap, useGSAP } from '@/lib/gsap';
import { useRouter } from 'next/navigation'; // or your router

export function AnimatedLayout({ children }: { children: React.ReactNode }) {
  const container = useRef<HTMLDivElement>(null);

  // Entrance animation
  useGSAP(() => {
    gsap.from(container.current, { opacity: 0, y: 10, duration: 0.4 });
  }, { scope: container });

  return <div ref={container}>{children}</div>;
}
```

---

## Testing Animations

```ts
// In tests, skip all GSAP animations
beforeAll(() => {
  gsap.globalTimeline.timeScale(100); // near-instant
});

// Or disable entirely
beforeAll(() => {
  gsap.ticker.lagSmoothing(0);
  gsap.globalTimeline.progress(1); // jump to end
});
```
