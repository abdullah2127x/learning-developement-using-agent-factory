# Server Actions & Forms

## What Are Server Actions?

Server Actions are async functions that run on the server, invoked from the client via forms or event handlers. They use the `'use server'` directive.

```tsx
// app/actions.ts
'use server'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.post.create({ data: { title, content } })
  revalidatePath('/posts')
}
```

---

## Defining Server Actions

### In a Separate File (Recommended for Client Components)

```tsx
// app/actions.ts
'use server'  // All exports become Server Actions

export async function createPost(formData: FormData) { /* ... */ }
export async function deletePost(formData: FormData) { /* ... */ }
```

### Inline in Server Components

```tsx
export default function Page() {
  async function handleSubmit(formData: FormData) {
    'use server'
    // ...
  }
  return <form action={handleSubmit}>...</form>
}
```

---

## Forms (Native HTML)

```tsx
import { createPost } from '@/app/actions'

export function CreateForm() {
  return (
    <form action={createPost}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

**Progressive enhancement**: Forms work even without JavaScript loaded.

---

## Form Validation with useActionState

```tsx
'use client'

import { useActionState } from 'react'
import { createUser } from '@/app/actions'

const initialState = { message: '' }

export function SignupForm() {
  const [state, formAction, pending] = useActionState(createUser, initialState)

  return (
    <form action={formAction}>
      <input type="email" name="email" required />
      <p aria-live="polite">{state?.message}</p>
      <button disabled={pending}>
        {pending ? 'Creating...' : 'Sign up'}
      </button>
    </form>
  )
}
```

```tsx
// app/actions.ts
'use server'

export async function createUser(prevState: any, formData: FormData) {
  const email = formData.get('email') as string

  if (!email.includes('@')) {
    return { message: 'Invalid email address' }
  }

  await db.user.create({ data: { email } })
  return { message: 'Account created!' }
}
```

---

## Pending State with useFormStatus

```tsx
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Saving...' : 'Save'}
    </button>
  )
}
```

**Must be a child of `<form>`** — cannot be used in the same component that renders the form.

---

## Event Handler Invocation

```tsx
'use client'

import { incrementLike } from './actions'
import { useState } from 'react'

export default function LikeButton({ initialLikes }: { initialLikes: number }) {
  const [likes, setLikes] = useState(initialLikes)

  return (
    <button onClick={async () => {
      const updated = await incrementLike()
      setLikes(updated)
    }}>
      {likes} likes
    </button>
  )
}
```

---

## Passing Actions as Props

```tsx
// Server Component
import ClientForm from './client-form'
import { updateItem } from './actions'

export default function Page() {
  return <ClientForm updateAction={updateItem} />
}
```

```tsx
// Client Component
'use client'
export default function ClientForm({
  updateAction,
}: {
  updateAction: (formData: FormData) => void
}) {
  return <form action={updateAction}>...</form>
}
```

---

## After Mutations: Revalidation & Redirect

```tsx
'use server'

import { revalidatePath } from 'next/cache'
import { updateTag } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const post = await db.post.create({
    data: {
      title: formData.get('title') as string,
      content: formData.get('content') as string,
    },
  })

  updateTag('posts')           // Immediate cache expire (read-your-writes)
  revalidatePath('/posts')     // Revalidate the posts page
  redirect(`/posts/${post.id}`) // Redirect (throws — nothing runs after)
}
```

**Order matters**: `revalidatePath`/`revalidateTag` BEFORE `redirect` — redirect throws and stops execution.

---

## Cookies in Server Actions

```tsx
'use server'

import { cookies } from 'next/headers'

export async function setTheme(theme: string) {
  const cookieStore = await cookies()
  cookieStore.set('theme', theme)
}

export async function getTheme() {
  const cookieStore = await cookies()
  return cookieStore.get('theme')?.value ?? 'light'
}
```

Setting cookies in a Server Action triggers a re-render of the current page/layouts.

---

## Input Validation (Zod)

Always validate server action inputs:

```tsx
'use server'

import { z } from 'zod'

const CreatePostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
})

export async function createPost(formData: FormData) {
  const result = CreatePostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  })

  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors }
  }

  await db.post.create({ data: result.data })
  revalidatePath('/posts')
}
```

---

## Optimistic Updates

```tsx
'use client'

import { useOptimistic } from 'react'
import { addTodo } from './actions'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: string) => [...state, { id: 'temp', text: newTodo }]
  )

  async function handleSubmit(formData: FormData) {
    const text = formData.get('text') as string
    addOptimisticTodo(text)     // Immediately show in UI
    await addTodo(formData)     // Server mutation
  }

  return (
    <>
      <form action={handleSubmit}>
        <input name="text" />
        <button type="submit">Add</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => <li key={todo.id}>{todo.text}</li>)}
      </ul>
    </>
  )
}
```

---

## Error Handling

```tsx
'use server'

export async function createPost(formData: FormData) {
  try {
    await db.post.create(...)
    revalidatePath('/posts')
    return { success: true }
  } catch (error) {
    // Don't expose internal errors to client
    return { success: false, message: 'Failed to create post' }
  }
}
```

For unrecoverable errors, `throw` — caught by nearest `error.tsx` boundary.

---

## Security Considerations

- Server Actions use POST method only
- Each action gets a unique, unguessable endpoint
- Always validate inputs (never trust `formData`)
- Always check authorization (who is making this request?)
- Use `server-only` package for modules with secrets
- Closures over sensitive data are encrypted by Next.js
