---
name: js-cli-beautifier
description: Comprehensive toolkit for beautifying JavaScript/Node.js CLI applications with enhanced visual output, formatting, color schemes, and interactive elements. Use when Claude needs to improve the visual appearance and user experience of JavaScript command-line interfaces through styling, formatting, color coding, progress indicators, and other visual enhancements.
license: Complete terms in LICENSE.txt
---

# JavaScript CLI Beautifier

This skill provides tools and guidance for enhancing the visual appearance and user experience of JavaScript/Node.js command-line interfaces.

## What This Skill Does

The JavaScript CLI Beautifier skill helps create more visually appealing and user-friendly JavaScript command-line interfaces through:

1. **Color and Styling**: Applying color schemes, themes, and visual formatting
2. **Output Formatting**: Creating well-structured tables, lists, and visual elements
3. **Interactive Elements**: Adding progress bars, loading indicators, and interactive prompts
4. **Visual Feedback**: Providing clear status indicators and user feedback

## Required Dependencies

This skill uses several JavaScript libraries for CLI beautification. You may need to install these dependencies depending on which features you use:

For npm projects:
```
npm install chalk cli-table3 cli-progress ora boxen inquirer
```

For yarn projects:
```
yarn add chalk cli-table3 cli-progress ora boxen inquirer
```

For pnpm projects:
```
pnpm add chalk cli-table3 cli-progress ora boxen inquirer
```

Or add to your package.json dependencies:
```json
{
  "dependencies": {
    "chalk": "^5.0.0",
    "cli-table3": "^0.6.0",
    "cli-progress": "^3.10.0",
    "ora": "^6.0.0",
    "boxen": "^7.0.0",
    "inquirer": "^9.0.0"
  }
}
```

## When to Use This Skill

Use this skill when working on JavaScript/Node.js CLI applications that need visual enhancement, including:
- Adding color coding to JavaScript CLI output
- Creating formatted tables and lists in Node.js terminal applications
- Implementing progress indicators and loading animations in Node.js
- Designing interactive prompts and menus for Node.js CLIs
- Improving log formatting and readability in JavaScript applications
- Enhancing overall user experience in Node.js terminal applications

## Core Principles

### Visual Consistency
Maintain consistent styling across all CLI elements to create a professional appearance.

### Accessibility
Ensure color schemes have sufficient contrast and provide alternatives for color-blind users.

### Performance
Keep visual enhancements lightweight to avoid slowing down CLI applications.

### Cross-Platform Compatibility
Use libraries and techniques that work across different terminal environments and operating systems.

## Recommended Libraries and Tools

### JavaScript/Node.js
- `chalk`: For colorizing terminal output
- `cli-table3`: For creating formatted tables
- `ora`: For elegant terminal spinners
- `inquirer`: For interactive command-line prompts
- `figures`: For displaying symbols across different platforms
- `boxen`: For creating boxes in the terminal
- `cli-progress`: For progress bars

### Proper Import Patterns
When using these libraries, ensure correct import patterns to avoid runtime errors. Modern libraries often support both CommonJS and ES modules, but the syntax differs:

**For CommonJS (require):**
```javascript
// For chalk (colors and styling)
const chalk = require('chalk');

// For cli-table3 (formatted tables)
const Table = require('cli-table3');

// For cli-progress (progress bars)
const cliProgress = require('cli-progress');

// For boxen (content containers with borders)
const boxen = require('boxen');  // Note: Do not destructure as {boxen}

// For ora (loading spinners) - CommonJS approach
const ora = require('ora');
```

**For ES Modules (import):**
```javascript
// For chalk (colors and styling)
import chalk from 'chalk';

// For cli-table3 (formatted tables)
import Table from 'cli-table3';

// For cli-progress (progress bars)
import cliProgress from 'cli-progress';

// For boxen (content containers with borders)
import boxen from 'boxen';

// For ora (loading spinners) - ES modules approach
import ora from 'ora';
```

### Module System Configuration
To use ES modules in your project:

1. **Update package.json**: Set `"type": "module"` in your package.json file
2. **File extensions**: Use `.mjs` for ES modules or ensure your project is configured for ES modules
3. **Node.js version**: Ensure you're using Node.js 12+ for full ES modules support

