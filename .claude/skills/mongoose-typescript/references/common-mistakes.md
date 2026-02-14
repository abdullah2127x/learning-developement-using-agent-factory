# Common Mistakes & Anti-Patterns

## 1. Missing strictNullChecks in tsconfig.json

```
// BAD: InferSchemaType won't infer correctly
// tsconfig.json: { "strict": false }

// GOOD: Required for automatic type inference
// tsconfig.json: { "compilerOptions": { "strict": true } }
```

## 2. Model Recompilation in Next.js

```typescript
// BAD: Throws OverwriteModelError on hot reload
export default model('User', userSchema);

// GOOD: Check if model already exists
export default mongoose.models.User || model('User', userSchema);
```

## 3. Schema Definition in Temporary Variable (Loses Type Inference)

```typescript
// BAD: TypeScript widens types, InferSchemaType gives any-like results
const definition = {
  name: { type: String, required: true },
};
const schema = new Schema(definition);

// GOOD: Define inline
const schema = new Schema({
  name: { type: String, required: true },
});

// GOOD: Use `as const` if you must separate
const definition = {
  name: { type: String, required: true },
} as const;
const schema = new Schema(definition);
```

## 4. Forgetting runValidators on Updates

```typescript
// BAD: Validators DON'T run on updates by default
await User.findByIdAndUpdate(id, { age: -5 }); // saves -5 even with min: 0

// GOOD: Always pass runValidators
await User.findByIdAndUpdate(id, { age: -5 }, { runValidators: true });
// Throws ValidationError
```

## 5. Treating `unique` as a Validator

```typescript
// BAD: Expecting unique to work like required/min/max
const schema = new Schema({
  email: { type: String, unique: true },
});
await doc.validate(); // Does NOT check uniqueness!

// GOOD: unique creates a MongoDB index; handle E11000 separately
try {
  await doc.save();
} catch (err: any) {
  if (err.code === 11000) {
    // Handle duplicate key
  }
}
```

## 6. Using Edge Runtime with Mongoose

```typescript
// BAD: Mongoose requires Node.js net API
export const runtime = 'edge';

// GOOD: Always use Node.js runtime
export const runtime = 'nodejs';
```

## 7. Not Using lean() for Read-Only Data

```typescript
// BAD: Full Mongoose document overhead for API response
const users = await User.find();
return NextResponse.json(users);

// GOOD: Plain objects, much faster, less memory
const users = await User.find().lean();
return NextResponse.json(users);
```

## 8. Passing Mongoose Documents to Client Components

```typescript
// BAD: Mongoose documents aren't serializable
const user = await User.findById(id);
return <ClientComponent user={user} />; // Error or data loss

// GOOD: Convert to plain object
const user = await User.findById(id).lean();
return <ClientComponent user={JSON.parse(JSON.stringify(user))} />;
// Or better: map to a typed plain object
```

## 9. Interface-Schema Mismatch (Silent Bugs)

```typescript
// BAD: Interface says optional, schema says required — no TS error
interface IUser {
  name?: string; // optional in TS
}
const schema = new Schema<IUser>({
  name: { type: String, required: true }, // required in Mongoose
});
// Mongoose validates at runtime but TS won't catch missing name at compile time

// GOOD: Match interface to schema
interface IUser {
  name: string; // required in TS too
}
```

## 10. Adding Middleware After model() Compilation

```typescript
// BAD: Hook never fires
const User = model('User', userSchema);
userSchema.pre('save', function() { /* ... */ });

// GOOD: Define all hooks BEFORE model()
userSchema.pre('save', function() { /* ... */ });
const User = model('User', userSchema);
```

## 11. Forgetting to await dbConnect()

```typescript
// BAD: Race condition — query may run before connection
export async function GET() {
  dbConnect(); // not awaited!
  const users = await User.find();
  return NextResponse.json(users);
}

// GOOD: Always await
export async function GET() {
  await dbConnect();
  const users = await User.find().lean();
  return NextResponse.json(users);
}
```

## 12. Hardcoding MONGODB_URI

```typescript
// BAD: Secret in source code
await mongoose.connect('mongodb+srv://user:pass@cluster.mongodb.net/db');

// GOOD: Environment variable
await mongoose.connect(process.env.MONGODB_URI!);
// Store in .env.local (git-ignored)
```

## 13. Not Handling ObjectId Validation in API Routes

```typescript
// BAD: Invalid ObjectId crashes with CastError
const user = await User.findById(params.id); // "abc" → CastError

// GOOD: Validate first
import { isValidObjectId } from 'mongoose';

if (!isValidObjectId(params.id)) {
  return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
}
const user = await User.findById(params.id);
```

## 14. Mixed Type Without markModified()

```typescript
// BAD: Changes to Mixed fields aren't detected
doc.metadata.newProp = 'value';
await doc.save(); // newProp NOT saved

// GOOD: Mark the path as modified
doc.metadata.newProp = 'value';
doc.markModified('metadata');
await doc.save(); // saved ✓
```

## 15. Forgetting toJSON/toObject Virtuals

```typescript
// BAD: Virtuals missing from API responses
schema.virtual('fullName').get(function() { return `${this.first} ${this.last}`; });
// res.json(doc) → { first: '...', last: '...' } — no fullName

// GOOD: Enable virtual serialization
const schema = new Schema({ ... }, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true },
});
```

## 16. Untyped Populate

```typescript
// BAD: author is still Types.ObjectId in TypeScript
const post = await Post.findById(id).populate('author');
post.author.name; // TS error: Property 'name' does not exist on ObjectId

// GOOD: Generic populate
const post = await Post.findById(id)
  .populate<{ author: IUser }>('author')
  .orFail();
post.author.name; // string ✓
```

---

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `OverwriteModelError` | Model registered twice (hot reload) | `mongoose.models.X \|\| model()` |
| `Cannot read 'prototype'` | ESM/CJS mismatch | Add `esmExternals: "loose"` to next.config |
| Types are `any` | Missing `strict: true` in tsconfig | Enable strictNullChecks |
| Validation not running on update | `runValidators` not set | Add `{ runValidators: true }` |
| Virtuals missing in response | toJSON not configured | Add `toJSON: { virtuals: true }` |
| `MissingSchemaError` | Model imported before connection | Ensure `dbConnect()` called first |
| Duplicate key E11000 | `unique` index violation | Handle in try/catch (not validation) |
| Populate returns ObjectId | Wrong type or missing ref | Check `ref` matches model name |
| Data not updating | Mixed type not marked modified | Use `markModified('path')` |
| Edge runtime crash | Mongoose needs Node.js net | Set `runtime = 'nodejs'` |
| `buffering timed out` | No active connection | Verify MONGODB_URI and `await dbConnect()` |
| Empty `_id` in subdocs | Using inline object not Schema | Use `new Schema()` for subdocs needing _id |
