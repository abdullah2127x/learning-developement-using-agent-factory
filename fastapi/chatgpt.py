"""
============================================================================
WEEK 2: ASYNC/AWAIT MASTERY - TOPIC 2: CONCURRENT EXECUTION
============================================================================
Roadmap Reference: LEARNING_ROADMAP.md - Week 2, Section 2
Priority: MEDIUM 🟡

What You'll Learn:
    ✓ asyncio.gather() - run multiple tasks
    ✓ asyncio.wait() - wait for tasks with options
    ✓ asyncio.create_task() - schedule coroutines
    ✓ Task cancellation and timeouts
    ✓ Race conditions in async code
    ✓ Async locks and semaphores
============================================================================
"""

import asyncio
import time
import random

# ============================================================================
# PART 1: asyncio.gather() - Deep Dive
# ============================================================================

print("=" * 70)
"PART 1: asyncio.gather() - ADVANCED USAGE"
print("=" * 70)

async def fetch_data(source, delay):
    """Simulate fetching data from a source"""
    await asyncio.sleep(delay)
    return f"Data from {source}"

async def demonstrate_gather():
    # Basic usage (you already know this)
    print("\n--- Basic gather() ---")
    results = await asyncio.gather(
        fetch_data("API 1", 1),
        fetch_data("API 2", 1),
        fetch_data("API 3", 1),
    )
    print(f"Results: {results}")
    
    # With return_exceptions=True (important for production!)
    print("\n--- gather() with error handling ---")
    
    async def sometimes_fails(source, delay):
        if source == "API 2":
            raise Exception(f"{source} failed!")
        await asyncio.sleep(delay)
        return f"Data from {source}"
    
    results = await asyncio.gather(
        sometimes_fails("API 1", 1),
        sometimes_fails("API 2", 1),
        sometimes_fails("API 3", 1),
        return_exceptions=True  # ← Don't fail everything if one fails
    )
    
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"  ❌ API {i} failed: {result}")
        else:
            print(f"  ✅ API {i} succeeded: {result}")
    
    # Unpacking results
    print("\n--- gather() with unpacking ---")
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    fail_count = sum(1 for r in results if isinstance(r, Exception))
    print(f"Success: {success_count}, Failed: {fail_count}")

asyncio.run(demonstrate_gather())

# ============================================================================
# PART 2: asyncio.wait() - More Control
# ============================================================================

print("\n" + "=" * 70)
"PART 2: asyncio.wait() - FINE-GRAINED CONTROL"
print("=" * 70)

async def demonstrate_wait():
    """
    asyncio.wait() gives you more control than gather():
    - Wait for FIRST_COMPLETED
    - Wait for FIRST_EXCEPTION
    - Wait for ALL_COMPLETED (default)
    """
    
    async def task_with_delay(name, delay):
        await asyncio.sleep(delay)
        return f"Result from {name}"
    
    # Create tasks
    tasks = [
        asyncio.create_task(task_with_delay("Fast", 0.5)),
        asyncio.create_task(task_with_delay("Medium", 1.0)),
        asyncio.create_task(task_with_delay("Slow", 2.0)),
    ]
    
    # Wait for first task to complete
    print("\n--- wait() with FIRST_COMPLETED ---")
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    print(f"Completed: {len(done)}")
    for t in done:
        print(f"  ✅ {t.result()}")
    
    print(f"Still pending: {len(pending)}")
    
    # Cancel pending tasks
    for t in pending:
        t.cancel()
    
    # Wait for all to finish (cancelled or completed)
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
    
    # Wait for first exception
    print("\n--- wait() with FIRST_EXCEPTION ---")
    
    async def might_fail(name, delay, fail=False):
        await asyncio.sleep(delay)
        if fail:
            raise Exception(f"{name} failed!")
        return f"Result from {name}"
    
    tasks = [
        asyncio.create_task(might_fail("Task 1", 0.5, fail=False)),
        asyncio.create_task(might_fail("Task 2", 1.0, fail=True)),  # Will fail
        asyncio.create_task(might_fail("Task 3", 1.5, fail=False)),
    ]
    
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION
    )
    
    print(f"Completed/Failed: {len(done)}")
    for t in done:
        try:
            print(f"  Result: {t.result()}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    # Cancel remaining
    for t in pending:
        t.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)

asyncio.run(demonstrate_wait())

# ============================================================================
# PART 3: Task Cancellation
# ============================================================================

print("\n" + "=" * 70)
"PART 3: TASK CANCELLATION"
print("=" * 70)

async def cancellable_task(name, duration):
    """A task that can be cancelled"""
    try:
        print(f"  [{name}] Starting work...")
        for i in range(duration):
            print(f"  [{name}] Working... {i+1}/{duration}")
            await asyncio.sleep(0.5)
        print(f"  [{name}] Completed!")
        return f"Result from {name}"
    except asyncio.CancelledError:
        print(f"  [{name}] ❌ Was cancelled! Cleaning up...")
        # Cleanup code here (close files, connections, etc.)
        raise  # Re-raise to properly signal cancellation

