# React Hook Form API Reference

## useForm Configuration

```tsx
const {
  register, handleSubmit, formState, watch, setValue, getValues,
  reset, setError, clearErrors, trigger, control, setFocus,
} = useForm<FormData>({
  resolver: zodResolver(schema),  // Zod validation
  defaultValues: { name: '', email: '' },
  mode: 'onBlur',               // When to validate
  reValidateMode: 'onChange',    // Re-validate strategy after first submit
  criteriaMode: 'firstError',   // 'all' to gather all errors per field
  shouldFocusError: true,        // Focus first error field on submit
  delayError: undefined,         // Delay error display (ms)
})
```

### Validation Modes

| Mode | Behavior | Use When |
|------|----------|----------|
| `'onSubmit'` (default) | Validate only on submit | Simple forms, minimal feedback |
| `'onBlur'` | Validate when field loses focus | **Recommended** — good UX balance |
| `'onChange'` | Validate on every keystroke | Real-time feedback (expensive) |
| `'onTouched'` | Validate on first blur, then onChange | Progressive feedback |
| `'all'` | Validate on both blur and change | Maximum feedback |

---

## register

Connects an input to the form. Returns `{ ref, name, onChange, onBlur }`.

```tsx
<input {...register('email')} />

// With additional options
<input {...register('age', { valueAsNumber: true })} type="number" />
<input {...register('date', { valueAsDate: true })} type="date" />

// Validation is handled by Zod resolver, but you can add RHF-native rules too:
<input {...register('name', { required: 'Required' })} />
```

### register Options

| Option | Purpose |
|--------|---------|
| `valueAsNumber` | Parse value as number (critical for `<input type="number">`) |
| `valueAsDate` | Parse value as Date |
| `setValueAs` | Custom transform: `(v) => v.trim()` |
| `disabled` | Disable field, omit from data |
| `onChange` | Custom change handler (called alongside RHF's) |
| `onBlur` | Custom blur handler |
| `deps` | Field names to trigger validation on when this field changes |

---

## formState

```tsx
const {
  errors,           // FieldErrors — per-field error objects
  isDirty,          // boolean — any field modified from defaults
  isValid,          // boolean — all fields pass validation
  isSubmitting,     // boolean — handleSubmit is running
  isSubmitSuccessful, // boolean — last submit succeeded
  dirtyFields,      // { [field]: boolean }
  touchedFields,    // { [field]: boolean }
  submitCount,      // number — total submit attempts
} = formState
```

### Error Object Shape

```tsx
errors.email?.message    // "Invalid email" (string)
errors.email?.type       // "too_small" (Zod issue code)
errors.email?.ref        // DOM reference

// Nested errors
errors.address?.city?.message

// Field array errors
errors.items?.[0]?.name?.message
errors.items?.root?.message  // Array-level validation
```

---

## Key Methods

### handleSubmit

```tsx
<form onSubmit={handleSubmit(onValid, onInvalid)}>
// onValid: (data: FormData) => void | Promise<void>
// onInvalid?: (errors: FieldErrors) => void  (optional)
```

### watch — Subscribe to Field Changes

```tsx
const name = watch('name')              // Single field
const [name, email] = watch(['name', 'email']) // Multiple
const allValues = watch()                // All fields

// Callback form (no re-render)
useEffect(() => {
  const subscription = watch((value, { name, type }) => {
    console.log(value, name, type)
  })
  return () => subscription.unsubscribe()
}, [watch])
```

### setValue — Programmatic Update

```tsx
setValue('name', 'John')
setValue('name', 'John', {
  shouldValidate: true,  // Trigger validation
  shouldDirty: true,     // Mark as dirty
  shouldTouch: true,     // Mark as touched
})
```

### reset — Reset Form

```tsx
reset()                           // Reset to defaultValues
reset({ name: 'Jane', email: '' }) // Reset to new values
reset(undefined, { keepDirtyValues: true }) // Keep user changes
```

### setError — Manual Error

```tsx
setError('email', { type: 'server', message: 'Email already taken' })
setError('root.serverError', { message: 'Server unavailable' })
```

### trigger — Manual Validation

```tsx
await trigger('email')              // Validate one field
await trigger(['email', 'name'])    // Validate multiple
await trigger()                     // Validate all
```

---

## Controller (Controlled Components)

For components that don't expose a `ref` (Select, DatePicker, Checkbox groups):

```tsx
import { Controller } from 'react-hook-form'

<Controller
  name="role"
  control={control}
  render={({ field, fieldState: { error } }) => (
    <select {...field} className={error ? 'border-red-500' : 'border-gray-300'}>
      <option value="">Select role</option>
      <option value="admin">Admin</option>
      <option value="user">User</option>
    </select>
  )}
/>
```

### useController (Hook Form)

```tsx
import { useController } from 'react-hook-form'

function CustomSelect({ name, control, options }) {
  const { field, fieldState: { error } } = useController({ name, control })

  return (
    <div>
      <select {...field}>
        {options.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
      </select>
      {error && <p className="text-sm text-red-600">{error.message}</p>}
    </div>
  )
}
```

### When to Use register vs Controller

| Use `register` | Use `Controller` |
|----------------|-----------------|
| Native `<input>`, `<textarea>`, `<select>` | Custom UI components (Radix, Headless UI) |
| Uncontrolled inputs | Components requiring `value` + `onChange` props |
| Best performance (fewest re-renders) | External date pickers, rich text editors |

---

## FormProvider + useFormContext

Share form methods across deeply nested components without prop drilling:

```tsx
import { FormProvider, useFormContext } from 'react-hook-form'

// Parent
function CheckoutForm() {
  const methods = useForm<CheckoutData>({ resolver: zodResolver(schema) })

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <ShippingSection />
        <PaymentSection />
        <button type="submit">Pay</button>
      </form>
    </FormProvider>
  )
}

// Nested child — no props needed
function ShippingSection() {
  const { register, formState: { errors } } = useFormContext<CheckoutData>()

  return (
    <div>
      <input {...register('shipping.address')} />
      {errors.shipping?.address && <p>{errors.shipping.address.message}</p>}
    </div>
  )
}
```

**Rule**: Don't nest `<FormProvider>` — use one per form.

---

## useFieldArray

Manage dynamic lists of fields (add/remove/reorder):

```tsx
import { useFieldArray } from 'react-hook-form'

const { fields, append, remove, move, swap, insert, update, replace } = useFieldArray({
  control,
  name: 'items',
  rules: { minLength: 1 },  // Array-level validation
})
```

### Critical Rules

1. **Always use `field.id` as React key** (never array index)
2. **Provide complete default values** in `append`/`prepend`/`insert`
3. **Register with template literal**: `` register(`items.${index}.name`) ``
4. **Array-level errors**: `errors.items?.root?.message`

```tsx
{fields.map((field, index) => (
  <div key={field.id}>  {/* field.id, NOT index */}
    <input {...register(`items.${index}.name`)} />
    {errors.items?.[index]?.name && (
      <p className="text-sm text-red-600">{errors.items[index].name.message}</p>
    )}
    <button type="button" onClick={() => remove(index)}>Remove</button>
  </div>
))}
<button type="button" onClick={() => append({ name: '' })}>Add Item</button>
```
