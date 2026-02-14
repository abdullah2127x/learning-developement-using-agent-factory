# Relationships, Populate & Discriminators

## Relationship Patterns

### 1. References (ObjectId + populate)

Best for: entities accessed independently, many-to-many, large related docs.

```typescript
import { Schema, model, Types, HydratedDocument } from 'mongoose';

// User schema
const userSchema = new Schema({
  name: { type: String, required: true },
  email: { type: String, required: true },
}, { timestamps: true });

// Post schema — references User
const postSchema = new Schema({
  title: { type: String, required: true },
  content: { type: String, required: true },
  author: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
}, { timestamps: true });

const User = mongoose.models.User || model('User', userSchema);
const Post = mongoose.models.Post || model('Post', postSchema);
```

### 2. Embedded Subdocuments

Best for: data always accessed together, 1:1 or 1:few relationships.

```typescript
// Inline nested object (no _id, no middleware)
const userSchema = new Schema({
  name: String,
  address: {
    street: String,
    city: { type: String, required: true },
    zip: String,
    country: { type: String, default: 'US' },
  },
});

// Separate schema (has _id, supports middleware, validation)
const addressSchema = new Schema({
  street: String,
  city: { type: String, required: true },
  zip: String,
});

const userSchema = new Schema({
  name: String,
  address: { type: addressSchema, required: true },      // single subdoc
  addresses: [addressSchema],                             // array of subdocs
});
```

### 3. Hybrid (Embed + Reference)

Denormalize frequently-read fields, keep reference for full data:

```typescript
const commentSchema = new Schema({
  text: { type: String, required: true },
  // Embedded author summary (fast reads, no populate needed)
  author: {
    _id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    name: { type: String, required: true },
    avatar: String,
  },
});
```

---

## Populate with TypeScript

### Basic Populate (Recommended: Generic parameter)

```typescript
import { InferSchemaType } from 'mongoose';

type IUser = InferSchemaType<typeof userSchema>;
type IPost = InferSchemaType<typeof postSchema>;

// Untyped populate — author is still Types.ObjectId
const post = await Post.findById(id).populate('author');

// Typed populate — author becomes IUser
const post = await Post.findById(id)
  .populate<{ author: IUser }>('author')
  .orFail();

post.author.name; // string ✓ (typed!)
```

### Multi-field Populate

```typescript
const post = await Post.findById(id)
  .populate<{ author: IUser }>('author')
  .populate<{ tags: ITag[] }>('tags')
  .orFail();

post.author.name; // string ✓
post.tags[0].label; // string ✓
```

### Populate with Select

```typescript
const post = await Post.findById(id)
  .populate<{ author: Pick<IUser, 'name' | 'email'> }>('author', 'name email')
  .orFail();
```

### Nested Populate

```typescript
const post = await Post.findById(id)
  .populate<{ author: IUser & { company: ICompany } }>({
    path: 'author',
    populate: { path: 'company' },
  })
  .orFail();
```

### Populate with Conditions

```typescript
const posts = await Post.find()
  .populate<{ author: IUser | null }>({
    path: 'author',
    match: { role: 'admin' },  // only populate if author is admin
    select: 'name email',
  });
// author is null for non-admin authors
```

### PopulatedDoc (Alternative — NOT recommended)

```typescript
import { PopulatedDoc, Document, Types } from 'mongoose';

interface IPost {
  author: PopulatedDoc<Document<Types.ObjectId> & IUser>;
}
// Requires runtime instanceof checks — prefer generic populate approach
```

### Virtual Populate (Reverse references)

```typescript
// User doesn't store post IDs, but can "populate" posts
const userSchema = new Schema({ name: String }, {
  toJSON: { virtuals: true },
});

userSchema.virtual('posts', {
  ref: 'Post',
  localField: '_id',
  foreignField: 'author',
});

// Usage:
const user = await User.findById(id)
  .populate<{ posts: IPost[] }>('posts')
  .orFail();
```

### Populate Maps

