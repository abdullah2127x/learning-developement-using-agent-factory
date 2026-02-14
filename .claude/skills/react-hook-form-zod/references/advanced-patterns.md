# Advanced Form Patterns

## Multi-Step Form Wizard

### Architecture

```
FormProvider (shared form state across steps)
├── Step 1: Personal Info  → validate subset of schema
├── Step 2: Address        → validate subset of schema
├── Step 3: Review         → display all data
└── Submit: Full schema validation
```

### Implementation

```tsx
// lib/schemas/checkout.ts
import { z } from 'zod'

export const personalSchema = z.object({
  firstName: z.string().min(1, 'Required'),
  lastName: z.string().min(1, 'Required'),
  email: z.string().email(),
})

export const addressSchema = z.object({
  street: z.string().min(1, 'Required'),
  city: z.string().min(1, 'Required'),
  zip: z.string().regex(/^\d{5}$/, 'Invalid ZIP'),
})

export const checkoutSchema = personalSchema.merge(addressSchema)
export type CheckoutData = z.infer<typeof checkoutSchema>
```

```tsx
// components/checkout-wizard.tsx
'use client'

import { useState } from 'react'
import { useForm, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { checkoutSchema, personalSchema, addressSchema, type CheckoutData } from '@/lib/schemas/checkout'

const STEPS = [
  { title: 'Personal Info', schema: personalSchema, fields: ['firstName', 'lastName', 'email'] },
  { title: 'Address', schema: addressSchema, fields: ['street', 'city', 'zip'] },
  { title: 'Review', schema: null, fields: [] },
]

export function CheckoutWizard() {
  const [step, setStep] = useState(0)

  const methods = useForm<CheckoutData>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      firstName: '', lastName: '', email: '',
      street: '', city: '', zip: '',
    },
    mode: 'onBlur',
  })

  const nextStep = async () => {
    const currentFields = STEPS[step].fields as (keyof CheckoutData)[]
    const valid = await methods.trigger(currentFields)
    if (valid) setStep(s => s + 1)
  }

  const prevStep = () => setStep(s => s - 1)

  const onSubmit = async (data: CheckoutData) => {
    await submitCheckout(data)
  }

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        {/* Step indicator */}
        <div className="flex gap-2 mb-6">
          {STEPS.map((s, i) => (
            <div key={i} className={`flex-1 h-2 rounded ${i <= step ? 'bg-blue-600' : 'bg-gray-200'}`} />
          ))}
        </div>

        {step === 0 && <PersonalStep />}
        {step === 1 && <AddressStep />}
        {step === 2 && <ReviewStep />}

        <div className="flex gap-3 mt-6">
          {step > 0 && (
            <button type="button" onClick={prevStep}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm">
              Back
            </button>
          )}
          {step < STEPS.length - 1 ? (
            <button type="button" onClick={nextStep}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white">
              Next
            </button>
          ) : (
            <button type="submit" disabled={methods.formState.isSubmitting}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white
                disabled:opacity-50">
              {methods.formState.isSubmitting ? 'Submitting...' : 'Place Order'}
            </button>
          )}
        </div>
      </form>
    </FormProvider>
  )
}
```

```tsx
// Each step uses useFormContext — no prop drilling
function PersonalStep() {
  const { register, formState: { errors } } = useFormContext<CheckoutData>()

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">First Name</label>
        <input {...register('firstName')} className={inputClasses(!!errors.firstName)} />
        {errors.firstName && <p className="mt-1 text-sm text-red-600">{errors.firstName.message}</p>}
      </div>
      {/* ... lastName, email ... */}
    </div>
  )
}
```

---

## Dynamic Field Arrays

```tsx
'use client'

import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  teamName: z.string().min(1, 'Required'),
  members: z.array(z.object({
    name: z.string().min(1, 'Name required'),
    role: z.enum(['developer', 'designer', 'manager']),
    email: z.string().email('Invalid email'),
  })).min(1, 'Add at least one member').max(10, 'Max 10 members'),
})

type FormData = z.infer<typeof schema>

export function TeamForm() {
  const { register, control, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      teamName: '',
      members: [{ name: '', role: 'developer', email: '' }],
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'members' })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium">Team Name</label>
        <input {...register('teamName')} className="..." />
        {errors.teamName && <p className="text-sm text-red-600">{errors.teamName.message}</p>}
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-medium">Members</h3>

        {fields.map((field, index) => (
          <div key={field.id} className="flex gap-3 items-start p-4 border rounded-md">
            <div className="flex-1">
              <input {...register(`members.${index}.name`)} placeholder="Name" className="..." />
              {errors.members?.[index]?.name && (
                <p className="text-xs text-red-600">{errors.members[index].name.message}</p>
              )}
            </div>
            <div className="flex-1">
              <select {...register(`members.${index}.role`)} className="...">
                <option value="developer">Developer</option>
                <option value="designer">Designer</option>
                <option value="manager">Manager</option>
              </select>
            </div>
            <div className="flex-1">
              <input {...register(`members.${index}.email`)} placeholder="Email" className="..." />
              {errors.members?.[index]?.email && (
                <p className="text-xs text-red-600">{errors.members[index].email.message}</p>
              )}
            </div>
            <button type="button" onClick={() => remove(index)}
              className="text-red-500 hover:text-red-700 text-sm" disabled={fields.length <= 1}>
              Remove
            </button>
          </div>
        ))}

        {/* Array-level error */}
        {errors.members?.root && (
          <p className="text-sm text-red-600">{errors.members.root.message}</p>
        )}

        <button type="button"
          onClick={() => append({ name: '', role: 'developer', email: '' })}
          className="text-sm text-blue-600 hover:text-blue-800">
          + Add Member
        </button>
      </div>

      <button type="submit" className="...">Save Team</button>
    </form>
  )
}
```

