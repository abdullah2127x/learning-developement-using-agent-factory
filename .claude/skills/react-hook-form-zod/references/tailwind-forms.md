# Tailwind CSS Form Styling

## Base Input Classes

```tsx
// Standard input — reuse across all text inputs
const inputBase = `block w-full rounded-md border px-3 py-2 text-sm shadow-sm
  placeholder:text-gray-400
  focus:outline-none focus:ring-2 focus:ring-offset-0
  disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed`

const inputNormal = `${inputBase} border-gray-300 focus:border-blue-500 focus:ring-blue-500`
const inputError = `${inputBase} border-red-500 focus:border-red-500 focus:ring-red-500`
```

### Dynamic Error Styling

```tsx
function cn(hasError: boolean) {
  return `block w-full rounded-md border px-3 py-2 text-sm shadow-sm
    placeholder:text-gray-400 focus:outline-none focus:ring-2
    disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
    ${hasError
      ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'}`
}

<input {...register('name')} className={cn(!!errors.name)} />
```

---

## Complete Field Components

### Text Input

```tsx
<div>
  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
    Full Name
  </label>
  <input
    id="name"
    {...register('name')}
    className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm
      placeholder:text-gray-400 focus:outline-none focus:ring-2
      ${errors.name
        ? 'border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:ring-blue-500'}`}
    placeholder="John Doe"
    aria-invalid={errors.name ? 'true' : 'false'}
    aria-describedby={errors.name ? 'name-error' : undefined}
  />
  {errors.name && (
    <p id="name-error" className="mt-1 text-sm text-red-600">{errors.name.message}</p>
  )}
</div>
```

### Textarea

```tsx
<div>
  <label htmlFor="message" className="block text-sm font-medium text-gray-700">
    Message
  </label>
  <textarea
    id="message"
    {...register('message')}
    rows={4}
    className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm
      placeholder:text-gray-400 focus:outline-none focus:ring-2 resize-y
      ${errors.message
        ? 'border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:ring-blue-500'}`}
    placeholder="Your message..."
  />
  {errors.message && (
    <p className="mt-1 text-sm text-red-600">{errors.message.message}</p>
  )}
</div>
```

### Select

```tsx
<div>
  <label htmlFor="role" className="block text-sm font-medium text-gray-700">Role</label>
  <select
    id="role"
    {...register('role')}
    className={`mt-1 block w-full rounded-md border px-3 py-2 text-sm shadow-sm
      focus:outline-none focus:ring-2
      ${errors.role
        ? 'border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:ring-blue-500'}`}
  >
    <option value="">Select a role</option>
    <option value="admin">Admin</option>
    <option value="user">User</option>
  </select>
  {errors.role && (
    <p className="mt-1 text-sm text-red-600">{errors.role.message}</p>
  )}
</div>
```

### Checkbox

```tsx
<div className="flex items-start gap-2">
  <input
    id="terms"
    type="checkbox"
    {...register('acceptTerms')}
    className="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600
      focus:ring-2 focus:ring-blue-500"
  />
  <label htmlFor="terms" className="text-sm text-gray-700">
    I accept the <a href="/terms" className="text-blue-600 underline">terms</a>
  </label>
</div>
{errors.acceptTerms && (
  <p className="text-sm text-red-600">{errors.acceptTerms.message}</p>
)}
```

### Radio Group

```tsx
<fieldset>
  <legend className="text-sm font-medium text-gray-700">Plan</legend>
  <div className="mt-2 space-y-2">
    {['free', 'pro', 'enterprise'].map(plan => (
      <label key={plan} className="flex items-center gap-2">
        <input
          type="radio"
          value={plan}
          {...register('plan')}
          className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <span className="text-sm text-gray-700 capitalize">{plan}</span>
      </label>
    ))}
  </div>
  {errors.plan && <p className="mt-1 text-sm text-red-600">{errors.plan.message}</p>}
</fieldset>
```

---

## Buttons

```tsx
// Primary submit
<button
  type="submit"
  disabled={isSubmitting}
  className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white
    hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    transition-colors"
>
  {isSubmitting ? 'Saving...' : 'Save'}
</button>

// Secondary / Cancel
<button
  type="button"
  className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium
    text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  Cancel
</button>

// Danger / Delete
<button
  type="button"
  className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white
    hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
>
  Delete
</button>
```

---

## Form Layout Patterns

### Single Column (Mobile-First)

```tsx
<form className="space-y-4 max-w-md mx-auto">
  {/* Fields stack vertically with consistent spacing */}
</form>
```

### Two Column (Responsive)

```tsx
<form className="space-y-4 max-w-2xl">
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
    <div>{/* First name */}</div>
    <div>{/* Last name */}</div>
  </div>
  <div>{/* Full-width email */}</div>
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
    <div className="sm:col-span-2">{/* City */}</div>
    <div>{/* ZIP */}</div>
  </div>
</form>
```

### Card Form

```tsx
<div className="mx-auto max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
  <h2 className="text-lg font-semibold text-gray-900">Contact Us</h2>
  <p className="mt-1 text-sm text-gray-500">We'll get back to you within 24 hours.</p>
  <form className="mt-6 space-y-4">
    {/* Fields */}
  </form>
</div>
```

---

## Dark Mode

```tsx
<input className="
  bg-white dark:bg-gray-800
  border-gray-300 dark:border-gray-600
  text-gray-900 dark:text-white
  placeholder:text-gray-400 dark:placeholder:text-gray-500
  focus:ring-blue-500 dark:focus:ring-blue-400
" />

<label className="text-gray-700 dark:text-gray-300">Label</label>
<p className="text-red-600 dark:text-red-400">Error message</p>
```

---

## Success / Error Alerts

```tsx
// Success
<div className="rounded-md bg-green-50 border border-green-200 p-4">
  <p className="text-sm font-medium text-green-800">Form submitted successfully!</p>
</div>

// Error
<div className="rounded-md bg-red-50 border border-red-200 p-4">
  <p className="text-sm font-medium text-red-800">Something went wrong. Please try again.</p>
</div>
```

---

## Accessibility Checklist

- `<label htmlFor="id">` linked to every input via `id`
- `aria-invalid="true"` on inputs with errors
- `aria-describedby="error-id"` linking input to error message
- `aria-required="true"` on required fields
- Error messages have matching `id` for `aria-describedby`
- Focus ring visible on keyboard navigation (`focus:ring-2`)
- Disabled state has `disabled:opacity-50 disabled:cursor-not-allowed`
- Form-level errors announced with `role="alert"` or `aria-live="polite"`
