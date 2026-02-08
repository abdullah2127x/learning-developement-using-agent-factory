---
name: py-cli-beautifier
description: Comprehensive toolkit for beautifying Python CLI applications with enhanced visual output, formatting, color schemes, and interactive elements. Use when Claude needs to improve the visual appearance and user experience of Python command-line interfaces through styling, formatting, color coding, progress indicators, and other visual enhancements.
license: Complete terms in LICENSE.txt
---

# Python CLI Beautifier

This skill provides tools and guidance for enhancing the visual appearance and user experience of Python command-line interfaces.

## What This Skill Does

The Python CLI Beautifier skill helps create more visually appealing and user-friendly Python command-line interfaces through:

1. **Color and Styling**: Applying color schemes, themes, and visual formatting
2. **Output Formatting**: Creating well-structured tables, lists, and visual elements
3. **Interactive Elements**: Adding progress bars, loading indicators, and interactive prompts
4. **Visual Feedback**: Providing clear status indicators and user feedback

## Required Dependencies

This skill uses several Python libraries for CLI beautification. You may need to install these dependencies depending on which features you use:

For uv projects:
```
uv add rich colorama termcolor tabulate click prompt_toolkit tqdm art
```

For regular Python projects:
```
pip install rich colorama termcolor tabulate click prompt_toolkit tqdm art
```

Or add to your requirements.txt:
```
rich>=12.0.0
colorama>=0.4.0
tabulate>=0.8.0
click>=8.0.0
tqdm>=4.60.0
prompt_toolkit>=3.0.0
```

## When to Use This Skill

Use this skill when working on Python CLI applications that need visual enhancement, including:
- Adding color coding to Python CLI output
- Creating formatted tables and lists in Python terminal applications
- Implementing progress indicators and loading animations in Python
- Designing interactive prompts and menus for Python CLIs
- Improving log formatting and readability in Python applications
- Enhancing overall user experience in Python terminal applications

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

### Python
- `rich`: For rich text and beautiful formatting in the terminal
- `colorama`: For cross-platform colored terminal text
- `termcolor`: For colored text output
- `tabulate`: For creating formatted tables
- `click`: For creating beautiful command-line interfaces
- `prompt_toolkit`: For advanced interactive applications
- `tqdm`: For progress bars
- `art`: For ASCII art and decorative elements

### Common Import Patterns
When using these libraries, ensure correct import patterns:

```python
# For rich (comprehensive formatting)
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel

# For colorama (basic colors)
from colorama import init, Fore, Back, Style
init()  # Initialize colorama

# For tabulate (tables)
from tabulate import tabulate

# For tqdm (progress bars)
from tqdm import tqdm

# For click (interactive CLIs)
import click
```

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

### `scripts/format_table.py`
Utility for creating formatted tables in Python CLI applications.

### `scripts/progress_bar.py`
Implementation of progress bars for long-running Python CLI operations.

### `scripts/colorize_output.py`
Functions for applying consistent color schemes to Python CLI output.

### `scripts/complete_example.py`
Complete example demonstrating all Python CLI beautification features with proper error handling and fallback implementations.

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
   - Ensure all dependencies are installed: `pip install rich colorama termcolor tabulate click prompt_toolkit tqdm art`
   - Verify dependencies are properly installed in your environment

2. **Color Support Issues**
   - On Windows, ensure colorama is initialized with `init()`
   - Use `colorama.init()` to enable color support on older Windows versions

3. **Fallback Implementations**
   If rich is not available, you can use basic colorama or plain text:
   - For tables: Use tabulate or manual formatting
   - For progress: Use simple text-based progress indicators

## References

For specific implementation details, see:
- `references/color-schemes.md` - Comprehensive color scheme guidelines
- `references/formatting-patterns.md` - Output formatting patterns and examples
- `references/interactive-elements.md` - Implementation of interactive CLI components
- `references/accessibility.md` - Accessibility guidelines for Python CLI applications
- `references/troubleshooting.md` - Common issues and solutions for Python CLI beautification