# GROQ Query Language

## Basics

GROQ (Graph-Relational Object Queries) queries the Sanity Content Lake.

```groq
*                              // All documents
*[_type == "post"]             // Filter by type
*[_type == "post"][0]          // First result
*[_type == "post"][0...10]     // Slice (first 10)
*[_type == "post"][0..10]      // Inclusive slice (11 items)
```

## Filtering

```groq
// Equality
*[_type == "post" && status == "published"]

// Comparison
*[_type == "product" && price > 100]
*[_type == "event" && startDate >= "2024-01-01"]

// Boolean logic
*[_type == "post" && (featured == true || pinned == true)]

// Field existence
*[_type == "post" && defined(publishedAt)]
*[_type == "post" && !defined(archivedAt)]

// Text matching (glob)
*[_type == "post" && title match "React*"]

// Array membership
*[_type == "post" && "javascript" in tags]
*[_type == "post" && category._ref in ["id1", "id2"]]

// Reference check
*[_type == "post" && references("author-document-id")]

// Null check
*[_type == "post" && slug.current != null]

// Combined
*[_type == "post"
  && status == "published"
  && defined(slug.current)
  && publishedAt < now()
]
```

## Projections

```groq
// Select specific fields
*[_type == "post"] {
  _id,
  title,
  "slug": slug.current,     // Computed field (rename/transform)
  publishedAt
}

// Expand all fields + add computed
*[_type == "post"] {
  ...,                       // All original fields
  "wordCount": length(split(body, " "))
}

// Nested projection
*[_type == "post"] {
  title,
  "author": author->{        // Dereference + project
    name,
    "avatar": photo.asset->url
  }
}

// Slug — always extract .current
*[_type == "post"] {
  "slug": slug.current
}
```

## Ordering

```groq
// Single field
*[_type == "post"] | order(publishedAt desc)

// Multiple fields
*[_type == "post"] | order(featured desc, publishedAt desc)

// Ascending (default)
*[_type == "product"] | order(price asc)
```

## Dereferencing (References)

```groq
// Follow a reference
author->                     // Get full author document
author->name                 // Get single field
author->{name, bio, photo}   // Get projection

// Array of references
categories[]->               // Expand all references in array
categories[]->{title, slug}  // With projection

// Multiple hops
author->department->name     // Two levels deep
```

## Joins (Reverse References)

```groq
// Find all posts that reference an author (from author's perspective)
*[_type == "author"] {
  _id,
  name,
  "posts": *[_type == "post" && references(^._id)] {
    title,
    "slug": slug.current,
    publishedAt
  }
}

// Count related items
*[_type == "category"] {
  title,
  "postCount": count(*[_type == "post" && references(^._id)])
}
```

## Query Parameters

```groq
// Use $variables for parameterized queries
*[_type == "post" && slug.current == $slug][0]
*[_type == "post" && _id == $id][0]
*[_type == "post" && publishedAt > $after] | order(publishedAt desc) [0...$limit]
```

In TypeScript:
```typescript
const post = await client.fetch(
  `*[_type == "post" && slug.current == $slug][0]`,
  { slug: "hello-world" }
);
```

## GROQ Functions

```groq
// count — count items
count(*[_type == "post"])
count(categories)

// length — string length
length(title)

// defined — check if field exists
defined(publishedAt)

// now() — current ISO timestamp
*[_type == "event" && startDate >= now()]

// coalesce — first non-null value
"name": coalesce(fullName, username, "Anonymous")

// select — conditional expression
"label": select(
  featured == true => "Featured",
  status == "draft" => "Draft",
  "Published"
)

// pt::text — extract plain text from Portable Text
"excerpt": pt::text(body)

// string — cast to string
"id": string(_id)

// lower/upper — text case
"slug": lower(title)
```

## Common Query Patterns

### List page (all items)

```groq
*[_type == "post" && defined(slug.current)] | order(publishedAt desc) {
  _id,
  title,
  "slug": slug.current,
  publishedAt,
  "author": author->name,
  "categories": categories[]->{_id, title},
  "mainImage": mainImage.asset->url
}
```

### Detail page (single item by slug)

```groq
*[_type == "post" && slug.current == $slug][0] {
  _id,
  title,
  "slug": slug.current,
  publishedAt,
  body,
  mainImage,
  "author": author->{name, bio, "photo": photo.asset->url},
  "categories": categories[]->{_id, title}
}
```

### Home page (featured items)

```groq
{
  "featuredPosts": *[_type == "post" && featured == true] | order(publishedAt desc) [0...3] {
    _id, title, "slug": slug.current, publishedAt
  },
  "settings": *[_type == "siteSettings"][0] {
    title, description
  }
}
```

### Paginated list

```groq
*[_type == "post"] | order(publishedAt desc) [$offset...$offset + $limit] {
  _id, title, "slug": slug.current
}
```

### Filtering with Portable Text excerpt

```groq
*[_type == "post"] | order(publishedAt desc) [0...10] {
  _id,
  title,
  "slug": slug.current,
  "excerpt": pt::text(body)[0...150]
}
```

### Sitemap query

```groq
*[_type in ["post", "page"] && defined(slug.current)] {
  "slug": slug.current,
  _type,
  _updatedAt
}
```

### Search (text matching)

```groq
*[_type == "post" && (title match $q || pt::text(body) match $q)] {
  _id,
  title,
  "slug": slug.current
}
```

## Inline Object in GROQ

```groq
// Return a shaped object
{
  "hero": *[_type == "homePage"][0].hero,
  "posts": *[_type == "post"] | order(publishedAt desc) [0...6] {
    _id, title, "slug": slug.current
  }
}
```

## Array Operations in GROQ

```groq
// Access array element
*[_type == "post"] { "firstTag": tags[0] }

// Filter array elements
*[_type == "post"] {
  "publishedImages": images[status == "published"]
}

// Dereference array items
*[_type == "post"] {
  "tagNames": tags[]->name
}

// Array projection
*[_type == "movie"] {
  "actorNames": actors[].person->name
}
```

## Conditional Types in Projections

```groq
*[_type == "page"] {
  title,
  "heroType": hero._type,
  hero {
    _type == "heroImage" => {
      "imageUrl": image.asset->url,
      "alt": image.alt
    },
    _type == "heroVideo" => {
      videoUrl,
      thumbnail
    }
  }
}
```
