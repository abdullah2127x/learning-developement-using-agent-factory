---
name: react-hook-form-zod
description: |
  Build type-safe, validated forms in Next.js using React Hook Form, Zod schemas,
  and Tailwind CSS styling. This skill should be used when users need to create
  contact forms, registration forms, multi-step wizards, dynamic field arrays,
  or any form with validation. Covers useForm, zodResolver, Server Actions integration,
  Tailwind form components, and production patterns from simple to complex.
---

# React Hook Form + Zod + Tailwind Forms

Build type-safe, validated, beautifully styled forms for Next.js applications.

## What This Skill Does

- Creates forms with React Hook Form + Zod validation + Tailwind styling
- Builds reusable form field components with consistent error handling
- Implements multi-step form wizards with per-step validation
- Integrates with Next.js Server Actions for server-side mutations
- Handles dynamic field arrays, conditional fields, and complex schemas
- Provides production-ready form patterns with loading, error, and success states

## What This Skill Does NOT Do

- Build forms without React Hook Form (use native forms or Formik instead)
- Create backend validation logic (handles client-side + Server Action bridge)
- Design custom UI component libraries (uses Tailwind utility classes)
- Handle file upload infrastructure (covers the form input, not storage)

---

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Next.js version, existing form patterns, Tailwind config, component library |
| **Conversation** | Form fields, validation rules, submission target (Server Action, API, client) |
| **Skill References** | Patterns from `references/` — RHF API, Zod schemas, Tailwind styling |
| **User Guidelines** | Design system, accessibility requirements, error message style |

---

## Installation

```bash
npm install react-hook-form @hookform/resolvers zod
```

---

## Mental Model

```
Zod Schema (defines shape + rules)
    ↓ z.infer<typeof schema> → TypeScript type
    ↓ zodResolver(schema) → validation adapter
    ↓
React Hook Form (manages state + validation)
    ↓ useForm({ resolver }) → register, handleSubmit, errors
    ↓
Tailwind Components (render + style)
    ↓ Conditional error classes, focus rings, disabled states
    ↓
Server Action or API (processes data)
```

**Key insight**: Zod is the single source of truth for both TypeScript types AND validation rules. Define once, use everywhere.

---

## Quick Start

```tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
})

type FormData = z.infer<typeof schema>

export function ContactForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormData) => {
    await submitToServer(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Name</label>
        <input
          {...register('name')}
          className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm
            ${errors.name
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'}
            focus:outline-none focus:ring-2`}
        />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Email</label>
        <input
          {...register('email')}
          type="email"
          className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm
            ${errors.email
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'}
            focus:outline-none focus:ring-2`}
        />
        {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white
          hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500
          disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
```

---

## Decision Tree

```
What kind of form?
├── Simple (3-5 fields, one step)
│   → Single schema + useForm + register
├── With dynamic fields (add/remove items)
│   → useFieldArray + array schema
├── Multi-step wizard
│   → Per-step schemas + FormProvider + shared state
├── With controlled components (Select, DatePicker, etc.)
│   → Controller or useController
├── With Server Action submission
│   → handleSubmit → call server action → revalidate
└── With file upload
    → Separate handling, Zod custom validation
```

---

## Reusable Field Component Pattern

```tsx
// components/form-field.tsx
import { FieldError } from 'react-hook-form'

interface FormFieldProps {
  label: string
  error?: FieldError
  children: React.ReactNode
  description?: string
}

export function FormField({ label, error, children, description }: FormFieldProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      {description && <p className="mt-0.5 text-xs text-gray-500">{description}</p>}
      <div className="mt-1">{children}</div>
      {error && <p className="mt-1 text-sm text-red-600">{error.message}</p>}
    </div>
  )
}
```

```tsx
// components/input.tsx
import { forwardRef } from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ hasError, className = '', ...props }, ref) => (
    <input
      ref={ref}
      className={`block w-full rounded-md border px-3 py-2 text-sm shadow-sm
        placeholder:text-gray-400 focus:outline-none focus:ring-2
        disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
        ${hasError
          ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
          : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'}
        ${className}`}
      {...props}
    />
  )
)
Input.displayName = 'Input'
```

---

## Production Checklist

- [ ] Zod schema defined with clear error messages for every field
- [ ] `z.infer<typeof schema>` used as form type (single source of truth)
- [ ] `zodResolver(schema)` passed to `useForm`
- [ ] `defaultValues` provided for all fields (prevents uncontrolled→controlled warning)
- [ ] Error messages displayed for every field with `errors.fieldName?.message`
- [ ] `isSubmitting` used to disable button and show loading state
- [ ] Server Action validates with same Zod schema (defense in depth)
- [ ] `aria-invalid` set on inputs with errors for accessibility
- [ ] `field.id` used as key in useFieldArray (never array index)
- [ ] Number inputs use `valueAsNumber: true` in register options
- [ ] Cross-field validation uses `.refine()` with `path` targeting correct field
- [ ] Form tested with keyboard navigation and screen reader

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/react-hook-form-api.md` | useForm config, register, formState, modes, Controller, FormProvider, useFieldArray |
| `references/zod-schemas.md` | Schema types, refine, superRefine, transform, discriminatedUnion, error customization |
| `references/tailwind-forms.md` | Input/select/textarea/checkbox/radio styling, error states, dark mode, responsive layout |
| `references/nextjs-integration.md` | Server Actions, useActionState, server-side validation, revalidation, progressive enhancement |
| `references/advanced-patterns.md` | Multi-step wizards, dynamic fields, conditional schemas, file upload, dependent fields |
| `references/common-mistakes.md` | Anti-patterns, debugging, RHF + Zod gotchas |
