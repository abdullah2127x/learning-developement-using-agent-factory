# TypeScript Schema Typing

## Two Approaches

### Approach 1: Automatic Inference (Recommended for simple schemas)

```typescript
import { Schema, model, InferSchemaType } from 'mongoose';

const userSchema = new Schema({
  name: { type: String, required: true },
  email: { type: String, required: true },
  avatar: String,
  age: { type: Number, min: 0 },
  tags: [String],
  metadata: { type: Map, of: String },
});

// Automatically inferred type
type IUser = InferSchemaType<typeof userSchema>;
// Result: { name: string; email: string; avatar?: string | null; age?: number | null; tags: string[]; metadata?: Map<string, string>; }

const User = model('User', userSchema);
```

**Requirements:**
- `"strict": true` or `"strictNullChecks": true` in tsconfig.json
- Schema MUST be defined inline in `new Schema()` call
- If defined separately, use `as const`:

```typescript
const definition = {
  name: { type: String, required: true },
  email: { type: String, required: true },
} as const;

const schema = new Schema(definition);
type IUser = InferSchemaType<typeof schema>;
```

**InferRawDocType** — for separated definitions:

```typescript
import { InferRawDocType } from 'mongoose';

const definition = {
  name: { type: String, required: true },
} as const;

type RawUser = InferRawDocType<typeof definition>;
// { name: string }
```

### Approach 2: Separate Interface (Required for methods/statics/virtuals)

```typescript
import { Schema, model, Model } from 'mongoose';

interface IUser {
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

const userSchema = new Schema<IUser>({
  name: { type: String, required: true },
  email: { type: String, required: true },
  avatar: String,
}, { timestamps: true });

const User = model<IUser>('User', userSchema);
```

**Important caveat**: Mongoose does NOT verify that interface matches schema. A `required` field in the schema won't make the interface field non-optional — you must align them manually.

Mongoose DOES check that schema paths exist in the interface (catches typos):
```typescript
// ERROR: 'emaill' doesn't exist in IUser
const schema = new Schema<IUser>({ emaill: String }); // TS error
```

Mongoose does NOT check that all interface fields are in the schema (allows timestamps, plugins to add paths).

## Schema Generic Parameters (Full Signature)

```typescript
new Schema<
  RawDocType,            // 1. Raw document data shape
  TModelType,            // 2. Model type (default: Model<DocType>)
  TInstanceMethods,      // 3. Instance methods
  TQueryHelpers,         // 4. Query helper methods
  TVirtuals,             // 5. Virtual properties
  TStaticMethods,        // 6. Static methods
  TSchemaOptions,        // 7. Schema options type
  DocType,               // 8. Inferred document type
  THydratedDocumentType  // 9. Hydrated document type
>
```

**Common patterns:**

```typescript
// Simple (no methods) — only first param
new Schema<IUser>({ ... })

// With methods — params 1, 2, 3
new Schema<IUser, Model<IUser>, IUserMethods>({ ... })

// With methods + query helpers — params 1, 2, 3, 4
new Schema<IUser, Model<IUser, IQueryHelpers>, IUserMethods, IQueryHelpers>({ ... })

// With everything — params 1, 2, 3, 4, 5, 6
new Schema<IUser, UserModelType, IUserMethods, IQueryHelpers, IVirtuals, IStatics>({ ... })
```

## Schema Types Reference

### Primitives

```typescript
const schema = new Schema({
  str: String,                              // string | undefined
  strRequired: { type: String, required: true }, // string
  num: Number,                              // number | undefined
  bool: Boolean,                            // boolean | undefined
  date: Date,                               // Date | undefined
  buf: Buffer,                              // Buffer | undefined
});
```

### ObjectId

```typescript
import { Schema, Types } from 'mongoose';

const schema = new Schema({
  _id: Schema.Types.ObjectId,           // explicit _id
  author: { type: Schema.Types.ObjectId, ref: 'User' }, // reference
});

// In interface:
interface IPost {
  author: Types.ObjectId;  // Use Types.ObjectId (NOT Schema.Types.ObjectId)
}
```

