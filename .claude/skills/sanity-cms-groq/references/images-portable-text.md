# Images & Portable Text

## Images with @sanity/image-url

### Setup

```bash
npm install @sanity/image-url
```

```typescript
// sanity/lib/image.ts
import createImageUrlBuilder from "@sanity/image-url";
import type { SanityImageSource } from "@sanity/image-url/lib/types/types";
import { client } from "./client";

const builder = createImageUrlBuilder(client);

export function urlFor(source: SanityImageSource) {
  return builder.image(source);
}
```

### urlFor Builder Methods

```typescript
// Basic usage
urlFor(post.mainImage).url()                      // Original URL
urlFor(post.mainImage).width(800).url()           // Fixed width
urlFor(post.mainImage).height(600).url()          // Fixed height
urlFor(post.mainImage).width(800).height(600).url() // Fixed both

// Quality + format
urlFor(post.mainImage)
  .width(800)
  .quality(80)
  .auto("format")              // WebP for supporting browsers
  .url()

// Fit modes
.fit("clip")                   // No cropping, scale to fit
.fit("crop")                   // Crop to fill (uses hotspot)
.fit("fill")                   // Fill area, letterbox
.fit("max")                    // Scale down to fit, no upscaling
.fit("scale")                  // Scale to exact dimensions

// Focal point (works with hotspot: true in schema)
.focalPoint(0.5, 0.3)         // x, y (0.0-1.0)

// Effects
.blur(10)                      // Blur (0-100)
.sharpen(10)                   // Sharpen (0-100)
.invert()                      // Invert colors
.orientation(90)               // Rotate

// Crop by rect
.rect(left, top, width, height) // Manual crop

// Background color (for transparent images)
.bg("ffffff")                  // Hex color
```

### With Next.js Image Component

```typescript
// components/SanityImage.tsx
import Image from "next/image";
import { urlFor } from "@/sanity/lib/image";
import type { SanityImageSource } from "@sanity/image-url/lib/types/types";

interface SanityImageProps {
  image: SanityImageSource & { alt?: string };
  width: number;
  height: number;
  className?: string;
  priority?: boolean;
}

export function SanityImage({ image, width, height, className, priority }: SanityImageProps) {
  const imageUrl = urlFor(image)
    .width(width)
    .height(height)
    .auto("format")
    .quality(80)
    .url();

  return (
    <Image
      src={imageUrl}
      alt={image.alt ?? ""}
      width={width}
      height={height}
      className={className}
      priority={priority}
    />
  );
}
```

### Responsive Image with srcSet

```typescript
// components/ResponsiveSanityImage.tsx
import Image from "next/image";
import { urlFor } from "@/sanity/lib/image";

export function ResponsiveSanityImage({ image, alt }: { image: any; alt: string }) {
  return (
    <Image
      src={urlFor(image).auto("format").quality(80).url()}
      alt={alt}
      fill                        // Fill parent container
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      className="object-cover"   // CSS fit
    />
  );
}
```

### Image in GROQ Query

When you need the image URL from GROQ directly:

```groq
*[_type == "post"] {
  title,
  // Get the full image object (for urlFor on frontend)
  mainImage,
  // OR get just the URL (less flexible, no transforms)
  "imageUrl": mainImage.asset->url,
  // Get blurred placeholder
  "imageLqip": mainImage.asset->metadata.lqip,
  // Get dominant color
  "imageDominantColor": mainImage.asset->metadata.palette.dominant.background
}
```

## Portable Text

### Schema Definition

```typescript
// Basic (blocks only)
defineField({
  name: "body",
  type: "array",
  of: [{ type: "block" }],
})

// Rich (blocks + images + custom types)
defineField({
  name: "content",
  type: "array",
  of: [
    { type: "block" },
    {
      type: "image",
      options: { hotspot: true },
      fields: [{ name: "alt", type: "string", title: "Alt text" }],
    },
    // Custom block types (rendered differently)
    {
      name: "callout",
      type: "object",
      title: "Callout Box",
      fields: [
        { name: "text", type: "string" },
        {
          name: "tone",
          type: "string",
          options: { list: ["info", "warning", "success", "error"] },
        },
      ],
    },
  ],
})
```

