#!/usr/bin/env python3
"""
format_table.py - Utility for creating formatted tables in Python CLI applications
"""

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

try:
    from rich.table import Table
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def create_rich_table(headers, rows):
    """Create a formatted table using rich library"""
    if not RICH_AVAILABLE:
        raise ImportError("rich library is not available")

    table = Table(show_header=True, header_style="bold blue")

    # Add headers
    for header in headers:
        table.add_column(header, style="dim")

    # Add rows
    for row in rows:
        table.add_row(*[str(item) for item in row])

    console = Console()
    console.print(table)


def create_tabulate_table(headers, rows, table_format="grid"):
    """Create a formatted table using tabulate library"""
    if not TABULATE_AVAILABLE:
        raise ImportError("tabulate library is not available")

    all_rows = [headers] + rows
    return tabulate(all_rows, headers="firstrow", tablefmt=table_format)


def create_simple_table(headers, rows):
    """Create a simple formatted table without external libraries"""
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


# Example usage
if __name__ == "__main__":
    headers = ["Name", "Status", "Last Updated"]
    rows = [
        ["Project A", "Active", "2026-01-06"],
        ["Project B", "Warn", "2026-01-05"],
        ["Project C", "Error", "2026-01-04"]
    ]

    print("Simple formatted table:")
    print(create_simple_table(headers, rows))

    if TABULATE_AVAILABLE:
        print("\nTabulate formatted table:")
        print(create_tabulate_table(headers, rows))

    if RICH_AVAILABLE:
        print("\nRich formatted table:")
        create_rich_table(headers, rows)