### Arrays

```typescript
const schema = new Schema({
  tags: [String],                        // string[]
  scores: [{ type: Number }],           // number[]
  addresses: [{                          // embedded subdoc array
    street: String,
    city: { type: String, required: true },
    zip: String,
  }],
  refs: [{ type: Schema.Types.ObjectId, ref: 'Other' }], // ObjectId[]
});

// Interface for subdoc arrays:
interface IUser {
  tags: string[];
  addresses: Array<{ street?: string; city: string; zip?: string }>;
  refs: Types.ObjectId[];
}
```

**Hydrated array subdocuments** (when you need subdoc methods like `.id()`, `.remove()`):

```typescript
import { HydratedArraySubdocument, HydratedDocument } from 'mongoose';

type AddressSubdoc = HydratedArraySubdocument<{ street?: string; city: string }>;
type UserDoc = HydratedDocument<IUser, { addresses: AddressSubdoc[] }>;
```

### Maps

```typescript
const schema = new Schema({
  metadata: { type: Map, of: String },            // Map<string, string>
  settings: { type: Map, of: Schema.Types.Mixed }, // Map<string, any>
  social: {                                        // Map with ref
    type: Map,
    of: { type: Schema.Types.ObjectId, ref: 'Social' },
  },
});

// Interface:
interface IUser {
  metadata?: Map<string, string>;
  settings?: Map<string, any>;
}

// Access: doc.metadata.get('key'), doc.metadata.set('key', 'value')
// Populate maps: .populate('social.$*')
```

### Nested Objects vs Subdocuments

```typescript
// Nested object (no _id, no middleware)
const schema = new Schema({
  name: {
    first: { type: String, required: true },
    last: String,
  }
});

// Subdocument (has _id, supports middleware) — use separate Schema
const nameSchema = new Schema({
  first: { type: String, required: true },
  last: String,
});

const schema = new Schema({
  name: { type: nameSchema, required: true },
});
```

### Enums (Type-Safe)

```typescript
// With InferSchemaType
const schema = new Schema({
  role: { type: String, enum: ['admin', 'user', 'moderator'] as const },
  status: { type: String, enum: ['active', 'inactive'] as const, required: true },
});
type IUser = InferSchemaType<typeof schema>;
// role?: 'admin' | 'user' | 'moderator' | null
// status: 'active' | 'inactive'

// With separate interface
type Role = 'admin' | 'user' | 'moderator';
interface IUser {
  role: Role;
}
const schema = new Schema<IUser>({
  role: { type: String, enum: ['admin', 'user', 'moderator'] },
});
```

### Timestamps

```typescript
// Automatic with InferSchemaType (Mongoose adds createdAt, updatedAt)
const schema = new Schema({ name: String }, { timestamps: true });
type IUser = InferSchemaType<typeof schema>;
// includes createdAt?: Date, updatedAt?: Date

// With separate interface — declare explicitly
interface IUser {
  name?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### Mixed / Any Type

```typescript
const schema = new Schema({
  anything: Schema.Types.Mixed,   // any
  alsoAnything: {},               // any
});
// Changes to Mixed fields require markModified():
// doc.anything = { foo: 'bar' };
// doc.markModified('anything');
// doc.save();
```

## RawDocType vs HydratedDocument

| | RawDocType | HydratedDocument |
|---|---|---|
| **What** | Plain data shape | Mongoose document instance |
| **Has** | Just fields | Fields + methods + virtuals + save() |
| **Use for** | Interface definition, API responses | Working with docs in code |
| **Get via** | `InferSchemaType<typeof schema>` | `new Model()`, `findOne()`, etc. |
| **Lean** | What `.lean()` returns | What queries return (without lean) |

```typescript
import { HydratedDocument } from 'mongoose';

type UserDocument = HydratedDocument<IUser>;

// Or derive from model:
type UserDocument = ReturnType<(typeof UserModel)['hydrate']>;
```
