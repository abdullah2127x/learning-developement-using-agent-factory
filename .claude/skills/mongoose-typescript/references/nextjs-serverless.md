# Next.js Serverless Integration

## Connection Management

### The Problem: Connection Storming

In serverless (Vercel, AWS Lambda), each function invocation may create a new connection.
MongoDB has connection limits. Without caching, you'll hit `MongoServerError: too many open connections`.

### Solution: Cached Connection

Mongoose handles this automatically — calling `mongoose.connect()` when already connected is a no-op.

```typescript
// lib/db.ts
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

if (!MONGODB_URI) {
  throw new Error('Please define the MONGODB_URI environment variable in .env.local');
}

async function dbConnect(): Promise<typeof mongoose> {
  // Mongoose caches connections — safe to call multiple times
  if (mongoose.connections[0].readyState) {
    return mongoose;
  }
  await mongoose.connect(MONGODB_URI);
  return mongoose;
}

export default dbConnect;
```

### Alternative: Global Cache Pattern (for non-Mongoose drivers)

```typescript
// lib/db.ts — only needed if NOT using Mongoose's built-in caching
declare global {
  var mongoose: { conn: typeof import('mongoose') | null; promise: Promise<typeof import('mongoose')> | null };
}

let cached = global.mongoose;
if (!cached) {
  cached = global.mongoose = { conn: null, promise: null };
}

async function dbConnect() {
  if (cached.conn) return cached.conn;
  if (!cached.promise) {
    cached.promise = mongoose.connect(MONGODB_URI).then((m) => m);
  }
  cached.conn = await cached.promise;
  return cached.conn;
}
```

## Model Registration (Prevent Hot-Reload Errors)

**Critical for Next.js dev mode**: Hot Module Replacement re-executes model files.
Mongoose throws `OverwriteModelError` if you call `model()` twice with the same name.

```typescript
// models/User.ts — ALWAYS use this pattern
import mongoose, { Schema, model, InferSchemaType } from 'mongoose';

const userSchema = new Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  role: { type: String, enum: ['admin', 'user'] as const, default: 'user' },
}, { timestamps: true });

type IUser = InferSchemaType<typeof userSchema>;

// Check if model already exists before creating
const User = mongoose.models.User || model('User', userSchema);

export default User;
export type { IUser };
```

### With Methods/Statics (Typed)

```typescript
import mongoose, { Schema, model, Model, HydratedDocument } from 'mongoose';

interface IUser {
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface IUserMethods {
  isAdmin(): boolean;
}

interface UserModel extends Model<IUser, {}, IUserMethods> {
  findByEmail(email: string): Promise<HydratedDocument<IUser, IUserMethods> | null>;
}

const userSchema = new Schema<IUser, UserModel, IUserMethods>({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  role: { type: String, enum: ['admin', 'user'], default: 'user' },
}, { timestamps: true });

userSchema.method('isAdmin', function () {
  return this.role === 'admin';
});

userSchema.static('findByEmail', function (email: string) {
  return this.findOne({ email });
});

const User = (mongoose.models.User as UserModel) || model<IUser, UserModel>('User', userSchema);
export default User;
```

## next.config.js Configuration

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    esmExternals: "loose",
  },
  serverExternalPackages: ["mongoose"],
  // For older Next.js versions:
  // experimental: { serverComponentsExternalPackages: ["mongoose"] }
};

module.exports = nextConfig;
```

## Edge Runtime: NOT SUPPORTED

Mongoose requires Node.js `net` API, which Edge Runtime doesn't provide.

```typescript
// ALWAYS set this in Server Components and Route Handlers using Mongoose
export const runtime = 'nodejs';
// Never use: export const runtime = 'edge';
```

## App Router Patterns

### Route Handler (API Route)

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import dbConnect from '@/lib/db';
import User from '@/models/User';

export const runtime = 'nodejs';

export async function GET() {
  await dbConnect();
  const users = await User.find().lean();
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  await dbConnect();
  const body = await request.json();

  try {
    const user = await User.create(body);
    return NextResponse.json(user, { status: 201 });
  } catch (error: any) {
    if (error.name === 'ValidationError') {
      return NextResponse.json(
        { errors: Object.values(error.errors).map((e: any) => e.message) },
        { status: 400 }
      );
    }
    if (error.code === 11000) {
      return NextResponse.json({ error: 'Duplicate key' }, { status: 409 });
    }
    throw error;
  }
}
```

### Route Handler with Dynamic Params

```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import dbConnect from '@/lib/db';
import User from '@/models/User';
import { isValidObjectId } from 'mongoose';

export const runtime = 'nodejs';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  if (!isValidObjectId(id)) {
    return NextResponse.json({ error: 'Invalid ID' }, { status: 400 });
  }

  await dbConnect();
  const user = await User.findById(id).lean();
  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json(user);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await dbConnect();
  const body = await request.json();

  const user = await User.findByIdAndUpdate(id, body, {
    new: true,
    runValidators: true,
  }).lean();

  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json(user);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await dbConnect();
  const user = await User.findByIdAndDelete(id);
  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }
  return NextResponse.json({ message: 'Deleted' });
}
```

### Server Component

```typescript
// app/users/page.tsx
import dbConnect from '@/lib/db';
import User from '@/models/User';

export const runtime = 'nodejs';

export default async function UsersPage() {
  await dbConnect();
  const users = await User.find().sort({ createdAt: -1 }).lean();

  return (
    <div>
      <h1>Users</h1>
      {users.map((user) => (
        <div key={user._id.toString()}>
          <p>{user.name}</p>
          <p>{user.email}</p>
        </div>
      ))}
    </div>
  );
}
```

**Important**: Always convert `_id` to string in JSX: `user._id.toString()`.

### Server Action

```typescript
// app/actions/users.ts
'use server';

import dbConnect from '@/lib/db';
import User from '@/models/User';
import { revalidatePath } from 'next/cache';

export async function createUser(formData: FormData) {
  await dbConnect();

  const name = formData.get('name') as string;
  const email = formData.get('email') as string;

  try {
    await User.create({ name, email });
    revalidatePath('/users');
    return { success: true };
  } catch (error: any) {
    if (error.name === 'ValidationError') {
      return {
        success: false,
        errors: Object.fromEntries(
          Object.entries(error.errors).map(([k, v]: [string, any]) => [k, v.message])
        ),
      };
    }
    return { success: false, errors: { _form: 'Something went wrong' } };
  }
}
```

## Environment Variables

```bash
# .env.local
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/mydb?retryWrites=true&w=majority

# For local development
# MONGODB_URI=mongodb://localhost:27017/mydb
```

## Project Structure (Recommended)

```
app/
  api/
    users/
      route.ts          # CRUD route handler
      [id]/route.ts     # Single resource handler
  users/
    page.tsx            # Server Component (read)
  actions/
    users.ts            # Server Actions (write)
lib/
  db.ts                 # dbConnect function
models/
  User.ts               # Schema + type + model
  Post.ts
  index.ts              # Re-export: export { default as User } from './User';
types/
  index.ts              # Shared TypeScript types
```

## Serialization Gotchas

Mongoose documents are NOT plain objects. When passing to Client Components:

```typescript
// Option 1: lean() — returns plain objects
const users = await User.find().lean();

// Option 2: JSON.parse/stringify
const users = JSON.parse(JSON.stringify(await User.find()));

// Option 3: toObject() — per document
const user = (await User.findById(id))?.toObject();

// Dates become strings after serialization!
// ObjectIds become strings after serialization!
```