### Common Import Issues and Solutions
- **boxen**: Use `const boxen = require('boxen')` for CommonJS or `import boxen from 'boxen'` for ES modules
- **ora**: Use `const ora = require('ora')` for CommonJS or `import ora from 'ora'` for ES modules
- **Module not found**: If getting "is not a function" errors, ensure you're using the correct import syntax for your module system
- **Mixed module systems**: Avoid mixing CommonJS and ES modules in the same project without proper configuration

## Implementation Patterns

### Color Schemes
Use consistent color schemes that match your application's purpose:
- Blue for informational messages
- Green for success states
- Yellow for warnings
- Red for errors
- Cyan for neutral information

### Formatting Elements
- Use tables for displaying structured data
- Apply consistent indentation for nested information
- Use borders and separators to organize content
- Implement pagination for long outputs

### Interactive Elements
- Progress bars for long-running operations
- Loading indicators for asynchronous tasks
- Confirmation prompts for destructive actions
- Menu systems for complex navigation

## Scripts Available

### `scripts/format-table.js`
Utility for creating formatted tables in JavaScript CLI applications.

### `scripts/progress-bar.js`
Implementation of progress bars for long-running JavaScript CLI operations.

### `scripts/colorize-output.js`
Functions for applying consistent color schemes to JavaScript CLI output.

### `scripts/complete-example.js`
Complete example demonstrating all JavaScript CLI beautification features with proper error handling and fallback implementations.

### `scripts/es-module-example.js`
Complete example using ES modules (import/export) syntax for CLI beautification libraries, demonstrating proper usage to avoid "is not a function" errors.

### `scripts/commonjs-example.js`
Complete example using CommonJS (require) syntax for CLI beautification libraries, demonstrating proper usage patterns for projects using CommonJS modules.

## Common CLI Beautification Patterns

### Before Enhancement
```
Processing files...
File 1 processed
File 2 processed
File 3 processed
Operation completed successfully
```

### After Enhancement
```
┌─────────────────────────────────────────┐
│  [FILE] Processing files...             │
├─────────────────────────────────────────┤
│  [OK] File 1 processed                 │
│  [OK] File 2 processed                 │
│  [OK] File 3 processed                 │
├─────────────────────────────────────────┤
│  [SUCCESS] Operation completed          │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues and Solutions

1. **Module Not Found Errors**
   - Ensure all dependencies are installed: `npm install chalk cli-table3 cli-progress boxen ora`
   - Verify dependencies are listed in package.json

2. **Import/Export Issues - "is not a function" errors**
   - **ora library**: Getting `TypeError: ora is not a function` or `TypeError: ora is not a constructor`
     - **Solution**: Use proper import syntax - `const ora = require('ora')` for CommonJS or `import ora from 'ora'` for ES modules
   - **boxen library**: Getting `TypeError: boxen is not a function`
     - **Solution**: Use `const boxen = require('boxen')` for CommonJS or `import boxen from 'boxen'` for ES modules
   - **Mixed module systems**: Using both CommonJS and ES modules in the same project
     - **Solution**: Stick to one module system or configure proper interoperability

3. **Module System Configuration Issues**
   - **CommonJS vs ES Modules**: Modern libraries like ora and boxen may require ES modules
     - **Solution**: Update package.json with `"type": "module"` to enable ES modules support
   - **Import syntax errors**: Using `require()` when the library expects ES modules
     - **Solution**: Convert to `import` syntax and update your project configuration

4. **Fallback Implementations**
   If module imports fail, you can create manual implementations:
   - For boxes: Use manual border drawing with chalk
   - For progress: Use simple text-based progress indicators

## References

For specific implementation details, see:
- `references/color-schemes.md` - Comprehensive color scheme guidelines
- `references/formatting-patterns.md` - Output formatting patterns and examples
- `references/interactive-elements.md` - Implementation of interactive CLI components
- `references/accessibility.md` - Accessibility guidelines for JavaScript CLI applications
- `references/troubleshooting.md` - Common issues and solutions for JavaScript CLI beautification
- `references/module-systems.md` - Guide to CommonJS vs ES modules for CLI beautification libraries