async def demonstrate_cancellation():
    print("\n--- Cancelling a long-running task ---")
    
    # Start a long task
    task = asyncio.create_task(cancellable_task("LongTask", 10))
    
    # Wait a bit, then cancel
    await asyncio.sleep(1.5)
    print("\nCancelling task...")
    task.cancel()
    
    # Wait for cancellation to complete
    try:
        await task
    except asyncio.CancelledError:
        print("Task was successfully cancelled\n")
    
    # Graceful cancellation with timeout
    print("--- Graceful cancellation with timeout ---")
    
    async def run_with_timeout(task_name, timeout):
        task = asyncio.create_task(cancellable_task(task_name, 10))
        try:
            # Wait for task with timeout
            await asyncio.wait_for(asyncio.shield(task), timeout=timeout)
            return task.result()
        except asyncio.TimeoutError:
            print(f"Timeout! Cancelling {task_name}...")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                return f"{task_name} was cancelled after timeout"
    
    result = await run_with_timeout("TimedTask", 2)
    print(f"Result: {result}")

asyncio.run(demonstrate_cancellation())

# ============================================================================
# PART 4: Timeouts with asyncio.wait_for()
# ============================================================================

print("\n" + "=" * 70)
"PART 4: TIMEOUTS"
print("=" * 70)

async def slow_operation(duration):
    """Simulates a slow operation"""
    print(f"  Starting slow operation ({duration}s)...")
    await asyncio.sleep(duration)
    print(f"  Operation complete!")
    return "Success"

async def demonstrate_timeouts():
    # Timeout that doesn't trigger
    print("\n--- Timeout (operation completes in time) ---")
    try:
        result = await asyncio.wait_for(
            slow_operation(1),
            timeout=3.0
        )
        print(f"✅ Result: {result}")
    except asyncio.TimeoutError:
        print("❌ Operation timed out!")
    
    # Timeout that triggers
    print("\n--- Timeout (operation too slow) ---")
    try:
        result = await asyncio.wait_for(
            slow_operation(5),
            timeout=2.0
        )
        print(f"✅ Result: {result}")
    except asyncio.TimeoutError:
        print("❌ Operation timed out!")
    
    # Real-world example: API call with timeout
    print("\n--- Real-world: API call with timeout ---")
    
    async def fetch_user_api(user_id):
        # Simulate API call
        await asyncio.sleep(random.uniform(0.5, 3.0))
        return {"id": user_id, "name": f"User {user_id}"}
    
    async def fetch_with_timeout(user_id, timeout=2.0):
        try:
            return await asyncio.wait_for(
                fetch_user_api(user_id),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"  ⚠️  User {user_id} API timed out")
            return None
    
    # Fetch multiple users, some might timeout
    results = await asyncio.gather(
        fetch_with_timeout(1),
        fetch_with_timeout(2),
        fetch_with_timeout(3),
    )
    
    print(f"Results: {results}")
    successful = [r for r in results if r is not None]
    print(f"Successful: {len(successful)}/{len(results)}")

asyncio.run(demonstrate_timeouts())

# ============================================================================
# PART 5: Race Conditions & Async Locks
# ============================================================================

print("\n" + "=" * 70)
"PART 5: RACE CONDITIONS & LOCKS"
print("=" * 70)

# Shared resource (simulated database)
shared_counter = 0

async def unsafe_increment(task_id, times):
    """Unsafe: Multiple tasks modifying shared state"""
    global shared_counter
    for _ in range(times):
        current = shared_counter
        await asyncio.sleep(0.01)  # Simulate some work
        shared_counter = current + 1
    print(f"  [Task {task_id}] Done")

async def demonstrate_race_condition():
    global shared_counter
    shared_counter = 0
    
    print("\n--- Race Condition Example (UNSAFE) ---")
    print(f"Starting counter: {shared_counter}")
    
    # 3 tasks each increment 100 times
    await asyncio.gather(
        unsafe_increment(1, 100),
        unsafe_increment(2, 100),
        unsafe_increment(3, 100),
    )
    
    print(f"Final counter: {shared_counter}")
    print(f"Expected: 300, Got: {shared_counter}")
    print("❌ Race condition! Some increments were lost!")

asyncio.run(demonstrate_race_condition())

# Now with lock
async def safe_increment(lock, task_id, times):
    """Safe: Using lock to protect shared state"""
    global shared_counter
    for _ in range(times):
        async with lock:
            current = shared_counter
            await asyncio.sleep(0.01)
            shared_counter = current + 1
    print(f"  [Task {task_id}] Done")

