# Color Schemes for CLI Applications

## Standard Color Palette

### Status Colors
- **Success**: Green (✓, ✅, ✔️)
- **Error**: Red (✗, ❌, ✖️)
- **Warning**: Yellow (⚠️, ⚠, ◊)
- **Info**: Blue (ℹ️, ℹ, i)
- **Debug**: Gray (🐛, 🧪, #)

### Text Colors
- **Titles**: Magenta or Cyan
- **Highlights**: Cyan or Yellow
- **Subtle text**: Gray
- **Links**: Blue (underlined)

## Accessibility Considerations

### Color Contrast
- Ensure text has sufficient contrast against background
- Minimum contrast ratio of 4.5:1 for normal text
- Minimum contrast ratio of 3:1 for large text

### Color-Blind Friendly Palettes
- Don't rely solely on color to convey information
- Use patterns, symbols, or text in addition to color
- Common color blindness types:
  - Deuteranopia (green-blind)
  - Protanopia (red-blind)
  - Tritanopia (blue-blind)

## Popular Color Combinations

### Professional Theme
- Primary: Blue (#007acc)
- Success: Green (#28a745)
- Warning: Orange (#fd7e14)
- Error: Red (#dc3545)
- Info: Gray (#6c757d)

### Modern Theme
- Primary: Purple (#6f42c1)
- Success: Teal (#20c997)
- Warning: Yellow (#e9ecef)
- Error: Red (#e74c3c)
- Info: Blue (#3498db)

## Implementation Tips

### Using Chalk in Node.js
```javascript
const chalk = require('chalk');

// Basic colors
console.log(chalk.red('This is red'));
console.log(chalk.green('This is green'));

// Combining styles
console.log(chalk.red.bold('Bold red text'));
console.log(chalk.blue.bgYellow('Blue text with yellow background'));

// RGB colors
console.log(chalk.rgb(255, 136, 0).bold('Orange bold text'));
```

### Using Colorama in Python
```python
from colorama import Fore, Back, Style, init
init()  # Initialize colorama

print(Fore.GREEN + 'This is green text')
print(Back.YELLOW + 'Yellow background')
print(Style.RESET_ALL + 'Back to normal')
```

## Cross-Platform Considerations

- Not all terminals support the same color depth
- Some terminals may not support certain ANSI codes
- Always provide a fallback for color output
- Test in different terminal environments