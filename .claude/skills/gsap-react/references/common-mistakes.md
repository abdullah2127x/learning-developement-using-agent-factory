# Common Mistakes & Anti-Patterns

## Critical Mistakes

### 1. Using useEffect Instead of useGSAP

```jsx
// BAD — no cleanup, leaks in React 18 strict mode
useEffect(() => {
  gsap.to('.box', { x: 100 });
}, []);

// GOOD — auto cleanup via gsap.context()
useGSAP(() => {
  gsap.to('.box', { x: 100 });
}, { scope: container });
```

**Why it matters**: React 18 strict mode double-mounts. Without cleanup, you get two competing animations on the same element.

### 2. Missing scope Ref

```jsx
// BAD — selects ALL .box elements in the entire DOM
useGSAP(() => {
  gsap.to('.box', { x: 100 });
});

// GOOD — scoped to this component's children only
useGSAP(() => {
  gsap.to('.box', { x: 100 });
}, { scope: container });
```

### 3. Unscoped Event Handler Animations

```jsx
// BAD — animation escapes the context, never cleaned up
const handleClick = () => {
  gsap.to('.box', { rotation: 90 });
};

// GOOD — wrapped in contextSafe
const { contextSafe } = useGSAP({ scope: container });
const handleClick = contextSafe(() => {
  gsap.to('.box', { rotation: 90 });
});
```

### 4. Registering Plugins Inside Components

```jsx
// BAD — re-registers every render
function MyComponent() {
  gsap.registerPlugin(ScrollTrigger);
  // ...
}

// GOOD — register once at module level
gsap.registerPlugin(ScrollTrigger);
function MyComponent() {
  // ...
}
```

### 5. Animating Inline Styles That React Also Controls

```jsx
// BAD — React and GSAP fight over the same property
function Box({ isActive }) {
  return (
    <div style={{ opacity: isActive ? 1 : 0 }}> {/* React controls opacity */}
      {/* GSAP also animates opacity → conflict */}
    </div>
  );
}

// GOOD — let GSAP own animated properties
function Box({ isActive }) {
  const container = useRef();
  useGSAP(() => {
    gsap.to('.box', { opacity: isActive ? 1 : 0, duration: 0.3 });
  }, { dependencies: [isActive], scope: container });

  return <div ref={container}><div className="box">Content</div></div>;
}
```

---

## Moderate Mistakes

### 6. Creating Timelines Without Paused State

```jsx
// BAD — timeline plays immediately, even if you want manual control
const tl = gsap.timeline();

// GOOD — create paused, play when ready
const tl = gsap.timeline({ paused: true });
// Later: tl.play();
```

### 7. Not Using Defaults on Timelines

```jsx
// BAD — repetitive
tl.to('.a', { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' })
  .to('.b', { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' })
  .to('.c', { y: 0, opacity: 1, duration: 0.5, ease: 'power2.out' });

// GOOD — DRY with defaults
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: 'power2.out' } });
tl.to('.a', { y: 0, opacity: 1 })
  .to('.b', { y: 0, opacity: 1 }, '-=0.3')
  .to('.c', { y: 0, opacity: 1 }, '-=0.3');
```

### 8. Animating Layout Properties

```jsx
// BAD — causes layout thrashing, 60fps impossible on complex pages
gsap.to('.box', { width: 200, height: 100, top: 50, marginLeft: 20 });

// GOOD — use transforms (GPU composited)
gsap.to('.box', { scaleX: 2, scaleY: 1, y: 50, x: 20 });
```

### 9. Not Handling Dynamic Content with ScrollTrigger

```jsx
// BAD — ScrollTrigger positions calculated before images load
useGSAP(() => {
  gsap.from('.section', { scrollTrigger: { trigger: '.section' } });
}, { scope: container });

// GOOD — refresh after content loads
useGSAP(() => {
  gsap.from('.section', { scrollTrigger: { trigger: '.section' } });
}, { scope: container });

useEffect(() => {
  const images = container.current?.querySelectorAll('img');
  if (images) {
    Promise.all(
      Array.from(images).map(img =>
        img.complete ? Promise.resolve() : new Promise(r => img.onload = r)
      )
    ).then(() => ScrollTrigger.refresh());
  }
}, []);
```

### 10. Forgetting markers Removal

```jsx
// DEV — helpful
scrollTrigger: { markers: true }

// PRODUCTION — remove or conditionally add
scrollTrigger: {
  markers: process.env.NODE_ENV === 'development',
}
```

---

## Subtle Mistakes

### 11. from() Flicker on Remount

```jsx
// PROBLEM — element shows briefly at final state, then jumps to from() values
useGSAP(() => {
  gsap.from('.box', { opacity: 0, y: 50 });
}, { scope: container });

// SOLUTION — use set() + from() or use immediateRender
useGSAP(() => {
  gsap.set('.box', { opacity: 0, y: 50 });  // instant hide
  gsap.to('.box', { opacity: 1, y: 0, duration: 0.6 });
}, { scope: container });

// OR use fromTo for explicit control
useGSAP(() => {
  gsap.fromTo('.box', { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 0.6 });
}, { scope: container });
```

### 12. Overwriting Tweens on Same Target

```jsx
// PROBLEM — multiple tweens on same property create conflicts
gsap.to('.box', { x: 100 });
gsap.to('.box', { x: 200 }); // both try to animate x

// SOLUTION — use overwrite
gsap.to('.box', { x: 200, overwrite: true }); // kills prior x tweens
// OR use overwrite: 'auto' to only kill conflicting properties
```

### 13. Incorrect Dependency Arrays

```jsx
// BAD — creates new animation every render (no deps = runs every time)
useGSAP(() => {
  gsap.to('.box', { x: position });
}); // missing dependency array

// GOOD — explicit dependencies
useGSAP(() => {
  gsap.to('.box', { x: position });
}, { dependencies: [position], scope: container });
```

---

## Debugging Checklist

When animations aren't working:

1. **Element exists?** Check if selector matches any elements. Use browser DevTools.
2. **Scope correct?** Is `scope` ref attached to a mounted parent element?
3. **Plugin registered?** `gsap.registerPlugin(PluginName)` called at module level?
4. **Timing right?** Is the element in the DOM when `useGSAP` runs? (use `dependencies`)
5. **Property conflict?** Is React or CSS overriding the same property GSAP is animating?
6. **Competing tweens?** Multiple animations targeting the same property? Use `overwrite: true`.
7. **ScrollTrigger markers?** Add `markers: true` to visualize trigger positions.
8. **React strict mode?** Is double-mount causing duplicate animations? Use `useGSAP`.
9. **Console errors?** GSAP logs warnings for invalid targets, missing plugins, etc.
10. **Cleanup running?** Add `console.log` in cleanup return to verify.

### Quick Debug Snippet

```js
// Dump all active tweens and ScrollTriggers
console.log('Active tweens:', gsap.globalTimeline.getChildren());
console.log('ScrollTriggers:', ScrollTrigger.getAll());
```
