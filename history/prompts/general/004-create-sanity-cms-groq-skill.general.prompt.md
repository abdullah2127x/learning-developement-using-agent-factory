---
id: 004
title: Create Sanity CMS GROQ Skill
stage: general
date: 2026-02-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: AbdullahQureshi
command: skill-creator-pro
labels: ["sanity", "groq", "typescript", "nextjs", "cms", "portable-text", "typegen", "skill-creation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/sanity-cms-groq/SKILL.md
  - .claude/skills/sanity-cms-groq/references/schema-types.md
  - .claude/skills/sanity-cms-groq/references/groq-queries.md
  - .claude/skills/sanity-cms-groq/references/typescript-typegen.md
  - .claude/skills/sanity-cms-groq/references/images-portable-text.md
  - .claude/skills/sanity-cms-groq/references/nextjs-integration.md
  - .claude/skills/sanity-cms-groq/references/common-mistakes.md
tests:
  - Skill registered and visible in available skills list
---

## Prompt

Using your "skill-creator-pro" skill create a new skill for Sanity CMS schemas and GROQ queries with TypeScript. I will use it to build content schemas and type-safe queries from basic document types to complex relational schemas with references and portable text. Use context7 skill to study official Sanity documentation for schema definitions, GROQ query language, TypeScript types, references, images, slugs, and Next.js integration patterns, then build it so no self assumed knowledge.

## Response snapshot

Created a comprehensive Guide-type skill `sanity-cms-groq` with SKILL.md + 6 reference files. Domain discovery used Context7 (`/websites/sanity_io`, 7669 snippets, High reputation; `/sanity-io/next-sanity`, 169 snippets) and official documentation pages (sanity.io/docs/groq, sanity.io/docs/image-url). All knowledge sourced from official docs — zero assumed knowledge.

**Skill structure:**
- `SKILL.md` — Mental model (Schema→Studio→Content Lake→GROQ→TypeGen→sanityFetch→Server Components), 5-step quick start, decision trees (document vs object, references vs embedded, GROQ query vs projection, TypeScript strategy), env vars, file structure, production checklist
- `references/schema-types.md` — defineType/defineField/defineArrayMember, all field types table (primitives, slug, image with hotspot, file, geopoint, references, cross-dataset, array with all member types, object types), validation (built-in, custom sync/async, conditional), ordering, preview configuration, schema registration
- `references/groq-queries.md` — Complete GROQ syntax: filtering (equality, comparison, existence, text match, array membership, reference check), projections (field selection, computed fields, ellipsis, nested), ordering (asc/desc, multi-field), array slicing, dereferencing (->, multiple hops, array refs), joins (reverse references with ^ operator), parameterized queries, all GROQ functions (count/length/defined/now/coalesce/select/pt::text), common patterns (list/detail/homepage/paginated/sitemap/search/inline)
- `references/typescript-typegen.md` — TypeGen workflow (schema extract → typegen generate), sanity-typegen.json config, defineQuery vs plain literals, using generated types (auto-inferred with overloadClientMethods), manual interface approach (query result types vs document types), Sanity's built-in types, TypeGen in CI/CD
- `references/images-portable-text.md` — @sanity/image-url urlFor builder API (all transform methods: width/height/fit/quality/blur/sharpen/auto/format/focalPoint/crop modes), Next.js Image component integration, responsive images with fill, image data in GROQ (lqip/dominant color), Portable Text schema definition (basic/rich/custom types), @portabletext/react components API (types/marks/block/list/listItem), full custom renderer example, internal link annotation pattern, extracting plain text
- `references/nextjs-integration.md` — createClient configuration (useCdn, apiVersion, token), environment variables, sanityFetch helper (time-based revalidation, tag-based revalidation, no-cache), on-demand revalidation webhook route handler, generateStaticParams pattern, metadata generation with OG images, draft mode (previewClient), embedded Studio setup
- `references/common-mistakes.md` — 14 anti-patterns with before/after fixes (slug.current, asset URL, Portable Text rendering, defineQuery, null safety, asset.url vs urlFor, array dereference, apiVersion, missing params, defineArrayMember, no projection, token exposure, no revalidation, missing defineType), debugging table (12 symptoms)

## Outcome

- ✅ Impact: New reusable skill for type-safe Sanity CMS content modeling and GROQ queries in Next.js App Router projects
- 🧪 Tests: Skill registered and visible in skills list
- 📁 Files: 7 files created (1 SKILL.md + 6 references)
- 🔁 Next prompts: Test skill by creating a real schema + queries, validate with skill-validator
- 🧠 Reflection: Sanity's content model (slug as object with .current, image as object needing urlFor, Portable Text as block array) is the source of most beginner errors. TypeGen with defineQuery is the key to automatic TypeScript types from GROQ projections — this was the most important pattern to capture clearly.

## Evaluation notes (flywheel)

- Failure modes observed: sanity.io/docs/schema-types returned minified JS instead of content — worked around with GROQ docs page and Context7 queries
- Graders run and results (PASS/FAIL): PASS — skill registered, all files created, all content from official docs
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Validate skill with skill-validator for quality scoring