async def demonstrate_lock():
    global shared_counter
    shared_counter = 0
    
    print("\n--- Using asyncio.Lock (SAFE) ---")
    print(f"Starting counter: {shared_counter}")
    
    lock = asyncio.Lock()
    
    await asyncio.gather(
        safe_increment(lock, 1, 100),
        safe_increment(lock, 2, 100),
        safe_increment(lock, 3, 100),
    )
    
    print(f"Final counter: {shared_counter}")
    print(f"Expected: 300, Got: {shared_counter}")
    print("✅ No race condition! All increments counted!")

asyncio.run(demonstrate_lock())

# ============================================================================
# PART 6: Async Semaphores (Limit Concurrent Operations)
# ============================================================================

print("\n" + "=" * 70)
"PART 6: ASYNC SEMAPHORES"
print("=" * 70)

async def api_request(semaphore, request_id):
    """API request with rate limiting"""
    async with semaphore:
        print(f"  [Request {request_id}] Starting...")
        await asyncio.sleep(0.5)  # Simulate API call
        print(f"  [Request {request_id}] Complete")
        return f"Result {request_id}"

async def demonstrate_semaphore():
    print("\n--- Without Semaphore (unlimited concurrent) ---")
    # All 10 requests start at once
    await asyncio.gather(*[
        api_request_no_limit(i) for i in range(10)
    ])
    
    print("\n--- With Semaphore (max 3 concurrent) ---")
    # Only 3 requests at a time
    semaphore = asyncio.Semaphore(3)
    
    await asyncio.gather(*[
        api_request(semaphore, i) for i in range(10)
    ])

async def api_request_no_limit(request_id):
    print(f"  [Request {request_id}] Starting...")
    await asyncio.sleep(0.5)
    print(f"  [Request {request_id}] Complete")
    return f"Result {request_id}"

asyncio.run(demonstrate_semaphore())

# ============================================================================
# PART 7: PRACTICAL EXAMPLE - Retry with Exponential Backoff
# ============================================================================

print("\n" + "=" * 70)
"PART 7: RETRY WITH EXPONENTIAL BACKOFF"
print("=" * 70)

async def flaky_api_call():
    """Simulates an unreliable API"""
    if random.random() < 0.7:  # 70% chance of failure
        raise ConnectionError("API temporarily unavailable")
    return "Success!"

async def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    """
    Retry a function with exponential backoff.
    
    Delay pattern: 1s, 2s, 4s, 8s, ...
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            delay = base_delay * (2 ** attempt)
            print(f"  Attempt {attempt + 1} failed: {e}")
            print(f"  Retrying in {delay}s...")
            await asyncio.sleep(delay)
    
    print(f"  All {max_retries} attempts failed!")
    raise last_exception

async def demonstrate_retry():
    print("\n--- Retry with Exponential Backoff ---")
    
    # Set seed for reproducibility
    random.seed(42)
    
    try:
        result = await retry_with_backoff(flaky_api_call, max_retries=5)
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ All retries exhausted: {e}")

asyncio.run(demonstrate_retry())

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY: CONCURRENT EXECUTION PATTERNS")
print("=" * 70)

summary = """
┌─────────────────────────────────────────────────────────────────┐
│                    CONCURRENT EXECUTION                         │
├─────────────────────────────────────────────────────────────────┤
│ asyncio.gather(a, b)     → Run all, wait for all                │
│                          → Use return_exceptions=True for safety │
├─────────────────────────────────────────────────────────────────┤
│ asyncio.wait(tasks)      → More control than gather             │
│   FIRST_COMPLETED        → Return when any task finishes        │
│   FIRST_EXCEPTION        → Return when any task fails           │
│   ALL_COMPLETED          → Wait for all (default)               │
├─────────────────────────────────────────────────────────────────┤
│ task.cancel()            → Cancel a task                        │
│ asyncio.CancelledError   → Catch to cleanup before exit         │
├─────────────────────────────────────────────────────────────────┤
│ asyncio.wait_for(coro, timeout) → Timeout for operations        │
│ asyncio.TimeoutError     → Raised when timeout exceeded         │
├─────────────────────────────────────────────────────────────────┤
│ asyncio.Lock()           → Prevent race conditions              │
│ async with lock:         → Safe access to shared state          │
├─────────────────────────────────────────────────────────────────┤
│ asyncio.Semaphore(n)     → Limit concurrent operations to n     │
│ async with semaphore:    → Rate limiting pattern                │
├─────────────────────────────────────────────────────────────────┤
│ Retry Pattern:           → Exponential backoff                  │
│   delay = base * (2 ** attempt)  → 1s, 2s, 4s, 8s...            │
└─────────────────────────────────────────────────────────────────┘
"""
print(summary)

print("\n" + "=" * 70)
print("✅ TOPIC 2 COMPLETE: Concurrent Execution")
print("📚 NEXT: Topic 3 - Async Generators")
print("=" * 70)
