#!/usr/bin/env python3
"""
complete_example.py - Complete example demonstrating all Python CLI beautification features
"""

import time

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.panel import Panel
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

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


def print_header():
    """Print an enhanced header"""
    if RICH_AVAILABLE:
        console = Console()
        console.print(Panel("[bold blue]PYTHON CLI BEAUTIFIER COMPLETE EXAMPLE[/bold blue]", expand=False))
    else:
        print("=" * 60)
        print("PYTHON CLI BEAUTIFIER COMPLETE EXAMPLE")
        print("=" * 60)


def print_enhanced_messages():
    """Print enhanced messages with color coding"""
    print("\nENHANCED MESSAGE TYPES:")

    if RICH_AVAILABLE:
        rich_print("[green]✓ Success: Operation completed successfully[/green]")
        rich_print("[red]✗ Error: An error occurred during processing[/red]")
        rich_print("[yellow]⚠ Warning: This is a warning message[/yellow]")
        rich_print("[blue]ℹ Info: Here is some important information[/blue]")
        rich_print("[grey62]⚙ Debug: Debug information for troubleshooting[/grey62]")
    elif COLORAMA_AVAILABLE:
        print(f"{Fore.GREEN}✓ Success: Operation completed successfully{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: An error occurred during processing{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Warning: This is a warning message{Style.RESET_ALL}")
        print(f"{Fore.BLUE}ℹ Info: Here is some important information{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}⚙ Debug: Debug information for troubleshooting{Style.RESET_ALL}")
    else:
        print("✓ Success: Operation completed successfully")
        print("✗ Error: An error occurred during processing")
        print("⚠ Warning: This is a warning message")
        print("ℹ Info: Here is some important information")
        print("⚙ Debug: Debug information for troubleshooting")


def print_enhanced_table():
    """Print an enhanced table"""
    print("\nENHANCED TABLE:")

    headers = ["Name", "Status", "Last Updated"]
    rows = [
        ["Project A", "Active", "2026-01-06"],
        ["Project B", "Warn", "2026-01-05"],
        ["Project C", "Error", "2026-01-04"]
    ]

    if RICH_AVAILABLE:
        table = Table(show_header=True, header_style="bold blue")

        for header in headers:
            table.add_column(header, style="dim")

        for row in rows:
            status_color = "green" if row[1] == "Active" else "yellow" if row[1] == "Warn" else "red"
            table.add_row(row[0], f"[{status_color}]{row[1]}[/{status_color}]", row[2])

        console = Console()
        console.print(table)
    elif TABULATE_AVAILABLE:
        all_rows = [headers] + rows
        print(tabulate(all_rows, headers="firstrow", tablefmt="grid"))
    else:
        # Simple table without external libraries
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
        col_widths = [max(w, len(headers[i])) for i, w in enumerate(col_widths)]

        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
        header_row = "|"
        for i, header in enumerate(headers):
            header_row += f" {header.ljust(col_widths[i])} |"

        print(separator)
        print(header_row)
        print(separator)

        for row in rows:
            data_row = "|"
            for i, cell in enumerate(row):
                data_row += f" {str(cell).ljust(col_widths[i])} |"
            print(data_row)

        print(separator)


def print_enhanced_progress():
    """Print enhanced progress indicator"""
    print("\nENHANCED PROGRESS INDICATION:")

    if TQDM_AVAILABLE:
        with tqdm(total=5, desc="Processing items", unit="item") as pbar:
            for i in range(5):
                time.sleep(0.2)  # Simulate work
                pbar.set_postfix({"item": f"{i+1}/5"})
                pbar.update(1)
    elif RICH_AVAILABLE:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("Processing items", total=5)
            for i in range(5):
                time.sleep(0.2)  # Simulate work
                progress.update(task, advance=1)
    else:
        # Simple progress without external libraries
        for i in range(1, 6):
            print(f"Item {i}/5 completed")
            time.sleep(0.2)
        print("Progress: 100% complete")


def print_enhanced_status():
    """Print enhanced status information"""
    print("\nENHANCED STATUS INFORMATION:")

    if RICH_AVAILABLE:
        status_content = (
            "Application: CLI Beautifier Example\n"
            "Status: [green]✓ Running[/green]\n"
            "Version: 1.0.0\n"
            "Uptime: 00:00:05\n"
            "Tasks: [magenta]5/5 completed[/magenta]"
        )
        panel = Panel(status_content, title="Status Information")
        console = Console()
        console.print(panel)
    else:
        print("  Application: CLI Beautifier Example")
        print("  Status: ✓ Running")
        print("  Version: 1.0.0")
        print("  Uptime: 00:00:05")
        print("  Tasks: 5/5 completed")


def print_enhanced_task_list():
    """Print enhanced task list"""
    print("\nENHANCED TASK LIST:")

    tasks = [
        {"number": 1, "title": "Initialize CLI beautifier skill", "status": "✓", "color": "green"},
        {"number": 2, "title": "Test basic functionality", "status": "✓", "color": "green"},
        {"number": 3, "title": "Verify table output", "status": "✓", "color": "green"},
        {"number": 4, "title": "Check progress indicators", "status": "✓", "color": "green"},
        {"number": 5, "title": "Validate status display", "status": "✓", "color": "green"},
    ]

    if RICH_AVAILABLE:
        for task in tasks:
            color_tag = task["color"]
            rich_print(f"  [bold]{task['number']}.[/bold] [{color_tag}]{task['status']} {task['title']}[/{color_tag}]")
    elif COLORAMA_AVAILABLE:
        for task in tasks:
            color_map = {
                "green": Fore.GREEN,
                "yellow": Fore.YELLOW,
                "red": Fore.RED
            }
            color = color_map.get(task["color"], Fore.WHITE)
            print(f"  \033[1m{task['number']}.\033[0m {color}{task['status']} {task['title']}{Style.RESET_ALL}")
    else:
        for task in tasks:
            print(f"  {task['number']}. {task['status']} {task['title']}")


def print_enhanced_container():
    """Print enhanced content container"""
    print("\nENHANCED CONTENT CONTAINER:")

    content = [
        "This is content in an enhanced container",
        "Multiple lines work too",
        "Enhanced CLI functionality is working",
        "Visual improvements applied successfully"
    ]

    if RICH_AVAILABLE:
        content_text = "\n".join(content)
        panel = Panel(content_text, title="Content Container")
        console = Console()
        console.print(panel)
    else:
        max_len = max(len(line) for line in content)
        border = "╔" + "═" * (max_len + 2) + "╗"
        print(border)
        for line in content:
            padding = max_len - len(line)
            print(f"║ {line}{' ' * padding} ║")
        print("╚" + "═" * (max_len + 2) + "╝")


def main():
    """Main function to demonstrate all features"""
    print_header()
    print_enhanced_messages()
    print_enhanced_table()
    print_enhanced_progress()
    print_enhanced_status()
    print_enhanced_task_list()
    print_enhanced_container()

    print("\n✓ All tasks completed successfully!")

    if RICH_AVAILABLE:
        console = Console()
        console.print(Panel("[bold green]PYTHON CLI BEAUTIFIER COMPLETE EXAMPLE![/bold green]\n[bold white]All functionality demonstrated and ready for use.[/bold white]", expand=False))
    else:
        print("\nPYTHON CLI BEAUTIFIER COMPLETE EXAMPLE!")
        print("All functionality demonstrated and ready for use.")


if __name__ == "__main__":
    main()