---

## Conditional Fields (Discriminated Union)

```tsx
const schema = z.discriminatedUnion('contactMethod', [
  z.object({ contactMethod: z.literal('email'), email: z.string().email() }),
  z.object({ contactMethod: z.literal('phone'), phone: z.string().min(10) }),
])

export function ContactPreference() {
  const { register, watch, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { contactMethod: 'email' as const, email: '', phone: '' },
  })

  const method = watch('contactMethod')

  return (
    <div className="space-y-4">
      <select {...register('contactMethod')} className="...">
        <option value="email">Email</option>
        <option value="phone">Phone</option>
      </select>

      {method === 'email' && (
        <div>
          <input {...register('email')} type="email" placeholder="you@example.com" className="..." />
          {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
        </div>
      )}

      {method === 'phone' && (
        <div>
          <input {...register('phone')} type="tel" placeholder="(555) 123-4567" className="..." />
          {errors.phone && <p className="text-sm text-red-600">{errors.phone.message}</p>}
        </div>
      )}
    </div>
  )
}
```

---

## Dependent Field Validation

Fields whose validation depends on another field's value:

```tsx
const schema = z.object({
  hasDiscount: z.boolean(),
  discountCode: z.string().optional(),
}).refine(
  data => !data.hasDiscount || (data.discountCode && data.discountCode.length >= 5),
  { message: 'Discount code must be at least 5 characters', path: ['discountCode'] }
)

// Use deps option to re-trigger validation
<input type="checkbox" {...register('hasDiscount')} />
<input {...register('discountCode', { deps: ['hasDiscount'] })} />
```

---

## Reusable Form Hook Pattern

```tsx
// hooks/use-form-with-action.ts
import { useForm, type UseFormProps, type FieldValues, type Path } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { type ZodSchema } from 'zod'
import { useState } from 'react'

export function useFormWithAction<T extends FieldValues>(
  schema: ZodSchema<T>,
  action: (data: T) => Promise<{ success: boolean; errors?: Record<string, string[]> }>,
  options?: Omit<UseFormProps<T>, 'resolver'>
) {
  const [serverError, setServerError] = useState<string>()
  const [success, setSuccess] = useState(false)

  const form = useForm<T>({
    resolver: zodResolver(schema),
    ...options,
  })

  const onSubmit = form.handleSubmit(async (data) => {
    setServerError(undefined)
    setSuccess(false)

    const result = await action(data)

    if (result.success) {
      setSuccess(true)
      form.reset()
    } else if (result.errors) {
      Object.entries(result.errors).forEach(([field, messages]) => {
        if (field === '_form') setServerError(messages[0])
        else form.setError(field as Path<T>, { type: 'server', message: messages[0] })
      })
    }
  })

  return { ...form, onSubmit, serverError, success }
}
```

Usage:

```tsx
const { register, formState, onSubmit, serverError, success } = useFormWithAction(
  contactSchema,
  submitContact,
  { defaultValues: { name: '', email: '', message: '' } }
)
```

---

## Password Strength Indicator

```tsx
const PasswordInput = ({ register, watch, errors }) => {
  const password = watch('password') || ''
  const strength = getPasswordStrength(password)

  return (
    <div>
      <input type="password" {...register('password')} className="..." />
      {password && (
        <div className="mt-2">
          <div className="flex gap-1">
            {[1, 2, 3, 4].map(level => (
              <div key={level}
                className={`h-1.5 flex-1 rounded ${
                  strength >= level
                    ? ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500'][level - 1]
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="mt-1 text-xs text-gray-500">
            {['Weak', 'Fair', 'Good', 'Strong'][strength - 1]}
          </p>
        </div>
      )}
      {errors.password && <p className="text-sm text-red-600">{errors.password.message}</p>}
    </div>
  )
}

function getPasswordStrength(p: string): number {
  let score = 0
  if (p.length >= 8) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
}
```
