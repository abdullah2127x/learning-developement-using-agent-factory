# Zod Schema Patterns for Forms

## Core Types

```ts
import { z } from 'zod'

// Primitives
z.string()
z.number()
z.boolean()
z.date()
z.bigint()
z.undefined()
z.null()
z.any()

// Literals & Enums
z.literal('admin')
z.enum(['admin', 'user', 'guest'])
z.nativeEnum(MyEnum) // TypeScript enum

// Objects
z.object({ name: z.string(), age: z.number() })

// Arrays
z.array(z.string())
z.string().array() // equivalent
```

---

## String Validations

```ts
z.string()
  .min(1, 'Required')             // Non-empty (use for required fields)
  .max(100, 'Too long')
  .email('Invalid email')
  .url('Invalid URL')
  .uuid('Invalid UUID')
  .regex(/^[a-z]+$/, 'Lowercase only')
  .startsWith('https://')
  .endsWith('.com')
  .trim()                          // Transform: strip whitespace
  .toLowerCase()                   // Transform: lowercase
  .toUpperCase()                   // Transform: uppercase
```

## Number Validations

```ts
z.number()
  .min(0, 'Must be positive')
  .max(100, 'Max 100')
  .int('Must be whole number')
  .positive('Must be positive')
  .nonnegative('Cannot be negative')
  .finite()
  .multipleOf(5, 'Must be multiple of 5')

// Coerce string → number (useful for form inputs)
z.coerce.number().min(1)
```

## Date Validations

```ts
z.date()
  .min(new Date('2020-01-01'), 'Too old')
  .max(new Date(), 'Cannot be in future')

// Coerce string → Date
z.coerce.date()
```

---

## Optional, Nullable, Default

```ts
z.string().optional()      // string | undefined
z.string().nullable()      // string | null
z.string().nullish()       // string | null | undefined
z.string().default('N/A')  // Fills in default if undefined

// Common form pattern: optional but validated when provided
z.string().optional().or(z.literal('')) // allow empty string
z.string().min(1).or(z.literal(''))     // validate if non-empty
```

---

## Object Schemas

```ts
const UserSchema = z.object({
  name: z.string().min(1, 'Required'),
  email: z.string().email(),
  age: z.coerce.number().min(18),
  role: z.enum(['admin', 'user']),
  bio: z.string().max(500).optional(),
})

type User = z.infer<typeof UserSchema>
// { name: string; email: string; age: number; role: 'admin' | 'user'; bio?: string }

// Extend / Merge
const AdminSchema = UserSchema.extend({ permissions: z.array(z.string()) })

// Pick / Omit
const LoginSchema = UserSchema.pick({ email: true })
const PublicSchema = UserSchema.omit({ role: true })

// Partial (all optional)
const UpdateSchema = UserSchema.partial()

// Deep partial
const PatchSchema = UserSchema.deepPartial()
```

---

## Array Schemas

```ts
z.array(z.object({
  name: z.string().min(1, 'Required'),
  quantity: z.coerce.number().min(1),
}))
  .min(1, 'Add at least one item')
  .max(10, 'Maximum 10 items')
```

---

## Cross-Field Validation (.refine)

```ts
const PasswordSchema = z.object({
  password: z.string().min(8, 'Min 8 characters'),
  confirm: z.string(),
}).refine(data => data.password === data.confirm, {
  message: "Passwords don't match",
  path: ['confirm'],  // Error appears on confirm field
})
```

### Multiple Refinements

```ts
const DateRangeSchema = z.object({
  startDate: z.coerce.date(),
  endDate: z.coerce.date(),
}).refine(d => d.endDate > d.startDate, {
  message: 'End date must be after start date',
  path: ['endDate'],
}).refine(d => {
  const diff = d.endDate.getTime() - d.startDate.getTime()
  return diff <= 30 * 24 * 60 * 60 * 1000
}, {
  message: 'Range cannot exceed 30 days',
  path: ['endDate'],
})
```

---

## superRefine (Multiple Issues)

```ts
const schema = z.object({
  password: z.string(),
}).superRefine((data, ctx) => {
  if (data.password.length < 8) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'At least 8 characters',
      path: ['password'],
    })
  }
  if (!/[A-Z]/.test(data.password)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Must contain uppercase letter',
      path: ['password'],
    })
  }
  if (!/[0-9]/.test(data.password)) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Must contain a number',
      path: ['password'],
    })
  }
})
```

---

## Transform

Transform values during parsing (runs after validation):

```ts
const schema = z.object({
  email: z.string().email().transform(v => v.toLowerCase()),
  tags: z.string().transform(v => v.split(',').map(t => t.trim())),
  price: z.string().transform(v => parseFloat(v)),
})
```

---

## Discriminated Unions

For forms with conditional fields based on a selector:

```ts
const PaymentSchema = z.discriminatedUnion('method', [
  z.object({
    method: z.literal('credit_card'),
    cardNumber: z.string().min(16).max(16),
    cvv: z.string().min(3).max(4),
    expiry: z.string(),
  }),
  z.object({
    method: z.literal('bank_transfer'),
    accountNumber: z.string().min(10),
    routingNumber: z.string().min(9),
  }),
  z.object({
    method: z.literal('paypal'),
    paypalEmail: z.string().email(),
  }),
])
```

---

## Common Form Schema Patterns

### Contact Form

```ts
export const contactSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  email: z.string().email('Invalid email address'),
  subject: z.string().min(1, 'Subject is required').max(200),
  message: z.string().min(10, 'Message must be at least 10 characters').max(2000),
})
```

### Registration Form

```ts
export const registerSchema = z.object({
  username: z.string()
    .min(3, 'At least 3 characters')
    .max(20, 'Max 20 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, underscores'),
  email: z.string().email('Invalid email'),
  password: z.string()
    .min(8, 'At least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[0-9]/, 'Must contain a number'),
  confirmPassword: z.string(),
  acceptTerms: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the terms' }),
  }),
}).refine(d => d.password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
```

### Address Schema (Reusable)

```ts
export const addressSchema = z.object({
  street: z.string().min(1, 'Required'),
  city: z.string().min(1, 'Required'),
  state: z.string().min(1, 'Required'),
  zip: z.string().regex(/^\d{5}(-\d{4})?$/, 'Invalid ZIP code'),
  country: z.string().min(1, 'Required'),
})
```

---

## Type Inference

```ts
const schema = z.object({ name: z.string(), age: z.number() })

type FormInput = z.input<typeof schema>   // What goes IN (pre-transform)
type FormOutput = z.output<typeof schema>  // What comes OUT (post-transform)
type FormData = z.infer<typeof schema>     // Same as z.output (most common)
```
