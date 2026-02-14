# Next.js Integration

## Architecture: Client Form + Server Action

```
[Client Component] — 'use client'
  ├── Zod schema (shared)
  ├── useForm + zodResolver (client validation)
  ├── handleSubmit → calls Server Action
  └── Displays errors, loading, success

[Server Action] — 'use server'
  ├── Same Zod schema (server validation)
  ├── Parse + validate input
  ├── Mutate database
  ├── Revalidate cache
  └── Return result or redirect
```

---

## Pattern 1: Direct Server Action Call

```tsx
// lib/schemas.ts — shared schema (no directive needed)
import { z } from 'zod'

export const contactSchema = z.object({
  name: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
  message: z.string().min(10, 'At least 10 characters'),
})

export type ContactFormData = z.infer<typeof contactSchema>
```

```tsx
// app/actions.ts
'use server'

import { contactSchema, type ContactFormData } from '@/lib/schemas'
import { revalidatePath } from 'next/cache'

export async function submitContact(data: ContactFormData) {
  // Server-side validation (defense in depth)
  const result = contactSchema.safeParse(data)
  if (!result.success) {
    return { success: false, errors: result.error.flatten().fieldErrors }
  }

  try {
    await db.contact.create({ data: result.data })
    revalidatePath('/messages')
    return { success: true }
  } catch {
    return { success: false, errors: { _form: ['Failed to submit'] } }
  }
}
```

```tsx
// app/contact/page.tsx
import { ContactForm } from './contact-form'

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-md p-6">
      <h1 className="text-2xl font-bold">Contact Us</h1>
      <ContactForm />
    </div>
  )
}
```

```tsx
// app/contact/contact-form.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { contactSchema, type ContactFormData } from '@/lib/schemas'
import { submitContact } from '@/app/actions'
import { useState } from 'react'

export function ContactForm() {
  const [serverError, setServerError] = useState<string>()
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: { name: '', email: '', message: '' },
  })

  const onSubmit = async (data: ContactFormData) => {
    setServerError(undefined)
    const result = await submitContact(data)

    if (result.success) {
      setSuccess(true)
      reset()
    } else {
      setServerError(result.errors?._form?.[0] ?? 'Something went wrong')
    }
  }

  if (success) {
    return (
      <div className="rounded-md bg-green-50 border border-green-200 p-4 mt-6">
        <p className="text-sm text-green-800">Message sent! We'll be in touch.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
      {serverError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3" role="alert">
          <p className="text-sm text-red-800">{serverError}</p>
        </div>
      )}

      {/* ... form fields with register + errors ... */}

      <button type="submit" disabled={isSubmitting}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white
          hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
        {isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  )
}
```

---

## Pattern 2: useActionState (Progressive Enhancement)

Works without JavaScript (forms submit natively):

```tsx
'use client'

import { useActionState } from 'react'
import { submitContact } from '@/app/actions'

const initialState = { message: '', success: false }

export function ContactForm() {
  const [state, formAction, pending] = useActionState(submitContact, initialState)

  return (
    <form action={formAction} className="space-y-4">
      <input name="name" required className="..." />
      <input name="email" type="email" required className="..." />
      <textarea name="message" required className="..." />

      {state.message && (
        <p className={state.success ? 'text-green-600' : 'text-red-600'}>
          {state.message}
        </p>
      )}

      <button type="submit" disabled={pending}>
        {pending ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
```

```tsx
// app/actions.ts
'use server'

export async function submitContact(prevState: any, formData: FormData) {
  const result = contactSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    message: formData.get('message'),
  })

  if (!result.success) {
    return { success: false, message: 'Validation failed' }
  }

  await db.contact.create({ data: result.data })
  return { success: true, message: 'Message sent!' }
}
```

### When to Use Which

| Pattern | Use When |
|---------|----------|
| `handleSubmit` → Server Action | Rich client validation, complex error display, multi-step |
| `useActionState` + `formAction` | Progressive enhancement, simple forms, works without JS |

---

## Pattern 3: Server-Side Field Errors

Map server validation errors back to RHF fields:

```tsx
const onSubmit = async (data: ContactFormData) => {
  const result = await submitContact(data)

  if (!result.success && result.fieldErrors) {
    // Map server errors to RHF fields
    Object.entries(result.fieldErrors).forEach(([field, messages]) => {
      setError(field as keyof ContactFormData, {
        type: 'server',
        message: (messages as string[])[0],
      })
    })
    return
  }

  if (result.success) {
    reset()
  }
}
```

---

## Redirect After Submit

```tsx
// app/actions.ts
'use server'

import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

export async function createPost(data: PostFormData) {
  const result = postSchema.safeParse(data)
  if (!result.success) return { errors: result.error.flatten().fieldErrors }

  const post = await db.post.create({ data: result.data })

  revalidatePath('/posts')  // BEFORE redirect
  redirect(`/posts/${post.id}`) // Throws — nothing runs after
}
```

---

## File Uploads

```tsx
// Schema — validate file on client
const schema = z.object({
  name: z.string().min(1),
  avatar: z
    .instanceof(FileList)
    .refine(files => files.length > 0, 'File required')
    .refine(files => files[0]?.size <= 5_000_000, 'Max 5MB')
    .refine(
      files => ['image/jpeg', 'image/png'].includes(files[0]?.type),
      'Only JPEG/PNG'
    ),
})

// In form
<input type="file" accept="image/*" {...register('avatar')} />

// In submit — use FormData for file upload
const onSubmit = async (data: z.infer<typeof schema>) => {
  const formData = new FormData()
  formData.append('name', data.name)
  formData.append('avatar', data.avatar[0])
  await uploadAction(formData)
}
```

---

## Shared Schema Pattern

```
lib/
├── schemas/
│   ├── contact.ts    # export const contactSchema = z.object({...})
│   ├── auth.ts       # export const loginSchema, registerSchema
│   └── index.ts      # barrel export
```

Both client form and server action import the same schema:

```tsx
// Client: useForm({ resolver: zodResolver(contactSchema) })
// Server: contactSchema.safeParse(data)
```

Single source of truth for types AND validation.
