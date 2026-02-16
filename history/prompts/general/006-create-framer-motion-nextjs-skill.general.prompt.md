---
id: 006
title: Create Framer Motion Next.js Skill
stage: general
date: 2026-02-15
surface: agent
model: claude-opus-4-6-20250929
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["skill-creation","framer-motion","motion","nextjs","animations","gestures","scroll","typescript"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/framer-motion-nextjs/SKILL.md
  - .claude/skills/framer-motion-nextjs/references/motion-components.md
  - .claude/skills/framer-motion-nextjs/references/gestures-interactions.md
  - .claude/skills/framer-motion-nextjs/references/scroll-animations.md
  - .claude/skills/framer-motion-nextjs/references/layout-animations.md
  - .claude/skills/framer-motion-nextjs/references/hooks-utilities.md
  - .claude/skills/framer-motion-nextjs/references/nextjs-patterns.md
tests:
  - none
---

## Prompt

Using your "skill-creator-pro" skill create a new skill for Framer Motion animations in Next.js with TypeScript. I will use it to create smooth animations and transitions from basic fade-ins to complex gesture-based interactions, page transitions, and scroll-triggered animations. Use context7 skill to study official Framer Motion documentation for motion components, variants, gestures, layout animations, scroll animations, exit animations, and TypeScript types, then build it so no self assumed knowledge.

## Response snapshot

Created the `framer-motion-nextjs` skill with domain knowledge sourced entirely from official Motion documentation via Context7.

**Domain discovery sources:**
- Context7 `/websites/motion_dev` (1474 snippets, High reputation, 89.1 benchmark) — full Motion API
- Context7 `/websites/motion_dev_react` (562 snippets, High reputation, 88 benchmark) — React-specific docs
- 10 Context7 queries covering: motion components, gestures, scroll animations, layout animations, AnimatePresence, transitions, hooks, variants, useAnimate, accessibility

**Skill files created (7 total):**

1. **SKILL.md** — Mental model (motion component → animate/transition/variants/gestures/scroll/layout/exit), package setup (`motion/react` vs `motion/react-client`), decision trees (animation approach, transition type, Next.js component boundary), core props reference table, file structure, production checklist

2. **references/motion-components.md** — All motion component props (animate, initial, exit, transition, variants, style), transition types (spring physics/tween duration/inertia), spring parameters (stiffness/damping/mass), tween easings, keyframes with times array, repeat/delay, variant propagation with staggerChildren/delayChildren/when, dynamic variants with custom prop, transformTemplate

3. **references/gestures-interactions.md** — whileHover/whileTap/whileFocus/whileDrag/whileInView, hover/tap/pan events with PanInfo type, drag constraints (pixel and ref-based), dragElastic/dragMomentum/dragSnapToOrigin, Reorder.Group for drag-to-reorder, patterns: interactive card, magnetic button, swipe to dismiss, toggle switch

4. **references/scroll-animations.md** — whileInView with viewport options (once/root/margin/amount), viewport events, useScroll hook (scrollX/scrollY/scrollXProgress/scrollYProgress), target/container/offset parameters, offset edge values explained, useTransform range mapping, useInView hook, patterns: scroll progress bar, parallax, horizontal scroll section, scroll-linked colors, section reveal

5. **references/layout-animations.md** — layout prop ("position"/"size"), layoutId shared element transitions, LayoutGroup namespacing, layoutDependency/layoutScroll/layoutRoot, AnimatePresence modes (sync/wait/popLayout), onExitComplete, initial={false}, page transitions (template.tsx vs AnimatePresence), patterns: tab underline, card-to-modal, animated list, notification toast, accordion

6. **references/hooks-utilities.md** — useAnimate (scope/selectors/sequences/playback controls), useMotionValue (set/get/jump), useMotionValueEvent (change/animationStart/animationComplete), useTransform (range mapping/chaining/clamping), useSpring (smooth scroll), useInView, useReducedMotion (parallax/video), stagger (from options), reusable variant library (fadeIn/fadeInUp/slideIn/scaleIn/staggerContainer)

7. **references/nextjs-patterns.md** — Import strategy (`motion/react-client` for Server Components vs `motion/react` for client), thin client wrapper pattern (FadeIn/ScrollReveal/StaggerList), page transitions (template.tsx vs AnimatePresence), SSR hydration safety, LazyMotion bundle optimization (domAnimation/domMax), performance (GPU transforms, MotionValues over state, viewport once), MotionConfig reducedMotion, TypeScript types (HTMLMotionProps, Variants, MotionValue), 10-item anti-patterns table

## Outcome

- ✅ Impact: Production-ready Framer Motion animation skill for Next.js App Router covering declarative animations through complex gesture/scroll/layout patterns — sourced entirely from official Motion docs via Context7
- 🧪 Tests: none
- 📁 Files: 7 files created under `.claude/skills/framer-motion-nextjs/`
- 🔁 Next prompts: Use `/framer-motion-nextjs` when implementing animations in Next.js projects
- 🧠 Reflection: The `motion/react-client` import for Server Components is a key pattern that prevents unnecessary "use client" directives — encoding this in the decision tree ensures correct component boundaries

## Evaluation notes (flywheel)

- Failure modes observed: motion.dev is a SPA — WebFetch returns only CSS/HTML shell, no content. Context7 was the reliable source.
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add SVG animation patterns (path drawing, morphing) to motion-components.md
