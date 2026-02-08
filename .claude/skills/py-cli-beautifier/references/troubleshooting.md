# Troubleshooting Python CLI Beautification

This document covers common issues encountered when implementing Python CLI beautification and their solutions.

## Module Import Issues

### Rich Module Issues
**Problem**: `ModuleNotFoundError: No module named 'rich'`

**Solution**: Install rich library:
```bash
pip install rich
```

### Colorama Module Issues
**Problem**: Colors not working on Windows

**Solution**: Initialize colorama properly:
```python
from colorama import init
init()  # Call this once at the start of your script
```

## Dependency Management

### Installing Dependencies
```bash
pip install rich colorama termcolor tabulate click prompt_toolkit tqdm art
```

### Requirements.txt Example
```txt
rich>=12.0.0
colorama>=0.4.0
tabulate>=0.8.0
click>=8.0.0
tqdm>=4.60.0
prompt_toolkit>=3.0.0
```

## Fallback Implementations

When modules fail to load, you can implement similar functionality manually:

### Manual Table Implementation
```python
def create_simple_table(headers, rows):
    # Calculate column widths
    all_rows = [headers] + rows
    col_widths = []

    for i in range(len(headers)):
        max_width = max(len(str(row[i])) for row in all_rows)
        col_widths.append(max(max_width, len(headers[i])))

    # Create table string
    result = []

    # Header separator
    separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"

    # Header row
    header_row = "|"
    for i, header in enumerate(headers):
        header_row += f" {header.ljust(col_widths[i])} |"

    result.append(separator)
    result.append(header_row)
    result.append(separator)

    # Data rows
    for row in rows:
        data_row = "|"
        for i, cell in enumerate(row):
            data_row += f" {str(cell).ljust(col_widths[i])} |"
        result.append(data_row)

    result.append(separator)

    return "\n".join(result)
```

### Manual Progress Implementation
```python
import sys
import time

def simple_progress_bar(current, total, description="Processing"):
    percentage = int((current / total) * 100)
    bar_length = 30
    filled_length = int(bar_length * current // total)

    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    sys.stdout.write(f'\r{description}: |{bar}| {percentage}% ({current}/{total})')
    sys.stdout.flush()

    if current == total:
        print()  # New line when complete
```

## Cross-Platform Compatibility

### Terminal Compatibility Issues
- Some terminals don't support certain Unicode characters
- Colors may not display in all environments
- Consider using `colorama` for consistent color support across platforms

### Testing in Different Environments
- Test in various terminals (bash, zsh, Windows cmd, PowerShell)
- Consider fallbacks for environments with limited feature support
- Use feature detection rather than assuming capabilities