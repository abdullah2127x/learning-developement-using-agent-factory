"""
Sync vs Async -- See the difference with your own eyes.

Run this file:  python sync_vs_async_example.py
"""

import asyncio
import time


# ============================================================
# PART 1: SYNC -- One thing at a time
# ============================================================

def make_tea_sync():
    """Simulates making tea -- takes 3 seconds"""
    print("  [TEA] Started making tea...")
    time.sleep(3)  # Blocks everything for 3 seconds
    print("  [TEA] Tea is ready!")
    return "tea"


def make_toast_sync():
    """Simulates making toast -- takes 2 seconds"""
    print("  [TOAST] Started making toast...")
    time.sleep(2)  # Blocks everything for 2 seconds
    print("  [TOAST] Toast is ready!")
    return "toast"


def make_egg_sync():
    """Simulates making egg -- takes 4 seconds"""
    print("  [EGG] Started making egg...")
    time.sleep(4)  # Blocks everything for 4 seconds
    print("  [EGG] Egg is ready!")
    return "egg"


def sync_breakfast():
    """
    SYNC: Does one thing, waits, then starts the next.

    Timeline:
    0s -----> tea (3s) -----> toast (2s) -----> egg (4s) -----> done at 9s
    """
    print("\n" + "=" * 60)
    print("SYNC BREAKFAST -- One task at a time")
    print("=" * 60)

    start = time.time()

    make_tea_sync()      # Wait 3s
    make_toast_sync()    # Then wait 2s
    make_egg_sync()      # Then wait 4s

    total = time.time() - start
    print(f"\n  Total time: {total:.1f} seconds (3 + 2 + 4 = 9s)")
    print("  ^ Each task waited for the previous one to finish!")


# ============================================================
# PART 2: ASYNC -- Start all, switch while waiting
# ============================================================

async def make_tea_async():
    """Simulates making tea -- takes 3 seconds"""
    print("  [TEA] Started making tea...")
    await asyncio.sleep(3)  # "I'll wait, go do other stuff"
    print("  [TEA] Tea is ready!")
    return "tea"


async def make_toast_async():
    """Simulates making toast -- takes 2 seconds"""
    print("  [TOAST] Started making toast...")
    await asyncio.sleep(2)  # "I'll wait, go do other stuff"
    print("  [TOAST] Toast is ready!")
    return "toast"


async def make_egg_async():
    """Simulates making egg -- takes 4 seconds"""
    print("  [EGG] Started making egg...")
    await asyncio.sleep(4)  # "I'll wait, go do other stuff"
    print("  [EGG] Egg is ready!")
    return "egg"


async def async_breakfast():
    """
    ASYNC: Start all tasks, switch between them while waiting.

    Timeline:
    0s -----> tea starts
    0s -----> toast starts (at the same time!)
    0s -----> egg starts   (at the same time!)
    2s -----> toast done
    3s -----> tea done
    4s -----> egg done     -----> total = 4s (the longest task)
    """
    print("\n" + "=" * 60)
    print("ASYNC BREAKFAST -- All tasks at once")
    print("=" * 60)

    start = time.time()

    # Start ALL tasks at the same time
    await asyncio.gather(
        make_tea_async(),
        make_toast_async(),
        make_egg_async(),
    )

    total = time.time() - start
    print(f"\n  Total time: {total:.1f} seconds (max of 3, 2, 4 = 4s)")
    print("  ^ All tasks ran at the same time!")


# ============================================================
# PART 3: THE PROBLEM -- Sync call inside async (your scenario)
# ============================================================

async def make_tea_BLOCKING():
    """
    BAD: Uses time.sleep (sync/blocking) inside an async function.
    This is what happens when you use session.commit() inside async def.
    """
    print("  [TEA] Started making tea...")
    time.sleep(3)  # BAD - BLOCKS the event loop! No switching!
    print("  [TEA] Tea is ready!")
    return "tea"


async def make_toast_BLOCKING():
    print("  [TOAST] Started making toast...")
    time.sleep(2)  # BAD - BLOCKS the event loop!
    print("  [TOAST] Toast is ready!")
    return "toast"


async def make_egg_BLOCKING():
    print("  [EGG] Started making egg...")
    time.sleep(4)  # BAD - BLOCKS the event loop!
    print("  [EGG] Egg is ready!")
    return "egg"


async def broken_async_breakfast():
    """
    BROKEN ASYNC: Functions are async but use blocking calls inside.

    This is EXACTLY your scenario:
      async def create_student(...):
          session.commit()    <-- blocking call, like time.sleep()

    It "works" but takes 9 seconds instead of 4.
    You get the WORST of both worlds -- async syntax, sync performance.
    """
    print("\n" + "=" * 60)
    print("BROKEN ASYNC -- sync blocking calls inside async functions")
    print("(This is what happens with session.commit() in async def)")
    print("=" * 60)

    start = time.time()

    await asyncio.gather(
        make_tea_BLOCKING(),
        make_toast_BLOCKING(),
        make_egg_BLOCKING(),
    )

    total = time.time() - start
    print(f"\n  Total time: {total:.1f} seconds (still 9s, not 4s!)")
    print("  ^ Even though we used async, blocking calls froze everything!")
    print("  THIS is why session.commit() in async def is a problem.")


# ============================================================
# RUN ALL EXAMPLES
# ============================================================

if __name__ == "__main__":
    print("SYNC vs ASYNC -- Breakfast Example")
    print("Watch the time difference!\n")

    # 1. Sync -- takes ~9 seconds
    # sync_breakfast()

    # 2. Proper Async -- takes ~4 seconds
    # asyncio.run(async_breakfast())

    # 3. Broken Async (your scenario) -- takes ~9 seconds
    asyncio.run(broken_async_breakfast())

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
  sync def + time.sleep()         = 9s (but FastAPI uses threadpool, so OK)
  async def + await asyncio.sleep = 4s (proper async, best performance)
  async def + time.sleep()        = 9s (BROKEN -- blocks the event loop)
                                         ^
                                    This is your case:
                                    async def + session.commit()
                                    commit() is like time.sleep() -- it blocks.
    """)
