---
id: 001
title: Create Mongoose TypeScript Skill
stage: general
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["mongoose", "typescript", "nextjs", "skill-creation", "mongodb"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/mongoose-typescript/SKILL.md
  - .claude/skills/mongoose-typescript/references/typescript-schemas.md
  - .claude/skills/mongoose-typescript/references/methods-statics-virtuals.md
  - .claude/skills/mongoose-typescript/references/validation-middleware.md
  - .claude/skills/mongoose-typescript/references/relationships-populate.md
  - .claude/skills/mongoose-typescript/references/nextjs-serverless.md
  - .claude/skills/mongoose-typescript/references/common-mistakes.md
tests:
  - Skill registered and visible in available skills list
---

## Prompt

Using your "skill-creator-pro" skill create a new skill for Mongoose schemas with TypeScript types. I will use it to build type-safe MongoDB models for Next.js serverless projects from basic schemas to complex relational models. Use context7 skill to study official Mongoose TypeScript documentation, Schema validation, Model types, and Next.js database connection patterns, then build it so no self assumed knowledge.

## Response snapshot

Created a comprehensive Guide-type skill `mongoose-typescript` with SKILL.md + 6 reference files. Domain discovery used Context7 (`/websites/mongoosejs`) and official Mongoose documentation pages (mongoosejs.com) for TypeScript schemas, populate, query helpers, middleware, discriminators, validation, and Next.js integration patterns. All knowledge sourced from official docs — zero assumed knowledge.

**Skill structure:**
- `SKILL.md` — Mental model, quick start, decision trees (typing approach, relationship pattern, validation approach), type mapping table, Next.js essentials, production checklist
- `references/typescript-schemas.md` — InferSchemaType vs separate interface, all 9 Schema generics, type mapping, arrays, Maps, enums, timestamps, Mixed, RawDocType vs HydratedDocument
- `references/methods-statics-virtuals.md` — Schema options (recommended) and separate interface approaches for methods, statics, virtuals, query helpers, combined patterns, loadClass
- `references/validation-middleware.md` — Built-in validators, custom sync/async validators, cross-field validation, update validators, middleware types (document/query/aggregate/model), pre/post hooks, error handling middleware
- `references/relationships-populate.md` — References, embedded subdocs, hybrid pattern, typed populate (generic approach), virtual populate, Map populate, discriminators (basic, embedded, single nested), lean()
- `references/nextjs-serverless.md` — dbConnect, model registration, next.config.js, Edge Runtime limitation, Route Handlers, Server Components, Server Actions, serialization
- `references/common-mistakes.md` — 16 anti-patterns with before/after fixes, debugging checklist table

## Outcome

- ✅ Impact: New reusable skill for type-safe Mongoose development in Next.js serverless projects
- 🧪 Tests: Skill registered and visible in skills list
- 📁 Files: 7 files created (1 SKILL.md + 6 references)
- 🔁 Next prompts: Test skill by creating a real schema, validate with skill-validator
- 🧠 Reflection: Context7 `/esl/mongoosedocs` returned MongooseIM (XMPP server) not Mongoose ODM — `/websites/mongoosejs` was the correct library ID

## Evaluation notes (flywheel)

- Failure modes observed: Context7 library ID ambiguity (MongooseIM vs Mongoose ODM), first query returned wrong domain
- Graders run and results (PASS/FAIL): PASS — skill registered, all files created, all content sourced from official docs
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Validate skill with skill-validator for quality scoring
