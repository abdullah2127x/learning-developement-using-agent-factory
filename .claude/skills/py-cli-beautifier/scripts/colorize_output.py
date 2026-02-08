#!/usr/bin/env python3
"""
colorize_output.py - Functions for applying consistent color schemes to Python CLI output
"""

try:
    from rich.console import Console
    from rich.text import Text
    from rich import print as rich_print
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def colorize_rich(message, color="white"):
    """Colorize message using rich library"""
    if not RICH_AVAILABLE:
        raise ImportError("rich library is not available")

    return Text(message, style=color)


def colorize_colorama(message, color="white"):
    """Colorize message using colorama library"""
    if not COLORAMA_AVAILABLE:
        raise ImportError("colorama library is not available")

    color_map = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "reset": Style.RESET_ALL
    }

    color_code = color_map.get(color.lower(), Fore.WHITE)
    return f"{color_code}{message}{Style.RESET_ALL}"


def format_message_rich(message_type, message):
    """Format a message with color and icon using rich"""
    if not RICH_AVAILABLE:
        raise ImportError("rich library is not available")

    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "debug": "🐛",
        "highlight": "✨",
        "title": "🎯"
    }

    colors = {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "blue",
        "debug": "grey62",
        "highlight": "cyan",
        "title": "magenta"
    }

    icon = icons.get(message_type, "🔹")
    color = colors.get(message_type, "white")

    text = Text()
    text.append(icon + " ", style=color)
    text.append(message, style=color)

    return text


def format_message_colorama(message_type, message):
    """Format a message with color and icon using colorama"""
    if not COLORAMA_AVAILABLE:
        raise ImportError("colorama library is not available")

    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "debug": "🐛",
        "highlight": "✨",
        "title": "🎯"
    }

    colors = {
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.BLUE,
        "debug": Fore.LIGHTBLACK_EX,
        "highlight": Fore.CYAN,
        "title": Fore.MAGENTA
    }

    icon = icons.get(message_type, "🔹")
    color_code = colors.get(message_type, Fore.WHITE)

    return f"{color_code}{icon} {message}{Style.RESET_ALL}"


def create_status_banner_rich(title, status, status_type="info"):
    """Create a status banner using rich"""
    if not RICH_AVAILABLE:
        raise ImportError("rich library is not available")

    status_colors = {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "blue"
    }

    color = status_colors.get(status_type, "white")
    status_text = Text(status, style=f"bold {color}")

    from rich.panel import Panel
    return Panel(f"Name: {title}\nStatus: {status}", title="Application Status")


def create_status_banner_simple(title, status, status_type="info"):
    """Create a simple status banner without external libraries"""
    banner = f"""
┌─ APPLICATION STATUS ──────────────────────────────────┐
│  Name: {title:<43} │
│  Status: {status:<40} │
└────────────────────────────────────────────────────────┘
"""
    return banner


# Example usage
if __name__ == "__main__":
    if RICH_AVAILABLE:
        print("Rich formatted messages:")
        rich_print(format_message_rich("success", "Operation completed successfully"))
        rich_print(format_message_rich("error", "An error occurred during processing"))
        rich_print(format_message_rich("warning", "This is a warning message"))
        rich_print(format_message_rich("info", "Here is some important information"))

        print("\nRich status banner:")
        from rich.console import Console
        console = Console()
        console.print(create_status_banner_rich("My App", "Running", "success"))

    if COLORAMA_AVAILABLE:
        print("\nColorama formatted messages:")
        print(format_message_colorama("success", "Operation completed successfully"))
        print(format_message_colorama("error", "An error occurred during processing"))
        print(format_message_colorama("warning", "This is a warning message"))
        print(format_message_colorama("info", "Here is some important information"))

    print("\nSimple status banner:")
    print(create_status_banner_simple("My App", "Running"))