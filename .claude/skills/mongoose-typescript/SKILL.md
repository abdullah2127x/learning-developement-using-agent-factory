---
name: mongoose-typescript
description: |
  Comprehensive guide for building type-safe Mongoose schemas and models with TypeScript
  for Next.js serverless projects. This skill should be used when users need to create
  MongoDB schemas, define typed models, add validation, set up relationships (references,
  subdocuments, discriminators), configure Next.js database connections, or implement
  production-grade data layers with Mongoose and TypeScript.
---

# Mongoose + TypeScript for Next.js

Build type-safe MongoDB data layers — from basic schemas to complex relational models.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing models, connection setup, project structure, tsconfig settings |
| **Conversation** | User's specific schema requirements, relationships, validation rules |
| **Skill References** | Domain patterns from `references/` (typing strategies, Next.js patterns) |
| **User Guidelines** | Naming conventions, directory structure, testing preferences |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

## Mental Model

```
Schema Definition (runtime validation + structure)
       ↓
TypeScript Types (compile-time safety)
       ↓
Model (CRUD operations + custom methods)
       ↓
Next.js Integration (connection caching + serverless)
```

**Key insight**: Mongoose operates at TWO type levels:
1. **`RawDocType`** — plain data as stored in MongoDB (what you write)
2. **`HydratedDocument`** — Mongoose document with methods, virtuals, save() (what you get back)

## Quick Start

### Minimal typed schema + model (Next.js ready)

```typescript
// lib/db.ts
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

async function dbConnect() {
  if (mongoose.connections[0].readyState) return;
  await mongoose.connect(MONGODB_URI);
}
export default dbConnect;

// models/User.ts
import mongoose, { Schema, InferSchemaType, model } from 'mongoose';

const userSchema = new Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  role: { type: String, enum: ['admin', 'user'], default: 'user' },
}, { timestamps: true });

type IUser = InferSchemaType<typeof userSchema>;

export default mongoose.models.User || model('User', userSchema);
```

**tsconfig.json requirement**: `"strict": true` or `"strictNullChecks": true`

## Decision Trees

### Which typing approach?

```
Need methods/statics/virtuals?
├─ No → Use InferSchemaType (automatic inference)
│       Define schema inline in new Schema()
│       Use `as const` if schema defined separately
│
└─ Yes → Use separate interface + Schema generics
         Schema<DocType, ModelType, Methods, QueryHelpers, Virtuals, Statics>
         See references/methods-statics-virtuals.md
```

### Which relationship pattern?

```
Data always accessed together?
├─ Yes → Embedded subdocuments (nested schema)
│        Best for: address, preferences, metadata
│
├─ Sometimes → Hybrid (embed + selective populate)
│
└─ No → References (ObjectId + populate)
         Best for: users↔posts, orders↔products
         See references/relationships-populate.md

Need polymorphism? (different shapes in same collection)
└─ Yes → Discriminators
         Best for: events, notifications, content types
```

### Which validation approach?

```
Simple type/format check?
├─ Yes → Built-in validators (required, min, max, enum, match, minLength, maxLength)
│
├─ Cross-field logic? → Custom validator with function context
│                       validate: { validator: function(v) { return this.field > v; } }
│
└─ Async check? (uniqueness, external API)
   → Async custom validator (return Promise)
     See references/validation-middleware.md
```

## Schema Type Mapping (Quick Reference)

| TypeScript | Mongoose SchemaType | Notes |
|------------|-------------------|-------|
| `string` | `String` / `{ type: String }` | `required: true` → non-optional |
| `number` | `Number` | `min`, `max` validators |
| `boolean` | `Boolean` | |
| `Date` | `Date` | |
| `Types.ObjectId` | `Schema.Types.ObjectId` | Use with `ref` for populate |
| `string[]` | `[String]` | Array of strings |
| `Map<string, V>` | `{ type: Map, of: V }` | Use `.$*` for populate |
| Nested object | Inline `{}` or separate `Schema` | Prefer Schema for validation |
| Union/enum | `{ type: String, enum: [...] }` | Compile-time via `as const` |

## Next.js Integration Essentials

### Model registration (prevent hot-reload errors)

```typescript
// ALWAYS use this pattern in Next.js
export default mongoose.models.ModelName || model('ModelName', schema);
```

### next.config.js (required)

```javascript
const nextConfig = {
  experimental: {
    esmExternals: "loose",
    serverComponentsExternalPackages: ["mongoose"],
  },
};
```

### Edge Runtime: NOT SUPPORTED
Mongoose cannot run in Edge Runtime (no Node.js `net` API).
Always use `export const runtime = 'nodejs';` in Server Components using Mongoose.

## File Structure (Recommended)

```
lib/
  db.ts              # dbConnect function
models/
  User.ts            # Schema + types + model export
  Post.ts
  index.ts           # Re-export all models
types/
  models.ts          # Shared types (optional, for cross-model types)
```

## Production Checklist

- [ ] `strict: true` in tsconfig.json
- [ ] `mongoose.models.X || model()` pattern for all models
- [ ] `serverComponentsExternalPackages: ["mongoose"]` in next.config.js
- [ ] `runtime = 'nodejs'` on all Server Components using Mongoose
- [ ] `.env.local` for MONGODB_URI (never hardcode)
- [ ] `{ timestamps: true }` on schemas that need audit trails
- [ ] `unique` fields have corresponding MongoDB indexes (not a validator!)
- [ ] `runValidators: true` on all update operations
- [ ] `.lean()` on read-only queries for performance
- [ ] Populate typed with generics: `.populate<{ field: Type }>('field')`

## Reference Files

| File | When to Read |
|------|-------------|
| `references/typescript-schemas.md` | Schema typing, InferSchemaType, Schema generics, arrays, nested objects |
| `references/methods-statics-virtuals.md` | Instance methods, static methods, virtuals, query helpers |
| `references/validation-middleware.md` | Validators, custom validation, pre/post hooks, error handling |
| `references/relationships-populate.md` | References, populate typing, subdocuments, discriminators, Maps |
| `references/nextjs-serverless.md` | Connection caching, model registration, App Router, Server Components |
| `references/common-mistakes.md` | Anti-patterns with fixes, debugging checklist |

Search patterns for large references:
- Schema generics → `grep -n "Schema<" references/typescript-schemas.md`
- Populate typing → `grep -n "populate<" references/relationships-populate.md`
- Middleware hooks → `grep -n "schema.pre\|schema.post" references/validation-middleware.md`
- Next.js patterns → `grep -n "dbConnect\|mongoose.models" references/nextjs-serverless.md`
