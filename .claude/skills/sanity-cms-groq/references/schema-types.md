# Schema Types

## Core Helpers

```typescript
import { defineType, defineField, defineArrayMember } from "sanity";
```

- `defineType` — Define a top-level schema type (document, object, array)
- `defineField` — Define a field within a type
- `defineArrayMember` — Define an item type within an array field

## Document Type

The primary building block — has its own page in Studio, queryable by `_type`:

```typescript
// sanity/schemas/postType.ts
import { defineField, defineType } from "sanity";

export const postType = defineType({
  name: "post",
  title: "Post",
  type: "document",
  fields: [
    defineField({
      name: "title",
      type: "string",
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: "slug",
      type: "slug",
      options: { source: "title" },
      validation: (rule) => rule.required(),
    }),
    defineField({
      name: "publishedAt",
      type: "datetime",
      initialValue: () => new Date().toISOString(),
    }),
    defineField({
      name: "author",
      type: "reference",
      to: [{ type: "author" }],
    }),
    defineField({
      name: "categories",
      type: "array",
      of: [defineArrayMember({ type: "reference", to: [{ type: "category" }] })],
    }),
    defineField({
      name: "mainImage",
      type: "image",
      options: { hotspot: true },
      fields: [
        defineField({
          name: "alt",
          type: "string",
          title: "Alternative text",
        }),
      ],
    }),
    defineField({
      name: "body",
      type: "array",
      of: [defineArrayMember({ type: "block" })],
    }),
  ],
  preview: {
    select: {
      title: "title",
      media: "mainImage",
      subtitle: "author.name",
    },
  },
});
```

## All Field Types

### Primitive Types

| Type | TypeScript | Example |
|------|-----------|---------|
| `string` | `string` | Short text |
| `text` | `string` | Multi-line text (textarea) |
| `number` | `number` | Integer or float |
| `boolean` | `boolean` | Toggle |
| `datetime` | `string` (ISO 8601) | Date + time picker |
| `date` | `string` (YYYY-MM-DD) | Date picker |
| `url` | `string` | URL input with validation |
| `email` | `string` | Email input |
| `phone` | `string` | Phone number |

### Complex Types

```typescript
// Slug — generates URL-safe strings
defineField({
  name: "slug",
  type: "slug",
  options: {
    source: "title",           // Field to generate from
    maxLength: 96,             // Max characters
    slugify: (input) =>        // Custom slugify function
      input.toLowerCase().replace(/\s+/g, "-").slice(0, 96),
  },
})
// Stored as: { current: "my-post-title", _type: "slug" }
// Query: slug.current

// Image
defineField({
  name: "mainImage",
  type: "image",
  options: {
    hotspot: true,       // Enable hotspot/crop tool in Studio
    accept: "image/*",   // Accepted file types
    storeOriginalFilename: true,
  },
  fields: [              // Extend with additional fields
    defineField({ name: "alt", type: "string" }),
    defineField({ name: "caption", type: "string" }),
  ],
})
// Stored as: { _type: "image", asset: { _ref: "image-...", _type: "reference" }, hotspot: {...}, crop: {...} }

// File (non-image)
defineField({
  name: "attachment",
  type: "file",
  options: { accept: ".pdf,.doc,.docx" },
})

// Geopoint
defineField({
  name: "location",
  type: "geopoint",
})
// Stored as: { lat: 37.77, lng: -122.41, alt: 30 }
```

### Reference Types

```typescript
// Single reference
defineField({
  name: "author",
  type: "reference",
  to: [{ type: "author" }],   // Array: can reference multiple types
  options: {
    disableNew: true,          // Prevent creating new from this field
    filter: "_type == 'author' && !archived", // Pre-filter in picker
  },
})
// Stored as: { _type: "reference", _ref: "document-id" }
// Query: author->name (dereference)

// Cross-dataset reference (Sanity v3)
defineField({
  name: "externalRef",
  type: "crossDatasetReference",
  to: [{ type: "product", preview: { select: { title: "title" } } }],
  projectId: "other-project-id",
  dataset: "production",
  tokenId: "token-id",
})
```

