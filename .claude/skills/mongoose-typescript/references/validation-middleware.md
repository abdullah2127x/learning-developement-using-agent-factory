# Validation & Middleware

## Built-in Validators

### All Types

```typescript
const schema = new Schema({
  name: { type: String, required: true },                    // must be present
  name2: { type: String, required: [true, 'Name is required'] }, // custom message
  name3: {
    type: String,
    required: function(this: any) { return this.role === 'admin'; }, // conditional
  },
});
```

### String Validators

```typescript
const schema = new Schema({
  email: {
    type: String,
    required: true,
    match: [/^\S+@\S+\.\S+$/, '{VALUE} is not a valid email'],
    minlength: [5, 'Must be at least 5 chars'],
    maxlength: [255, 'Must be at most 255 chars'],
    lowercase: true,   // auto-transform
    trim: true,         // auto-transform
  },
  role: {
    type: String,
    enum: {
      values: ['admin', 'user', 'moderator'],
      message: '{VALUE} is not a valid role',
    },
  },
});
```

### Number Validators

```typescript
const schema = new Schema({
  age: {
    type: Number,
    min: [0, 'Age cannot be negative'],
    max: [150, 'Age cannot exceed 150'],
    required: true,
  },
  rating: {
    type: Number,
    min: 1,
    max: 5,
  },
});
```

### Message Templates

- `{VALUE}` — the value being validated
- `{PATH}` — the field name
- `{KIND}` — the validator type
- `{MIN}` / `{MAX}` — min/max values

## Custom Validators

### Synchronous

```typescript
const userSchema = new Schema({
  phone: {
    type: String,
    validate: {
      validator: function (v: string) {
        return /\d{3}-\d{3}-\d{4}/.test(v);
      },
      message: (props: any) => `${props.value} is not a valid phone number!`,
    },
    required: [true, 'Phone number required'],
  },
});
```

### Asynchronous (returns Promise)

```typescript
const userSchema = new Schema({
  email: {
    type: String,
    validate: {
      validator: async function (v: string) {
        const count = await mongoose.model('User').countDocuments({ email: v });
        return count === 0; // unique check
      },
      message: 'Email already exists',
    },
  },
});
```

### Cross-Field Validation

```typescript
const schema = new Schema({
  startDate: { type: Date, required: true },
  endDate: {
    type: Date,
    required: true,
    validate: {
      validator: function (this: any, v: Date) {
        return v > this.startDate;
      },
      message: 'End date must be after start date',
    },
  },
});
```

## Validation Methods

```typescript
// Async
try {
  await doc.validate();
} catch (err) {
  if (err instanceof mongoose.Error.ValidationError) {
    for (const [field, error] of Object.entries(err.errors)) {
      console.log(`${field}: ${error.message}`);
    }
  }
}

// Sync
const error = doc.validateSync();
if (error) {
  // same error structure
}

// Validate specific paths only
await doc.validate(['name', 'email']);
```

## Validation Error Structure

```typescript
{
  errors: {
    fieldName: {
      message: 'Error message',
      kind: 'required' | 'min' | 'max' | 'enum' | 'user defined' | ...,
      path: 'fieldName',
      value: theInvalidValue,
      reason?: Error,  // for custom validators that throw
    }
  }
}
```

## Update Validators

**Off by default!** Must opt in:

```typescript
// Enable on individual operations
await Model.findOneAndUpdate(
  { _id: id },
  { $set: { age: -1 } },
  { runValidators: true, new: true }
);

await Model.updateMany(
  { status: 'active' },
  { $set: { role: 'invalid' } },
  { runValidators: true }
);
```

**Critical difference**: In update validators, `this` is the Query (not the document).
Access updated values with `this.get()`:

```typescript
schema.path('color').validate(function (value) {
  // In updates, `this` is the Query object
  if (this.get('name') === 'special') {
    return value === 'red';
  }
  return true;
});
```

**Only these operators trigger validation**: `$set`, `$unset`, `$push`, `$addToSet`, `$pull`, `$pullAll`

