# TypeScript & TypeGen

## Two Approaches to TypeScript Types

| Approach | When to Use | How |
|----------|------------|-----|
| **TypeGen** (recommended) | Have Sanity CLI, running studio | Auto-generate from schema + queries |
| **Manual interfaces** | No CLI access, prototyping | Manually define types matching GROQ output |

## TypeGen (Automatic)

### Setup

```bash
npm install --save-dev @sanity/cli
# or use global
npm install -g @sanity/cli
```

### Configuration (sanity-typegen.json)

```json
{
  "path": "./src/**/*.{ts,tsx,js,jsx}",
  "schema": "schema.json",
  "generates": "./sanity.types.ts",
  "overloadClientMethods": true
}
```

### Workflow

```bash
# Step 1: Extract schema from Sanity Studio
npx sanity schema extract

# Step 2: Generate TypeScript types
npx sanity typegen generate

# Result: sanity.types.ts with all document types + query result types
```

### Add to package.json scripts

```json
{
  "scripts": {
    "typegen": "sanity schema extract && sanity typegen generate"
  }
}
```

### defineQuery — The Key for TypeGen

Use `defineQuery` instead of plain template literals so TypeGen can extract result types:

```typescript
// sanity/lib/queries.ts
import { defineQuery } from "next-sanity";

// TypeGen generates: PostsQueryResult type
export const POSTS_QUERY = defineQuery(`
  *[_type == "post" && defined(slug.current)] | order(publishedAt desc) [0...12] {
    _id,
    title,
    "slug": slug.current,
    publishedAt,
    "author": author->name,
    mainImage
  }
`);

// TypeGen generates: PostQueryResult type
export const POST_QUERY = defineQuery(`
  *[_type == "post" && slug.current == $slug][0] {
    _id,
    title,
    "slug": slug.current,
    publishedAt,
    body,
    mainImage,
    "author": author->{name, bio}
  }
`);
```

### Using Generated Types

```typescript
// Auto-typed when overloadClientMethods is true
import { client } from "@/sanity/lib/client";
import { POSTS_QUERY, POST_QUERY } from "@/sanity/lib/queries";

// TypeScript knows the return type automatically
const posts = await client.fetch(POSTS_QUERY);
// posts: PostsQueryResult

const post = await client.fetch(POST_QUERY, { slug: "hello-world" });
// post: PostQueryResult
```

### Generated types structure (sanity.types.ts)

After running TypeGen, the file contains:
```typescript
// Document types (one per schema type)
export type Post = {
  _id: string;
  _type: "post";
  _createdAt: string;
  _updatedAt: string;
  _rev: string;
  title?: string;
  slug?: Slug;
  publishedAt?: string;
  mainImage?: Image;
  body?: BlockContent;
};

// Query result types (one per defineQuery)
export type PostsQueryResult = Array<{
  _id: string;
  title: string | null;
  slug: string | null;
  publishedAt: string | null;
  author: string | null;
  mainImage: Image | null;
}>;

export type PostQueryResult = {
  _id: string;
  title: string | null;
  slug: string | null;
  // ...
} | null;
```

## Manual TypeScript Interfaces

When TypeGen isn't available, manually define types that match your GROQ projections:

### Document Types

```typescript
// types/sanity.ts
import type { PortableTextBlock } from "@portabletext/types";

// Matches Sanity's slug type
export interface SanitySlug {
  _type: "slug";
  current: string;
}

// Matches Sanity's image type
export interface SanityImage {
  _type: "image";
  asset: {
    _ref: string;
    _type: "reference";
  };
  hotspot?: {
    x: number;
    y: number;
    height: number;
    width: number;
  };
  crop?: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  alt?: string;
}

// Reference (before dereferencing)
export interface SanityReference {
  _ref: string;
  _type: "reference";
}

// Document base
export interface SanityDocument {
  _id: string;
  _type: string;
  _createdAt: string;
  _updatedAt: string;
  _rev: string;
}
```

### Query Result Types

Define types that match what your GROQ query returns (NOT the raw document):

```typescript
// types/posts.ts

// What the LIST query returns
export interface PostSummary {
  _id: string;
  title: string;
  slug: string;           // Note: slug.current extracted as string
  publishedAt: string;
  author: string;         // author->name extracted as string
  mainImage: SanityImage | null;
}

// What the DETAIL query returns
export interface PostDetail {
  _id: string;
  title: string;
  slug: string;
  publishedAt: string;
  body: PortableTextBlock[];
  mainImage: SanityImage | null;
  author: {
    name: string;
    bio: PortableTextBlock[] | null;
  } | null;
}
```

### Typing client.fetch

```typescript
// Without TypeGen — use generics
const posts = await client.fetch<PostSummary[]>(POSTS_QUERY);
const post = await client.fetch<PostDetail | null>(POST_QUERY, { slug });
```

## Sanity's Built-in Types

```typescript
import type {
  SanityDocument,
  SanityReference,
  SanityAsset,
  SanityImageObject,
  SanityImageHotspot,
  SanityImageCrop,
  SanityImageAsset,
  SanityImageMetadata,
} from "@sanity/types";

// Also from @portabletext/types
import type {
  PortableTextBlock,
  PortableTextMarkDefinition,
  PortableTextSpan,
} from "@portabletext/types";
```

## Type Utilities

```typescript
// Extract the value from a GROQ query result for a single field
type PostSlug = NonNullable<PostQueryResult>["slug"];

// Make a partial type for forms
type PostFormData = Pick<Post, "title" | "slug" | "publishedAt">;

// Type for image with alt required
type RequiredAltImage = SanityImage & { alt: string };
```

## TypeGen in CI/CD

```yaml
# .github/workflows/typegen.yml
name: Regenerate Types
on:
  push:
    paths:
      - 'sanity/schemas/**'
jobs:
  typegen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install
      - run: npm run typegen
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: regenerate sanity types"
          file_pattern: "sanity.types.ts"
```
