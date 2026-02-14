# Methods, Statics, Virtuals & Query Helpers

## Instance Methods

### Approach 1: Schema Options (Recommended — best type inference)

```typescript
import { Schema, model } from 'mongoose';

const userSchema = new Schema(
  {
    firstName: { type: String, required: true },
    lastName: { type: String, required: true },
    email: { type: String, required: true },
  },
  {
    methods: {
      fullName() {
        return `${this.firstName} ${this.lastName}`;
      },
      async updateEmail(newEmail: string) {
        this.email = newEmail;
        return this.save();
      },
    },
  }
);

const User = model('User', userSchema);
const user = new User({ firstName: 'John', lastName: 'Doe', email: 'j@d.com' });
user.fullName();      // string — auto-typed
user.updateEmail('new@email.com'); // Promise — auto-typed
```

### Approach 2: Separate Interface + Schema Generics

```typescript
import { Schema, model, Model, HydratedDocument } from 'mongoose';

interface IUser {
  firstName: string;
  lastName: string;
  email: string;
}

interface IUserMethods {
  fullName(): string;
  updateEmail(newEmail: string): Promise<HydratedDocument<IUser, IUserMethods>>;
}

// Pass methods as 3rd generic parameter
const userSchema = new Schema<IUser, Model<IUser>, IUserMethods>({
  firstName: { type: String, required: true },
  lastName: { type: String, required: true },
  email: { type: String, required: true },
});

userSchema.method('fullName', function fullName() {
  return `${this.firstName} ${this.lastName}`;
});

userSchema.method('updateEmail', function updateEmail(newEmail: string) {
  this.email = newEmail;
  return this.save();
});

const User = model<IUser, Model<IUser, {}, IUserMethods>>('User', userSchema);
```

## Static Methods

### Approach 1: Schema Options (Recommended)

```typescript
const userSchema = new Schema(
  { name: { type: String, required: true }, email: String },
  {
    statics: {
      findByEmail(email: string) {
        return this.findOne({ email });
      },
      async createWithDefaults(name: string) {
        return this.create({ name, email: `${name.toLowerCase()}@example.com` });
      },
    },
  }
);

const User = model('User', userSchema);
await User.findByEmail('test@test.com');  // auto-typed
```

### Approach 2: Extend Model Interface

```typescript
interface IUser {
  name: string;
  email: string;
}

interface UserModel extends Model<IUser> {
  findByEmail(email: string): Promise<HydratedDocument<IUser> | null>;
  createWithDefaults(name: string): Promise<HydratedDocument<IUser>>;
}

// Pass model type as 2nd generic
const userSchema = new Schema<IUser, UserModel>({
  name: { type: String, required: true },
  email: String,
});

userSchema.static('findByEmail', function (email: string) {
  return this.findOne({ email });
});

const User = model<IUser, UserModel>('User', userSchema);
await User.findByEmail('test@test.com'); // typed!
```

## Virtuals

### Approach 1: Schema Options (Recommended)

```typescript
const userSchema = new Schema(
  {
    firstName: { type: String, required: true },
    lastName: { type: String, required: true },
  },
  {
    virtuals: {
      fullName: {
        get() {
          return `${this.firstName} ${this.lastName}`;
        },
        set(v: string) {
          const [first, ...rest] = v.split(' ');
          this.firstName = first;
          this.lastName = rest.join(' ');
        },
      },
    },
    toJSON: { virtuals: true },  // include in JSON output
    toObject: { virtuals: true },
  }
);

const User = model('User', userSchema);
const user = new User({ firstName: 'John', lastName: 'Doe' });
user.fullName; // 'John Doe' — auto-typed
```

**Important**: `InferSchemaType` does NOT include virtuals. They're only available on hydrated documents (from model instances / queries).

### Approach 2: Manual Typing

```typescript
interface IUser {
  firstName: string;
  lastName: string;
}

interface IUserVirtuals {
  fullName: string;
}

type UserModelType = Model<IUser, {}, {}, {}, IUserVirtuals>;

const userSchema = new Schema<IUser, UserModelType, {}, {}, IUserVirtuals>(
  { firstName: String, lastName: String }
);

userSchema.virtual('fullName').get(function () {
  return `${this.firstName} ${this.lastName}`;
});
```

### Getting HydratedDocument Type with Virtuals