```typescript
const teamSchema = new Schema({
  members: {
    type: Map,
    of: { type: Schema.Types.ObjectId, ref: 'User' },
  },
});

// Populate all map values with special $* syntax
const team = await Team.findById(id).populate('members.$*');
team.members.get('lead'); // populated User document

// Nested map populate
const schema = new Schema({
  projects: {
    type: Map,
    of: new Schema({
      title: String,
      owner: { type: Schema.Types.ObjectId, ref: 'User' },
    }),
  },
});
await Model.find().populate('projects.$*.owner');
```

---

## Discriminators (Single Collection Inheritance)

Different document shapes in ONE collection. Best for: events, notifications, content types, shapes.

### Basic Discriminator

```typescript
// Base schema
const eventSchema = new Schema(
  { timestamp: { type: Date, default: Date.now }, user: String },
  { discriminatorKey: 'kind' }  // field that stores the type
);
const Event = model('Event', eventSchema);

// Discriminator 1: ClickEvent
const clickSchema = new Schema({ url: String, element: String });
const ClickEvent = Event.discriminator('Click', clickSchema);

// Discriminator 2: PurchaseEvent
const purchaseSchema = new Schema({
  product: String,
  amount: Number,
  currency: { type: String, default: 'USD' },
});
const PurchaseEvent = Event.discriminator('Purchase', purchaseSchema);
```

### Usage

```typescript
// Creating — saves to same 'events' collection
const click = await ClickEvent.create({ user: 'john', url: '/about', element: 'nav-link' });
const purchase = await PurchaseEvent.create({ user: 'john', product: 'widget', amount: 29.99 });

// Querying
const allEvents = await Event.find();           // returns all types
const clicks = await ClickEvent.find();          // only clicks
const purchases = await PurchaseEvent.find();    // only purchases

// Discriminator key is auto-set
click.kind; // 'Click'
purchase.kind; // 'Purchase'
```

### TypeScript Typing for Discriminators

```typescript
interface IEvent {
  timestamp: Date;
  user: string;
  kind: string;
}

interface IClick extends IEvent {
  url: string;
  element: string;
}

interface IPurchase extends IEvent {
  product: string;
  amount: number;
  currency: string;
}

const Event = model<IEvent>('Event', eventSchema);
const ClickEvent = Event.discriminator<IClick>('Click', clickSchema);
const PurchaseEvent = Event.discriminator<IPurchase>('Purchase', purchaseSchema);
```

### Embedded Discriminators (In Arrays)

```typescript
const batchSchema = new Schema({ events: [eventSchema] });

// Add discriminators to the array
const docArray = batchSchema.path('events') as Schema.Types.DocumentArray;
docArray.discriminator('Click', clickSchema);
docArray.discriminator('Purchase', purchaseSchema);

const Batch = model('Batch', batchSchema);

// Mixed types in one array
await Batch.create({
  events: [
    { kind: 'Click', url: '/home', element: 'btn' },
    { kind: 'Purchase', product: 'widget', amount: 10 },
  ],
});
```

### Single Nested Discriminators

```typescript
const shapeSchema = new Schema({ color: String }, { discriminatorKey: 'type' });
const containerSchema = new Schema({ shape: shapeSchema });

containerSchema.path('shape').discriminator('Circle', new Schema({ radius: Number }));
containerSchema.path('shape').discriminator('Square', new Schema({ side: Number }));

const Container = model('Container', containerSchema);

await Container.create({ shape: { type: 'Circle', color: 'red', radius: 5 } });
await Container.create({ shape: { type: 'Square', color: 'blue', side: 10 } });
```

### Discriminator Rules

1. Define hooks on schemas BEFORE calling `discriminator()`
2. Discriminator key (`kind` / `__t`) is immutable by default — use `overwriteDiscriminatorKey: true` to change
3. All discriminator docs live in the BASE model's collection
4. Base model queries return ALL types; discriminator queries filter by kind
5. Indexes on base schema apply to all discriminators

---

## .lean() for Performance

```typescript
// Returns plain JS objects (no Mongoose document overhead)
const users = await User.find().lean();
// users[0].save  → undefined (not a Mongoose doc)
// users[0].name  → string ✓

// Typed lean
interface IUser { name: string; email: string; }
const users = await User.find().lean<IUser[]>();

// Use lean for:
// - Read-only data (API responses, rendering)
// - Large result sets
// - Server Components in Next.js
// Don't use lean when:
// - You need to call .save(), virtuals, methods
// - You need change tracking
```
