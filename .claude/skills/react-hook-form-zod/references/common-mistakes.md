# Common Mistakes & Anti-Patterns

## Critical Mistakes

### 1. Missing defaultValues

```tsx
// BAD — causes uncontrolled→controlled React warning
const { register } = useForm<FormData>({
  resolver: zodResolver(schema),
  // no defaultValues!
})

// GOOD — always provide defaultValues matching your schema
const { register } = useForm<FormData>({
  resolver: zodResolver(schema),
  defaultValues: { name: '', email: '', age: 0 },
})
```

### 2. Forgetting valueAsNumber for Number Inputs

```tsx
// BAD — age arrives as string "25", Zod rejects because schema expects number
<input type="number" {...register('age')} />

// GOOD — parse as number before validation
<input type="number" {...register('age', { valueAsNumber: true })} />

// ALTERNATIVE — use z.coerce.number() in schema
const schema = z.object({ age: z.coerce.number().min(18) })
```

### 3. Using Array Index as Key in useFieldArray

```tsx
// BAD — causes state bugs, lost input values on reorder/remove
{fields.map((field, index) => (
  <div key={index}> {/* WRONG */}
    <input {...register(`items.${index}.name`)} />
  </div>
))}

// GOOD — use field.id (auto-generated unique ID)
{fields.map((field, index) => (
  <div key={field.id}> {/* CORRECT */}
    <input {...register(`items.${index}.name`)} />
  </div>
))}
```

### 4. No Server-Side Validation

```tsx
// BAD — trusting client-only validation
'use server'
export async function createUser(data: UserData) {
  await db.user.create({ data }) // No validation!
}

// GOOD — validate on server with same Zod schema
'use server'
export async function createUser(data: unknown) {
  const result = userSchema.safeParse(data)
  if (!result.success) return { errors: result.error.flatten().fieldErrors }
  await db.user.create({ data: result.data })
}
```

### 5. Defining Schema Inline (Recreated Every Render)

```tsx
// BAD — new schema object every render, breaks memoization
function MyForm() {
  const schema = z.object({ name: z.string() }) // recreated!
  const { register } = useForm({ resolver: zodResolver(schema) })
}

// GOOD — define outside component or in separate file
const schema = z.object({ name: z.string() })

function MyForm() {
  const { register } = useForm({ resolver: zodResolver(schema) })
}
```

---

## Moderate Mistakes

### 6. Cross-Field Validation Without path

```tsx
// BAD — error shows on form root, not on any specific field
.refine(d => d.password === d.confirm, {
  message: "Passwords don't match",
  // missing path!
})

// GOOD — error appears on the confirm field
.refine(d => d.password === d.confirm, {
  message: "Passwords don't match",
  path: ['confirm'],
})
```

### 7. Not Disabling Submit Button

```tsx
// BAD — user can double-submit
<button type="submit">Save</button>

// GOOD — disable during submission
<button type="submit" disabled={isSubmitting}
  className="disabled:opacity-50 disabled:cursor-not-allowed">
  {isSubmitting ? 'Saving...' : 'Save'}
</button>
```

### 8. Using onChange Mode for Large Forms

```tsx
// BAD — validates every field on every keystroke (expensive)
useForm({ mode: 'onChange', resolver: zodResolver(largeSchema) })

// GOOD — validate on blur, re-validate on change after first submit
useForm({ mode: 'onBlur', reValidateMode: 'onChange', resolver: zodResolver(largeSchema) })
```

### 9. Not Using z.infer for Type

```tsx
// BAD — type and schema can drift apart
type FormData = { name: string; email: string; age: number }
const schema = z.object({ name: z.string(), email: z.string().email() })
// FormData has 'age' but schema doesn't — silent bug

// GOOD — single source of truth
const schema = z.object({ name: z.string(), email: z.string().email() })
type FormData = z.infer<typeof schema>
```

### 10. Calling redirect After Setting Errors

```tsx
// BAD — redirect throws, errors never reach client
'use server'
export async function action(data) {
  if (invalid) {
    return { errors: { name: ['Required'] } }
  }
  redirect('/success') // If you return errors above, this is fine
  // But don't try to redirect AND return errors in same path
}
```

---

## Subtle Mistakes

### 11. Empty Append in useFieldArray

```tsx
// BAD — append rejects empty objects
append({}) // Error!

// GOOD — provide all field defaults
append({ name: '', email: '', role: 'user' })
```

### 12. Nested FormProvider

```tsx
// BAD — inner provider shadows outer, causes bugs
<FormProvider {...outerMethods}>
  <FormProvider {...innerMethods}> {/* DON'T nest */}
    <NestedInput />
  </FormProvider>
</FormProvider>

// GOOD — one FormProvider per form, use separate useForm for separate forms
```

### 13. Watching Too Many Fields

```tsx
// BAD — re-renders on every field change
const allValues = watch()

// GOOD — watch only what you need
const email = watch('email')

// BEST — use subscribe for side effects without re-renders
useEffect(() => {
  const sub = watch((value, { name }) => {
    if (name === 'country') updateCities(value.country)
  })
  return () => sub.unsubscribe()
}, [watch])
```

### 14. Missing aria Attributes

```tsx
// BAD — screen readers can't associate error with input
<input {...register('email')} />
{errors.email && <p>{errors.email.message}</p>}

// GOOD — accessible error association
<input
  {...register('email')}
  aria-invalid={!!errors.email}
  aria-describedby={errors.email ? 'email-error' : undefined}
/>
{errors.email && (
  <p id="email-error" role="alert" className="text-sm text-red-600">
    {errors.email.message}
  </p>
)}
```

---

## Debugging Checklist

1. **Validation not running?** Check `resolver: zodResolver(schema)` is passed to `useForm`
2. **Errors not showing?** Destructure `formState: { errors }` — RHF uses Proxy, must access it
3. **Number field failing?** Add `valueAsNumber: true` to `register` or use `z.coerce.number()`
4. **Field array bugs?** Use `field.id` as key, not index. Provide full defaults in `append`
5. **Server errors not showing?** Use `setError('fieldName', { message })` after server response
6. **Form not submitting?** Check for unresolved validation errors — add `onError` callback to `handleSubmit`
7. **Cross-field errors missing?** Ensure `.refine()` has `path` option pointing to correct field
8. **Type mismatch?** Use `z.infer<typeof schema>` as the form type — never define types separately
9. **Re-renders too frequent?** Switch from `onChange` to `onBlur` mode. Use `watch` sparingly
10. **Default values not applying?** Ensure `defaultValues` shape matches schema exactly
