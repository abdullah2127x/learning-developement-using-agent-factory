# Next.js App Router Integration

## Client Setup

```typescript
// sanity/lib/client.ts
import { createClient } from "next-sanity";

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: process.env.NEXT_PUBLIC_SANITY_API_VERSION ?? "2024-01-01",
  useCdn: true,          // true for production reads
  // token: process.env.SANITY_API_READ_TOKEN,  // For draft mode
});
```

**`apiVersion`**: Use a stable date string (`YYYY-MM-DD`). This pins you to a specific API version so your app doesn't break when Sanity updates the API.

**`useCdn: true`** caches responses at edge. Use `false` for:
- Draft/preview mode
- Server-Side Rendering with no caching
- Writes (always false for mutations)

## Environment Variables

```env
NEXT_PUBLIC_SANITY_PROJECT_ID="your-project-id"
NEXT_PUBLIC_SANITY_DATASET="production"
NEXT_PUBLIC_SANITY_API_VERSION="2024-01-01"
SANITY_API_READ_TOKEN=""      # For draft mode only (server-side only)
```

**Important**: `SANITY_API_READ_TOKEN` must NOT have `NEXT_PUBLIC_` prefix — it's server-only.

## Basic Fetch in Server Component

```typescript
// app/posts/page.tsx (Server Component)
import { client } from "@/sanity/lib/client";
import { POSTS_QUERY } from "@/sanity/lib/queries";

export default async function PostsPage() {
  // Default Next.js 15 behavior: no cache (cache: "no-store")
  // Add next.revalidate to opt into ISR
  const posts = await client.fetch(POSTS_QUERY);

  return (
    <ul>
      {posts.map((post) => (
        <li key={post._id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## sanityFetch Helper (Recommended)

Centralize caching options:

```typescript
// sanity/lib/client.ts
import { createClient, type QueryParams } from "next-sanity";

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: "2024-01-01",
  useCdn: true,
});

export async function sanityFetch<const QueryString extends string>({
  query,
  params = {},
  revalidate = 60,
  tags = [],
}: {
  query: QueryString;
  params?: QueryParams;
  revalidate?: number | false;
  tags?: string[];
}) {
  return client.fetch(query, params, {
    cache: "force-cache",
    next: {
      revalidate: tags.length ? false : revalidate,
      tags,
    },
  });
}
```

### Usage: Time-Based Revalidation (ISR)

```typescript
// app/posts/page.tsx
export default async function PostsPage() {
  const posts = await sanityFetch({
    query: POSTS_QUERY,
    revalidate: 3600,   // Revalidate every hour
  });
  return <PostList posts={posts} />;
}
```

### Usage: Tag-Based Revalidation

```typescript
// app/posts/[slug]/page.tsx
export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await sanityFetch({
    query: POST_QUERY,
    params: { slug: params.slug },
    tags: ["post"],    // Invalidated when this tag is triggered
  });
  return <Post post={post} />;
}
```

### Usage: No Cache (always fresh)

```typescript
const freshPosts = await sanityFetch({
  query: POSTS_QUERY,
  revalidate: 0,  // Always revalidate (no cache)
});
```

## Cache Revalidation (On-Demand)

### Webhook → Next.js Revalidate Route

When content is published in Sanity Studio:

```typescript
// app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { type NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const secret = req.nextUrl.searchParams.get("secret");

  if (secret !== process.env.SANITY_REVALIDATE_SECRET) {
    return NextResponse.json({ error: "Invalid secret" }, { status: 401 });
  }

  const body = await req.json();
  const documentType = body?.documentType ?? body?._type;

  // Revalidate by document type
  if (documentType) {
    revalidateTag(documentType);
  }

  // Or revalidate all
  revalidateTag("sanity");

  return NextResponse.json({ revalidated: true, time: Date.now() });
}
```

Set up a webhook in Sanity:
- URL: `https://yoursite.com/api/revalidate?secret=YOUR_SECRET`
- Trigger: `create`, `update`, `delete`
- Filter: optional GROQ filter

## Static Generation with generateStaticParams

```typescript
// app/posts/[slug]/page.tsx
import { client } from "@/sanity/lib/client";
import { defineQuery } from "next-sanity";

const SLUGS_QUERY = defineQuery(
  `*[_type == "post" && defined(slug.current)].slug.current`
);

export async function generateStaticParams() {
  const slugs = await client.fetch(SLUGS_QUERY);
  return slugs.map((slug) => ({ slug }));
}

export default async function PostPage({ params }: { params: { slug: string } }) {
  const post = await sanityFetch({
    query: POST_QUERY,
    params: { slug: params.slug },
    tags: ["post"],
  });

  if (!post) return notFound();
  return <Post post={post} />;
}
```

## Metadata Generation

```typescript
// app/posts/[slug]/page.tsx
import type { Metadata } from "next";

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = await sanityFetch({
    query: POST_QUERY,
    params: { slug: params.slug },
    tags: ["post"],
  });

  return {
    title: post?.title,
    description: post?.excerpt,
    openGraph: {
      images: post?.mainImage
        ? [urlFor(post.mainImage).width(1200).height(630).url()]
        : [],
    },
  };
}
```

## Draft Mode (Preview)

```typescript
// sanity/lib/client.ts — add token for drafts
export const previewClient = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: "2024-01-01",
  useCdn: false,          // No CDN for drafts
  token: process.env.SANITY_API_READ_TOKEN,
  perspective: "previewDrafts",  // Include draft documents
});
```

```typescript
// app/api/draft/enable/route.ts
import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const secret = searchParams.get("secret");
  const slug = searchParams.get("slug");

  if (secret !== process.env.SANITY_PREVIEW_SECRET) {
    return new Response("Invalid token", { status: 401 });
  }

  draftMode().enable();
  redirect(slug ?? "/");
}
```

## Common Sanity + Next.js File Structure

```
sanity/
  env.ts              # Project ID, dataset constants
  lib/
    client.ts         # createClient, sanityFetch
    image.ts          # urlFor builder
    queries.ts        # defineQuery exports
  schemas/
    index.ts          # Export all schema types
    postType.ts
    authorType.ts
sanity.config.ts      # Studio configuration
sanity.types.ts       # Generated by TypeGen
sanity-typegen.json   # TypeGen config
app/
  (studio)/
    studio/
      [[...tool]]/
        page.tsx      # Embedded Studio
  api/
    revalidate/
      route.ts        # Webhook handler
  posts/
    page.tsx          # List page
    [slug]/
      page.tsx        # Detail page
components/
  PortableTextBody.tsx
  SanityImage.tsx
```

## Embedded Studio (Next.js 13+)

Run Sanity Studio inside your Next.js app:

```typescript
// app/(studio)/studio/[[...tool]]/page.tsx
"use client";
import { NextStudio } from "next-sanity/studio";
import config from "@/sanity.config";

export default function StudioPage() {
  return <NextStudio config={config} />;
}
```

```typescript
// app/(studio)/studio/[[...tool]]/loading.tsx
import { NextStudioLoading } from "next-sanity/studio";
export default function Loading() {
  return <NextStudioLoading />;
}
```
