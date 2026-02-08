# Formatting Patterns for CLI Applications

## Table Formatting

### Basic Table Structure
```
┌─────────────┬─────────────┬─────────────┐
│ Column 1    │ Column 2    │ Column 3    │
├─────────────┼─────────────┼─────────────┤
│ Value 1     │ Value 2     │ Value 3     │
│ Value 4     │ Value 5     │ Value 6     │
└─────────────┴─────────────┴─────────────┘
```

### Headers and Footers
- Use double lines (═) for main headers and footers
- Use single lines (─) for internal separators
- Align text appropriately (left for text, right for numbers)

## List Formatting

### Numbered Lists
```
1. First item
2. Second item
3. Third item
```

### Bulleted Lists
```
• Item A
• Item B
• Item C
```

### Nested Lists
```
• Main item
  ○ Sub-item 1
  ○ Sub-item 2
    ▪ Sub-sub-item A
    ▪ Sub-sub-item B
• Another main item
```

## Box Elements

### Simple Box
```
┌─────────────────────────┐
│ This is a simple box    │
│ with multiple lines     │
└─────────────────────────┘
```

### Box with Header
```
┌─ Status ────────────────┐
│ Application is running  │
│ Version: 1.0.0          │
└─────────────────────────┘
```

## Progress Indicators

### Progress Bars
```
[████████████████████████████████████████] 100%
[███████████████-------------------------] 45%
```

### Spinners
```
Processing /
Processing -
Processing \
Processing |
```

## Log Formatting

### Standard Log Format
```
[HH:MM:SS] [LEVEL] Message content
[14:30:25] [INFO]  Application started
[14:30:26] [WARN]  Configuration file missing
[14:30:27] [ERROR] Database connection failed
```

### Structured Log Format
```
┌─ INFO ──────────────────────────────────────┐
│ Time:    2023-10-15 14:30:25               │
│ Module:  auth                               │
│ Message: User authenticated successfully    │
└─────────────────────────────────────────────┘
```

## Interactive Elements

### Input Prompts
```
? Enter your name:
» Input here
```

### Selection Menus
```
❯ ○ Option 1
  ○ Option 2
  ○ Option 3
```

### Confirmation Prompts
```
? Do you want to continue? (Y/n)
```

## Formatting Guidelines

### Alignment
- Left-align text content
- Right-align numerical values
- Center-align headers when appropriate

### Spacing
- Use consistent indentation (typically 2 spaces)
- Maintain equal padding inside boxes
- Separate sections with blank lines

### Typography Hierarchy
- Use bold for important elements
- Use italics sparingly for emphasis
- Maintain consistent font styles

## Implementation Patterns

### Using cli-table3 in Node.js
```javascript
const Table = require('cli-table3');

const table = new Table({
  head: ['Name', 'Age', 'City'],
  colWidths: [15, 10, 15],
  style: {
    head: ['cyan', 'bold'],
    border: ['grey']
  }
});

table.push(
  ['John', '30', 'New York'],
  ['Jane', '25', 'Los Angeles']
);

console.log(table.toString());
```

### Using rich in Python
```python
from rich.table import Table
from rich.console import Console

console = Console()
table = Table(show_header=True, header_style="bold magenta")
table.add_column("Name", style="dim", width=12)
table.add_column("Age")
table.add_column("City")

table.add_row("John", "30", "New York")
table.add_row("Jane", "25", "Los Angeles")

console.print(table)
```