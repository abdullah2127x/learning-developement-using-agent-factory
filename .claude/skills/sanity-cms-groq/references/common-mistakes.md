# Common Mistakes & Anti-Patterns

## 1. Accessing slug.current Incorrectly

```typescript
// BAD: slug is an object, not a string
const slug = post.slug;  // { _type: "slug", current: "my-post" }
<a href={`/posts/${post.slug}`}>...</a>  // Renders: /posts/[object Object]

// GOOD: Extract .current in GROQ projection
*[_type == "post"] {
  "slug": slug.current   // Returns string
}

// OR access in TypeScript
<a href={`/posts/${post.slug.current}`}>...</a>
```

## 2. Displaying Image Asset Directly

```typescript
// BAD: asset._ref is a reference ID, not a URL
<img src={post.mainImage.asset._ref} />
// Renders: image-abc123-800x600-jpg (not a URL!)

// GOOD: Always use urlFor
import { urlFor } from "@/sanity/lib/image";
<img src={urlFor(post.mainImage).width(800).url()} />
```

## 3. Rendering Portable Text as JSON

```typescript
// BAD: Body is an array of block objects, not HTML
<div>{post.body}</div>  // Error or [object Object]
<div dangerouslySetInnerHTML={{ __html: post.body }} />  // Empty

// GOOD: Use @portabletext/react
import { PortableText } from "@portabletext/react";
<PortableText value={post.body} />
```

## 4. Using Plain Template Literals for Queries

```typescript
// BAD: TypeGen can't detect the query type
const POSTS_QUERY = groq`*[_type == "post"]{ _id, title }`;
// Also BAD:
const POSTS_QUERY = `*[_type == "post"]{ _id, title }`;

// GOOD: Use defineQuery for TypeGen support
import { defineQuery } from "next-sanity";
const POSTS_QUERY = defineQuery(`*[_type == "post"]{ _id, title }`);
```

## 5. Not Handling null on Queries

```typescript
// BAD: Crashes if post not found (null reference)
const post = await client.fetch(POST_QUERY, { slug });
return <h1>{post.title}</h1>;  // TypeError: Cannot read properties of null

// GOOD: Check for null
import { notFound } from "next/navigation";
const post = await client.fetch(POST_QUERY, { slug });
if (!post) notFound();
return <h1>{post.title}</h1>;
```

## 6. Using asset.url Instead of urlFor

```typescript
// BAD: Raw URL — no transformations, no format optimization
"imageUrl": mainImage.asset->url   // Direct URL, no CDN transforms

// GOOD: Fetch the image object and transform on frontend
mainImage  // Return the full image object
// Then on frontend:
urlFor(post.mainImage).width(800).auto("format").url()
```

## 7. Forgetting Array Brackets in GROQ References

```typescript
// BAD: categories is an array of references, not a single ref
"categories": categories->title  // Error: array, not single ref

// GOOD: Use [] for array dereferencing
"categories": categories[]->{_id, title}
```

## 8. Hardcoding apiVersion

```typescript
// BAD: No version pinning
const client = createClient({
  apiVersion: "latest"  // Will break when API changes!
});

// GOOD: Pin to a specific date
const client = createClient({
  apiVersion: "2024-01-01"  // Stable forever
});
```

## 9. Missing Required Query Parameters

```typescript
// BAD: $slug not passed to client.fetch
const post = await client.fetch(
  `*[_type == "post" && slug.current == $slug][0]`
  // Missing second argument!
);

// GOOD: Always pass parameters object
const post = await client.fetch(
  `*[_type == "post" && slug.current == $slug][0]`,
  { slug: params.slug }
);
```

## 10. Not Defining Schema Array Members with defineArrayMember

```typescript
// BAD: TypeScript inference is poor
defineField({
  name: "sections",
  type: "array",
  of: [{ type: "object", fields: [...] }],  // Loses TypeScript types
})

// GOOD: Use defineArrayMember
defineField({
  name: "sections",
  type: "array",
  of: [
    defineArrayMember({
      type: "object",
      name: "section",
      fields: [...],
    }),
  ],
})
```

## 11. Fetching All Fields Without Projection

```typescript
// BAD: Fetches entire document including all nested data
*[_type == "post"]  // Downloads everything including blobs

// GOOD: Always project to only what you need
*[_type == "post"] {
  _id,
  title,
  "slug": slug.current,
  publishedAt
}
```

## 12. Accessing SANITY_API_READ_TOKEN Client-Side

```typescript
// BAD: Token exposed to browser
const token = process.env.NEXT_PUBLIC_SANITY_API_READ_TOKEN;  // EXPOSED!

// GOOD: Server-side only (no NEXT_PUBLIC_ prefix)
const token = process.env.SANITY_API_READ_TOKEN;  // Server-side only
```

## 13. No revalidation Strategy on Sanity Data

```typescript
// BAD: Default Next.js 15 behavior — uncached, fetches on every request
const posts = await client.fetch(POSTS_QUERY);

// GOOD: Add caching strategy
// Time-based (ISR)
const posts = await sanityFetch({ query: POSTS_QUERY, revalidate: 3600 });
// Tag-based (webhook-triggered)
const posts = await sanityFetch({ query: POSTS_QUERY, tags: ["post"] });
// Static
export const revalidate = 3600;  // Page-level static revalidation
```

## 14. Defining Schema Types Without defineType/defineField

```typescript
// BAD: No TypeScript inference from schema builder
export const postType = {
  name: "post",
  type: "document",
  fields: [
    { name: "title", type: "string" },
  ],
}

// GOOD: Always use defineType and defineField
export const postType = defineType({
  name: "post",
  type: "document",
  fields: [
    defineField({ name: "title", type: "string" }),
  ],
})
```

---

## Debugging Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Image not displaying | Using raw `asset._ref` | Use `urlFor(image).url()` |
| `[object Object]` in URL | Using slug object, not `.current` | Extract `"slug": slug.current` in GROQ |
| Portable Text renders as `[object Object]` | Rendering raw array | Use `<PortableText value={body} />` |
| `null` reference error on fetch | Missing null check | `if (!post) notFound()` |
| References not expanding | Missing `->` in GROQ | Use `author->{name}` not `author` |
| TypeScript error on `client.fetch` | No TypeGen + no manual type | Use `defineQuery()` or pass generic `<Type>` |
| Schema types not in Studio | Not registered in `schema.types` | Add to `schemaTypes` array in `sanity/schemas/index.ts` |
| `$param` not substituted | Missing params object | Pass second arg to `client.fetch(query, { param: value })` |
| Stale content in production | Missing cache tags | Use `tags: ["post"]` in `sanityFetch` + webhook |
| Draft not showing | `useCdn: true` | Set `useCdn: false` and `perspective: "previewDrafts"` |
| `apiVersion` error | Invalid version | Use format `YYYY-MM-DD` (e.g., `"2024-01-01"`) |
| Image missing alt text | No `alt` field in schema | Add `defineField({ name: "alt", type: "string" })` to image fields |
