# Interactive Elements for CLI Applications

## Input Prompts

### Basic Input
```
? Enter your name: [________________]
```

### Password Input
```
? Enter password: [••••••••••••]
```

### Confirmation
```
? Do you want to continue? (Y/n)
```

### Multi-line Input
```
? Describe the issue:
  | Line 1
  | Line 2
  | Line 3
```

## Selection Menus

### Single Selection
```
? Choose an option:
  ❯ ○ Option 1
    ○ Option 2
    ○ Option 3
```

### Multiple Selection
```
? Choose options (Press <space> to select):
  ☐ Option A
  ☐ Option B
  ☐ Option C
```

### Radio Selection
```
? Select priority:
  ◉ High
  ○ Medium
  ○ Low
```

## Progress Indicators

### Simple Progress Bar
```
Progress: [████████████████████████████████████████] 100%
```

### Detailed Progress Bar
```
Processing files: [███████████████-------------------------] 45% (9/20)
ETA: 00:01:23
```

### Spinner with Text
```
Processing... ⠋
Processing... ⠙
Processing... ⠹
```

## Status Indicators

### Status Banner
```
┌─ STATUS ──────────────────────────────────────┐
│ Application: Running                          │
│ Version:    1.0.0                            │
│ Uptime:     2h 15m 32s                       │
└───────────────────────────────────────────────┘
```

### Status Icons
```
✅ Success
❌ Error
⚠️  Warning
ℹ️  Information
⏳ Processing
⏸️  Paused
⏹️  Stopped
▶️  Running
```

## Interactive Tables

### Selectable Table
```
? Select a record:
  ❯ ✓ Name        | ID    | Status
    ○ John Smith  | 001   | Active
    ○ Jane Doe    | 002   | Inactive
    ○ Bob Wilson  | 003   | Active
```

### Editable Table
```
┌─ Edit Record ─────────────────────────────────┐
│ Name: [John Smith                    ]        │
│ Email:[john@example.com              ]        │
│ Status:[Active                       ] ▼      │
└───────────────────────────────────────────────┘
```

## Implementation Patterns

### Using Inquirer.js in Node.js
```javascript
const inquirer = require('inquirer');

// Basic input
const answer = await inquirer.prompt([
  {
    type: 'input',
    name: 'name',
    message: 'Enter your name:',
  }
]);

// Selection
const choice = await inquirer.prompt([
  {
    type: 'list',
    name: 'action',
    message: 'What would you like to do?',
    choices: ['Create', 'Update', 'Delete', 'View']
  }
]);

// Checkbox
const selections = await inquirer.prompt([
  {
    type: 'checkbox',
    name: 'features',
    message: 'Select features:',
    choices: ['Feature A', 'Feature B', 'Feature C']
  }
]);
```

### Using PyInquirer in Python
```python
from PyInquirer import prompt

questions = [
    {
        'type': 'input',
        'name': 'name',
        'message': 'Enter your name:',
    }
]

answers = prompt(questions)
print(answers)
```

### Using Enquirer in Node.js
```javascript
const { prompt } = require('enquirer');

const response = await prompt({
  type: 'select',
  name: 'theme',
  message: 'Choose a theme',
  choices: ['default', 'fancy', 'modern']
});
```

## Best Practices

### Accessibility
- Provide keyboard navigation alternatives
- Use high-contrast colors
- Support screen readers
- Offer text-only alternatives

### Responsiveness
- Handle terminal resize events
- Adapt layouts for different screen sizes
- Provide scrollable interfaces for long content

### Error Handling
- Validate input in real-time
- Provide clear error messages
- Offer suggestions for corrections
- Maintain context when errors occur

### Consistency
- Use consistent key bindings
- Maintain visual style across elements
- Follow platform conventions
- Provide help text for complex interactions

## Animation and Effects

### Smooth Transitions
- Fade in/out for new elements
- Smooth scrolling for lists
- Animated progress updates

### Visual Feedback
- Highlight active elements
- Show loading states
- Provide success/failure animations
- Use micro-interactions for better UX