```typescript
// From model method
type UserDocument = ReturnType<(typeof User)['hydrate']>;

// Or explicit
type UserDocument = HydratedDocument<IUser, {}, IUserVirtuals>;
```

## Query Helpers

### Approach 1: Schema Options (Recommended)

```typescript
const projectSchema = new Schema(
  { name: String, stars: Number, archived: Boolean },
  {
    query: {
      byName(name: string) {
        return this.find({ name });
      },
      active() {
        return this.find({ archived: { $ne: true } });
      },
    },
  }
);

const Project = model('Project', projectSchema);
// Chainable!
await Project.find().active().byName('mongoose').sort({ stars: -1 });
```

### Approach 2: Manual Typing

```typescript
import { HydratedDocument, Model, QueryWithHelpers, Schema, model } from 'mongoose';

interface IProject {
  name?: string;
  stars?: number;
}

interface ProjectQueryHelpers {
  byName(name: string): QueryWithHelpers<
    HydratedDocument<IProject>[],
    HydratedDocument<IProject>,
    ProjectQueryHelpers
  >;
}

type ProjectModelType = Model<IProject, ProjectQueryHelpers>;

const schema = new Schema<IProject, ProjectModelType, {}, ProjectQueryHelpers>({
  name: String,
  stars: Number,
});

schema.query.byName = function (
  this: QueryWithHelpers<any, HydratedDocument<IProject>, ProjectQueryHelpers>,
  name: string
) {
  return this.find({ name });
};

const Project = model<IProject, ProjectModelType>('Project', schema);
await Project.find().where('stars').gt(1000).byName('mongoose');
```

## Combined: Methods + Statics + Virtuals + Query Helpers

### Schema Options (Recommended — all in one)

```typescript
const userSchema = new Schema(
  {
    firstName: { type: String, required: true },
    lastName: { type: String, required: true },
    email: { type: String, required: true },
    role: { type: String, enum: ['admin', 'user'] as const, default: 'user' },
  },
  {
    timestamps: true,
    methods: {
      async setRole(role: 'admin' | 'user') {
        this.role = role;
        return this.save();
      },
    },
    statics: {
      findByEmail(email: string) {
        return this.findOne({ email });
      },
      findAdmins() {
        return this.find({ role: 'admin' });
      },
    },
    virtuals: {
      fullName: {
        get() { return `${this.firstName} ${this.lastName}`; },
      },
    },
    query: {
      byRole(role: string) {
        return this.find({ role });
      },
    },
    toJSON: { virtuals: true },
  }
);

export default mongoose.models.User || model('User', userSchema);
```

### Separate Interfaces (When needed for complex cases)

```typescript
interface IUser {
  firstName: string;
  lastName: string;
  email: string;
  role: 'admin' | 'user';
}

interface IUserMethods {
  setRole(role: 'admin' | 'user'): Promise<any>;
}

interface IUserVirtuals {
  fullName: string;
}

interface IUserQueryHelpers {
  byRole(role: string): QueryWithHelpers<any, any, IUserQueryHelpers>;
}

interface UserModel extends Model<IUser, IUserQueryHelpers, IUserMethods, IUserVirtuals> {
  findByEmail(email: string): Promise<HydratedDocument<IUser, IUserMethods> | null>;
  findAdmins(): Promise<HydratedDocument<IUser, IUserMethods>[]>;
}

const userSchema = new Schema<IUser, UserModel, IUserMethods, IUserQueryHelpers, IUserVirtuals>({
  firstName: { type: String, required: true },
  lastName: { type: String, required: true },
  email: { type: String, required: true },
  role: { type: String, enum: ['admin', 'user'], default: 'user' },
});

// Then define each method/static/virtual/query helper...
```

## loadClass() Pattern

For class-based OOP style:

```typescript
interface RawDoc { name: string; }

class UserClass {
  // Instance method — annotate `this`
  greet(this: HydratedDocument<RawDoc>) {
    return `Hello, ${this.name}`;
  }

  // Static method
  static findByName(this: Model<RawDoc>, name: string) {
    return this.findOne({ name });
  }

  // Virtual getter (TS limitation: can't annotate `this` on getters)
  get upperName() {
    return (this as unknown as HydratedDocument<RawDoc>).name.toUpperCase();
  }
}

const schema = new Schema<RawDoc>({ name: String });
schema.loadClass(UserClass);
```

**Note**: The schema options approach is preferred over `loadClass()` for better automatic type inference.
