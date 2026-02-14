# Progressive Learning Path

## Level 1: Foundations (Day 1-2)

### Goal
Animate a single element with `gsap.to()` inside a React component using `useGSAP`.

### Learn

1. **Install and register**
   ```bash
   npm install gsap @gsap/react
   ```
   ```jsx
   import gsap from 'gsap';
   import { useGSAP } from '@gsap/react';
   gsap.registerPlugin(useGSAP);
   ```

2. **First animation**
   ```jsx
   function MyComponent() {
     const container = useRef();
     useGSAP(() => {
       gsap.to('.box', { x: 200, duration: 1 });
     }, { scope: container });
     return <div ref={container}><div className="box">Hello</div></div>;
   }
   ```

3. **Core methods**: `gsap.to()`, `gsap.from()`, `gsap.fromTo()`, `gsap.set()`
4. **Properties**: `x`, `y`, `rotation`, `scale`, `opacity`, `duration`, `delay`

### Practice
- Fade in a card on mount
- Slide a navigation bar from off-screen
- Scale a button on mount

### Checkpoint
Can you explain why `useGSAP` instead of `useEffect`? (Answer: automatic cleanup via `gsap.context()`, safe for React 18 strict mode)

---

## Level 2: Easing & Stagger (Day 3-4)

### Goal
Make animations feel natural and animate groups of elements.

### Learn

1. **Easing**: `ease: 'power2.out'`, `'elastic.out(1, 0.3)'`, `'back.out(1.7)'`
2. **Rule of thumb**: `.out` for entrances, `.in` for exits, `.inOut` for transitions
3. **Stagger basics**: `stagger: 0.1`
4. **Advanced stagger**: `stagger: { each: 0.1, from: 'center' }`

### Practice
- Stagger-reveal a list of cards with `gsap.from()` and `stagger`
- Experiment with 5 different eases on the same animation
- Create a loading animation with `repeat: -1` and `yoyo: true`

### Checkpoint
Can you make a grid of items animate in from the center outward?

---

## Level 3: Timelines (Day 5-7)

### Goal
Sequence multiple animations with precise timing control.

### Learn

1. **Timeline creation**: `gsap.timeline()`
2. **Chaining**: `.to().from().to()`
3. **Position parameter**: `'-=0.2'`, `'<'`, `'>'`, absolute time
4. **Labels**: `tl.addLabel('intro')`
5. **Defaults**: `gsap.timeline({ defaults: { duration: 0.5 } })`
6. **Playback control**: `.play()`, `.pause()`, `.reverse()`, `.restart()`

### Practice
- Build a 3-step intro animation with overlapping elements
- Create a timeline that can be played/paused/reversed with buttons
- Nest two timelines into a master timeline

### Checkpoint
Can you create a timeline where 3 elements animate in with overlapping timing using position parameters?

---

## Level 4: Interactivity (Day 8-10)

### Goal
Animate in response to user actions (click, hover, scroll into view).

### Learn

1. **contextSafe for events**
   ```jsx
   const { contextSafe } = useGSAP({ scope: container });
   const onClick = contextSafe(() => gsap.to('.box', { rotation: '+=90' }));
   ```
2. **Hover patterns**: `onMouseEnter`/`onMouseLeave` with `contextSafe`
3. **Toggle animations**: play/reverse a paused timeline on click
4. **Dependency-driven**: `useGSAP(() => {...}, { dependencies: [isOpen] })`

### Practice
- Button that scales up on hover, scales back on leave
- Accordion that opens/closes with a timeline toggle
- Counter that animates when value prop changes

### Checkpoint
Can you explain why event handler animations need `contextSafe()`? (Answer: they're created outside the `useGSAP` callback scope, so they escape the context and won't be auto-cleaned)

---

## Level 5: ScrollTrigger (Day 11-15)

### Goal
Create scroll-driven animations: reveals, pinning, scrubbing.

### Learn

1. **Basic reveal**: `scrollTrigger: { trigger: '.section', start: 'top 80%' }`
2. **toggleActions**: `'play none none reverse'`
3. **Scrub**: Link animation progress to scroll position
4. **Pinning**: Fix element during scroll range
5. **Batch**: Staggered reveals for groups
6. **matchMedia**: Responsive scroll animations

### Practice
- Fade-up sections as they scroll into view
- Pin a hero section and animate content within it
- Create a horizontal scroll section on desktop, vertical on mobile
- Batch-animate a card grid as cards enter viewport

### Checkpoint
Can you build a pinned section with 3 animated steps that plays as you scroll?

---

## Level 6: Advanced Patterns (Day 16-20)

### Goal
Build reusable animation infrastructure for a production app.

### Learn

1. **Reusable hooks**: `useScrollReveal`, `useTimeline`, `useAnimateOnMount`
2. **Animation presets**: Centralized animation configs
3. **Flip plugin**: Animate layout changes (reorder, filter)
4. **Page transitions**: Animate between routes
5. **Performance**: GPU-accelerated properties, `will-change`, batch vs individual

### Practice
- Create 3 reusable animation hooks for your project
- Build a filterable grid using Flip plugin
- Implement page transitions with your router
- Profile animations in Chrome DevTools Performance tab

### Checkpoint
Can you explain the difference between animating `x` vs `left` performance-wise? (Answer: `x` uses CSS transforms which are GPU-composited; `left` triggers layout recalculation)

---

## Level 7: Expert (Ongoing)

### Goal
Master complex animation orchestration and edge cases.

### Topics

1. **SplitText**: Character/word/line animations (Club GSAP)
2. **MorphSVG**: SVG shape morphing (Club GSAP)
3. **DrawSVG**: SVG stroke animation (Club GSAP)
4. **ScrollSmoother**: Smooth scroll wrapper (Club GSAP)
5. **Custom eases**: `CustomEase.create()` for brand-specific motion
6. **Observer plugin**: Complex gesture handling
7. **MotionPath**: Animate along SVG paths
8. **GSDevTools**: Visual timeline debugging

### Architecture Topics
- Animation state machines for complex UI flows
- Shared animation context across component boundaries
- Code-splitting animation plugins
- Animation testing strategies
- Accessibility (prefers-reduced-motion)

### Accessibility Pattern

```jsx
useGSAP(() => {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReduced) {
    gsap.set('.animate', { opacity: 1, y: 0 }); // instant, no animation
  } else {
    gsap.from('.animate', { opacity: 0, y: 30, stagger: 0.1 });
  }
}, { scope: container });

// OR use matchMedia for automatic handling
useGSAP(() => {
  const mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', () => {
    gsap.from('.animate', { opacity: 0, y: 30, stagger: 0.1 });
  });
  mm.add('(prefers-reduced-motion: reduce)', () => {
    gsap.set('.animate', { opacity: 1 });
  });
}, { scope: container });
```

---

## Official Resources

| Resource | URL | Use For |
|----------|-----|---------|
| GSAP Docs | https://gsap.com/docs/v3 | API reference |
| React Guide | https://gsap.com/resources/React | Official React patterns |
| Ease Visualizer | https://gsap.com/docs/v3/Eases | Pick the right ease |
| CodePen Collection | https://codepen.io/GreenSock | Working examples |
| GSAP Forum | https://gsap.com/community | Community help |
| Install Helper | https://gsap.com/docs/v3/Installation | Setup for any bundler |
