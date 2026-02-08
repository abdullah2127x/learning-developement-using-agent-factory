#!/usr/bin/env python3
"""
progress_bar.py - Implementation of progress bars for Python CLI applications
"""

import sys
import time

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    from rich.progress import Progress, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def create_tqdm_progress(total=100, description="Processing"):
    """Create a progress bar using tqdm library"""
    if not TQDM_AVAILABLE:
        raise ImportError("tqdm library is not available")

    with tqdm(total=total, desc=description, unit="item") as pbar:
        for i in range(total):
            # Simulate work
            time.sleep(0.01)  # Replace with actual work
            pbar.update(1)


def create_rich_progress(total=100, description="Processing"):
    """Create a progress bar using rich library"""
    if not RICH_AVAILABLE:
        raise ImportError("rich library is not available")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(description, total=total)
        for i in range(total):
            # Simulate work
            time.sleep(0.01)  # Replace with actual work
            progress.update(task, advance=1)


def create_simple_progress(current, total, description="Processing"):
    """Create a simple text-based progress indicator"""
    percentage = int((current / total) * 100)
    bar_length = 30
    filled_length = int(bar_length * current // total)

    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    sys.stdout.write(f'\r{description}: |{bar}| {percentage}% ({current}/{total})')
    sys.stdout.flush()

    if current == total:
        print()  # New line when complete


def simulate_progress_with_simple(total=50, description="Processing"):
    """Simulate progress using simple progress indicator"""
    for i in range(total + 1):
        create_simple_progress(i, total, description)
        time.sleep(0.05)  # Simulate work


# Example usage
if __name__ == "__main__":
    print("Simple progress bar simulation:")
    simulate_progress_with_simple(20, "Items")

    if TQDM_AVAILABLE:
        print("\nTqdm progress bar:")
        create_tqdm_progress(10, "Items")

    if RICH_AVAILABLE:
        print("\nRich progress bar:")
        create_rich_progress(10, "Items")