---
name: gsap-react
description: |
  Comprehensive guide for building GSAP animations in React applications.
  This skill should be used when users need to create animations, transitions,
  scroll-based effects, or motion design in React using GSAP. Covers useGSAP hook,
  ScrollTrigger, timelines, cleanup, performance optimization, and production patterns.
---

# GSAP in React

Build production-grade animations in React using GSAP (GreenSock Animation Platform).

## What This Skill Does

- Implements GSAP animations with proper React lifecycle integration
- Creates scroll-driven animations with ScrollTrigger
- Builds reusable animation hooks and component patterns
- Ensures proper cleanup to prevent memory leaks in React 18+ strict mode
- Provides architecture patterns for scalable animation systems

## What This Skill Does NOT Do

- Create CSS-only animations (use CSS transitions/keyframes instead)
- Handle video/canvas rendering pipelines
- Replace React's built-in transition libraries (Framer Motion, React Spring)
- Manage backend or deployment concerns

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | React version (16.8+/18+), existing animation libs, bundler, TypeScript usage |
| **Conversation** | Animation type (scroll, entrance, interactive, page transitions) |
| **Skill References** | Patterns from `references/` — core concepts, React integration, production patterns |
| **User Guidelines** | Component conventions, state management approach, styling system |

---

## Mental Model: How GSAP Works

GSAP operates outside React's render cycle. It directly mutates DOM properties via `requestAnimationFrame`, bypassing virtual DOM diffing entirely.

```
React renders DOM → GSAP reads current values → GSAP interpolates per-frame → DOM updates directly
```

**Key insight**: GSAP owns the DOM properties it animates. React owns the component tree. The `useGSAP` hook bridges these two ownership models by scoping animations to components and auto-reverting on unmount.

---

## Quick Start

```bash
npm install gsap @gsap/react
```

```jsx
import { useRef } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(useGSAP);

function FadeIn({ children }) {
  const container = useRef();

  useGSAP(() => {
    gsap.from('.animate-item', { opacity: 0, y: 30, stagger: 0.1 });
  }, { scope: container });

  return <div ref={container}>{children}</div>;
}
```

---

## Core Decision Tree

```
What kind of animation?
├── Single property change → gsap.to() / gsap.from() / gsap.set()
├── Sequenced multi-step → gsap.timeline()
├── Scroll-driven → ScrollTrigger (standalone or on timeline)
├── Layout/reorder → Flip plugin
├── User interaction (hover/click) → contextSafe() wrapper
└── Responsive/breakpoint → gsap.matchMedia()
```

---

## The useGSAP Hook (Critical)

The official React hook. Drop-in replacement for `useEffect`/`useLayoutEffect` with auto-cleanup.

### Three Usage Patterns

```jsx
// 1. No dependencies — runs once on mount
useGSAP(() => { gsap.to('.box', { x: 100 }); }, { scope: container });

// 2. With dependencies — re-runs when deps change
useGSAP(() => { gsap.to('.box', { x: endX }); }, { dependencies: [endX], scope: container });

// 3. revertOnUpdate — full reset before re-animating
useGSAP(() => { gsap.to('.box', { x: endX }); }, { dependencies: [endX], scope: container, revertOnUpdate: true });
```

### contextSafe for Event Handlers

Animations created outside the hook callback (event handlers, timeouts) are NOT auto-cleaned.

```jsx
const { contextSafe } = useGSAP({ scope: container });

// Wrapped — will be cleaned up
const onClick = contextSafe(() => {
  gsap.to('.box', { rotation: '+=90' });
});

// NOT wrapped — memory leak
const onClickBad = () => {
  gsap.to('.box', { rotation: '+=90' }); // Will NOT be cleaned up
};
```

---

## Cleanup Rules (Non-Negotiable)

| Rule | Why |
|------|-----|
| Always use `useGSAP` instead of `useEffect` for GSAP | Auto-cleanup via `gsap.context()` |
| Always pass `scope` ref | Scopes selectors to component, prevents cross-component leaks |
| Wrap event-handler animations in `contextSafe()` | Otherwise they escape the context |
| Return cleanup for manual listeners | `return () => el.removeEventListener(...)` |
| Register plugins once at module level | `gsap.registerPlugin(ScrollTrigger)` outside components |

---

## Common Patterns at a Glance

| Pattern | Reference File |
|---------|---------------|
| Tweens, timelines, easing, stagger | `references/core-concepts.md` |
| useGSAP lifecycle, cleanup, SSR | `references/react-integration.md` |
| ScrollTrigger, pin, scrub, snap | `references/scrolltrigger.md` |
| Reusable hooks, architecture, perf | `references/production-patterns.md` |
| Anti-patterns, debugging checklist | `references/common-mistakes.md` |
| Beginner → advanced learning path | `references/progressive-learning.md` |

---

## Production Checklist

- [ ] `@gsap/react` installed, `useGSAP` registered as plugin
- [ ] Every animation inside `useGSAP` with `scope` ref
- [ ] Event-handler animations wrapped in `contextSafe()`
- [ ] ScrollTrigger cleanup via `useGSAP` (never manual `ScrollTrigger.create` without context)
- [ ] Plugins registered once at module level, not inside components
- [ ] `gsap.matchMedia()` used for responsive animations
- [ ] No inline styles competing with GSAP-animated properties
- [ ] `will-change` or `transform: translateZ(0)` on animated elements for GPU compositing
- [ ] `markers: true` removed before production deploy
- [ ] Tested in React 18 strict mode (double-mount behavior)

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/core-concepts.md` | Learning GSAP fundamentals (tweens, timelines, easing, stagger, utilities) |
| `references/react-integration.md` | useGSAP hook details, lifecycle, cleanup, SSR, TypeScript |
| `references/scrolltrigger.md` | Scroll-driven animations, pinning, scrubbing, responsive patterns |
| `references/production-patterns.md` | Reusable hooks, animation architecture, performance optimization |
| `references/common-mistakes.md` | Anti-patterns, debugging, gotchas with React 18 |
| `references/progressive-learning.md` | Structured learning path from beginner to expert |