### Rendering with @portabletext/react

```bash
npm install @portabletext/react
```

```typescript
// components/PortableTextBody.tsx
import { PortableText } from "@portabletext/react";
import type { PortableTextBlock } from "@portabletext/types";
import Image from "next/image";
import { urlFor } from "@/sanity/lib/image";

interface Props {
  value: PortableTextBlock[];
}

export function PortableTextBody({ value }: Props) {
  return (
    <PortableText
      value={value}
      components={portableTextComponents}
    />
  );
}

const portableTextComponents = {
  // Custom block types (from schema `of` array)
  types: {
    image: ({ value }: any) => (
      <figure className="my-8">
        <Image
          src={urlFor(value).width(800).auto("format").url()}
          alt={value.alt ?? ""}
          width={800}
          height={600}
          className="rounded-lg"
        />
        {value.caption && (
          <figcaption className="text-center text-sm text-gray-500 mt-2">
            {value.caption}
          </figcaption>
        )}
      </figure>
    ),

    callout: ({ value }: any) => (
      <div className={`p-4 rounded-lg my-4 border-l-4 bg-${value.tone}-50`}>
        <p>{value.text}</p>
      </div>
    ),
  },

  // Custom mark renderers (inline formatting)
  marks: {
    // External link
    link: ({ children, value }: any) => {
      const isExternal = !value.href.startsWith("/");
      return (
        <a
          href={value.href}
          target={isExternal ? "_blank" : undefined}
          rel={isExternal ? "noreferrer noopener" : undefined}
          className="text-blue-600 underline"
        >
          {children}
        </a>
      );
    },

    // Internal link (reference)
    internalLink: ({ children, value }: any) => (
      <a href={`/${value.reference?.slug?.current}`} className="text-blue-600 underline">
        {children}
      </a>
    ),

    // Custom highlight
    highlight: ({ children }: any) => (
      <mark className="bg-yellow-100">{children}</mark>
    ),
  },

  // Block-level overrides (h1-h6, blockquote, etc.)
  block: {
    h1: ({ children }: any) => (
      <h1 className="text-4xl font-bold mt-8 mb-4">{children}</h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-3xl font-bold mt-8 mb-4">{children}</h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-2xl font-semibold mt-6 mb-3">{children}</h3>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic my-4">
        {children}
      </blockquote>
    ),
    normal: ({ children }: any) => (
      <p className="mb-4 leading-relaxed">{children}</p>
    ),
  },

  // List overrides
  list: {
    bullet: ({ children }: any) => (
      <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>
    ),
    number: ({ children }: any) => (
      <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>
    ),
  },

  listItem: {
    bullet: ({ children }: any) => <li className="ml-4">{children}</li>,
    number: ({ children }: any) => <li className="ml-4">{children}</li>,
  },
};
```

### Simple PortableText (no customization)

```typescript
import { PortableText } from "@portabletext/react";

// Default rendering — uses HTML defaults
export function SimpleBody({ content }: { content: any[] }) {
  return <PortableText value={content} />;
}
```

### Custom Annotation for Internal Links (Schema)

```typescript
// In your block definition
marks: {
  annotations: [
    {
      name: "internalLink",
      type: "object",
      title: "Internal Link",
      fields: [
        {
          name: "reference",
          type: "reference",
          to: [{ type: "post" }, { type: "page" }],
        },
      ],
    },
  ],
},
```

GROQ to dereference internal links:
```groq
body[]{
  ...,
  markDefs[]{
    ...,
    _type == "internalLink" => {
      "href": "/" + @.reference->slug.current
    }
  }
}
```

### Extracting Plain Text from Portable Text

```groq
// In GROQ query
"excerpt": pt::text(body)[0...200]

// On the server (TypeScript)
import { toPlainText } from "@portabletext/react";
const excerpt = toPlainText(post.body).slice(0, 200);
```