## `unique` Is NOT a Validator

```typescript
// unique creates a MongoDB index, NOT a Mongoose validator
email: { type: String, unique: true }

// It does NOT run during validate()
// It throws a MongoDB duplicate key error (E11000) on save
// Handle separately:
try {
  await doc.save();
} catch (err: any) {
  if (err.code === 11000) {
    // Duplicate key error
  }
}
```

---

## Middleware (Hooks)

### Four Types

| Type | `this` context | Triggered by |
|------|----------------|-------------|
| **Document** | Document instance | `validate`, `save`, `updateOne`, `deleteOne`, `init` |
| **Query** | Query object | `find`, `findOne`, `findOneAndUpdate`, `updateOne`, `updateMany`, `deleteOne`, `deleteMany` |
| **Aggregate** | Aggregation pipeline | `aggregate` |
| **Model** | Model | `bulkWrite`, `insertMany`, `createCollection` |

### Pre Hooks

```typescript
// Document pre-save (most common)
schema.pre('save', function (next) {
  // `this` is the document
  if (this.isModified('password')) {
    this.password = hashPassword(this.password);
  }
  next(); // or return (async functions auto-call next)
});

// Async version (preferred)
schema.pre('save', async function () {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 10);
  }
});

// Query pre-find
schema.pre('find', function () {
  // `this` is the Query
  this.where({ deleted: { $ne: true } }); // soft delete filter
});

// Pre-findOneAndUpdate
schema.pre('findOneAndUpdate', function () {
  this.set({ updatedAt: new Date() });
});
```

### Post Hooks

```typescript
// Document post-save
schema.post('save', function (doc) {
  console.log(`Document ${doc._id} saved`);
});

// Query post-find
schema.post('find', function (docs) {
  console.log(`Found ${docs.length} documents`);
});

// Async post hook
schema.post('save', async function (doc) {
  await sendWelcomeEmail(doc.email);
});
```

### Error Handling Middleware

```typescript
// Catches errors from save operations
schema.post('save', function (error: any, doc: any, next: Function) {
  if (error.name === 'MongoServerError' && error.code === 11000) {
    next(new Error('Duplicate key error: email already exists'));
  } else {
    next(error);
  }
});

// Catches errors from updates
schema.post('findOneAndUpdate', function (error: any, doc: any, next: Function) {
  if (error.name === 'ValidationError') {
    next(new Error('Update validation failed'));
  } else {
    next(error);
  }
});
```

### Disambiguating Document vs Query Middleware

`updateOne` and `deleteOne` exist as both document and query middleware:

```typescript
// Document middleware (this = document)
schema.pre('updateOne', { document: true, query: false }, function () {
  console.log('Updating doc:', this._id);
});

// Query middleware (this = query) — default
schema.pre('updateOne', { document: false, query: true }, function () {
  console.log('Update query:', this.getFilter());
});
```

### Critical Rules

1. **Define middleware BEFORE `model()` compilation** — hooks added after won't execute
2. **Define middleware BEFORE `discriminator()`** — same reason
3. **Validation runs before other pre-save hooks** — Mongoose registers validation as a pre-save hook automatically
4. **Skip middleware when needed**:

```typescript
await doc.save({ middleware: false });          // skip all
await doc.save({ middleware: { pre: false } }); // skip pre only
```

### Common Middleware Patterns

```typescript
// Auto-slug generation
schema.pre('save', function () {
  if (this.isModified('title')) {
    this.slug = this.title.toLowerCase().replace(/\s+/g, '-');
  }
});

// Cascade delete
schema.pre('deleteOne', { document: true, query: false }, async function () {
  await mongoose.model('Comment').deleteMany({ postId: this._id });
});

// Auto-populate
schema.pre('find', function () {
  this.populate('author', 'name avatar');
});

// Last modified timestamp
schema.pre('findOneAndUpdate', function () {
  this.set({ lastModified: new Date() });
});
```