### Array Types

```typescript
// Array of primitives
defineField({
  name: "tags",
  type: "array",
  of: [{ type: "string" }],
  options: {
    layout: "tags",  // Tag input UI
    list: [          // Predefined options
      { value: "news", title: "News" },
      { value: "tutorial", title: "Tutorial" },
    ],
  },
})

// Array of objects
defineField({
  name: "sections",
  type: "array",
  of: [
    defineArrayMember({
      type: "object",
      name: "section",
      fields: [
        defineField({ name: "heading", type: "string" }),
        defineField({ name: "content", type: "text" }),
      ],
    }),
  ],
})

// Portable Text (rich text)
defineField({
  name: "body",
  type: "array",
  of: [defineArrayMember({ type: "block" })],
})

// Portable Text with images + custom types
defineField({
  name: "content",
  type: "array",
  of: [
    defineArrayMember({ type: "block" }),
    defineArrayMember({
      type: "image",
      options: { hotspot: true },
      fields: [defineField({ name: "alt", type: "string" })],
    }),
    // Custom block type
    defineArrayMember({
      name: "callout",
      type: "object",
      fields: [
        defineField({ name: "text", type: "string" }),
        defineField({
          name: "tone",
          type: "string",
          options: { list: ["info", "warning", "error"] },
        }),
      ],
    }),
  ],
})
```

### Object Type

Named reusable object (not a document — no `_id`):

```typescript
// sanity/schemas/addressType.ts
export const addressType = defineType({
  name: "address",
  type: "object",
  fields: [
    defineField({ name: "street", type: "string" }),
    defineField({ name: "city", type: "string" }),
    defineField({ name: "country", type: "string" }),
    defineField({ name: "postalCode", type: "string" }),
  ],
})

// Use in another schema:
defineField({
  name: "shippingAddress",
  type: "address",  // Reference the named object type
})
```

## Validation

```typescript
// String validation
validation: (rule) => rule
  .required()
  .min(3)
  .max(100)
  .regex(/^[a-z0-9-]+$/, "Lowercase, numbers and hyphens only"),

// Number validation
validation: (rule) => rule
  .required()
  .min(0)
  .max(100)
  .integer(),

// Custom validation
validation: (rule) => rule.custom((value) => {
  if (!value) return true;  // Allow empty
  if (value.length > 100) return "Must be under 100 characters";
  return true;
}),

// Async custom validation
validation: (rule) => rule.custom(async (value, context) => {
  // context.document = full parent document
  // context.getClient() = Sanity client for DB checks
  const client = context.getClient({ apiVersion: "2024-01-01" });
  const existing = await client.fetch(
    `count(*[_type == "post" && slug.current == $slug && _id != $id])`,
    { slug: value?.current, id: context.document?._id },
  );
  return existing === 0 ? true : "Slug must be unique";
}),

// Conditional validation
validation: (rule) => rule.custom((value, context) => {
  if (context.document?.isPublished && !value) {
    return "Required for published posts";
  }
  return true;
}),
```

## Ordering & Preview

```typescript
// Document ordering in Studio
orderings: [
  {
    title: "Published (newest first)",
    name: "publishedAtDesc",
    by: [{ field: "publishedAt", direction: "desc" }],
  },
],

// Preview card in Studio list
preview: {
  select: {
    title: "title",
    subtitle: "author.name",  // Can dereference one level
    media: "mainImage",
  },
  prepare({ title, subtitle, media }) {
    return {
      title: title ?? "Untitled",
      subtitle: subtitle ? `by ${subtitle}` : "No author",
      media,
    };
  },
},
```

## Registering Schemas

```typescript
// sanity/schemas/index.ts
import { postType } from "./postType";
import { authorType } from "./authorType";
import { categoryType } from "./categoryType";

export const schemaTypes = [postType, authorType, categoryType];

// sanity.config.ts
import { defineConfig } from "sanity";
import { schemaTypes } from "./sanity/schemas";

export default defineConfig({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  schema: {
    types: schemaTypes,
  },
});
```
