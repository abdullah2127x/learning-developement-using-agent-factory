# Color Schemes for Python CLI Applications

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
- Primary: Blue (using rich's blue)
- Success: Green (using rich's green)
- Warning: Yellow (using rich's yellow)
- Error: Red (using rich's red)
- Info: Gray (using rich's grey62)

### Modern Theme
- Primary: Magenta (using rich's magenta)
- Success: Green (using rich's green)
- Warning: Yellow (using rich's yellow)
- Error: Red (using rich's red)
- Info: Blue (using rich's blue)

## Implementation Tips

### Using Rich in Python
```python
from rich.console import Console
from rich.text import Text

console = Console()

# Basic colors
console.print("[red]This is red text[/red]")
console.log("[green]This is green text[/green]")

# Combining styles
console.print("[bold red]Bold red text[/bold red]")
console.print("[blue on yellow]Blue text with yellow background[/blue on yellow]")

# Using Text objects
text = Text("Colored text")
text.stylize("red", 0, 5)  # Style "Colored"
console.print(text)
```

### Using Colorama in Python
```python
from colorama import init, Fore, Back, Style
init()  # Initialize colorama

print(Fore.GREEN + 'This is green text')
print(Back.YELLOW + 'Yellow background')
print(Style.RESET_ALL + 'Back to normal')
```

## Cross-Platform Considerations

- Rich handles cross-platform color support automatically
- Colorama needs initialization on Windows for color support
- Test in different terminal environments
- Consider providing fallbacks for environments without color support