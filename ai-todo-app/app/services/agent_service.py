from agents import function_tool
from agents.run import RunConfig

from sqlmodel import Session


from app.database.session import engine
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.services.todo import TodoService

# ── Formatting ───────────────────────────────────────────────────────




def _format_todo(todo: Todo) -> str:
    """Format a single todo into a readable string for the agent."""
    return (
        f"[ID: {todo.id}] {todo.title}\n"
        f"  Status: {todo.status} | Priority: {todo.priority} | "
        f"Completed: {todo.completed}\n"
        f"  Description: {todo.description or '(none)'}\n"
        f"  Created: {todo.created_at:%Y-%m-%d %H:%M} | "
        f"Updated: {todo.updated_at:%Y-%m-%d %H:%M}"
    )


# ── Function tools (CRUD) ───────────────────────────────────────────


@function_tool
def list_todos(offset: int = 0, limit: int = 20) -> str:
    """
    List all todos from the database with pagination.

    Args:
        offset: Number of todos to skip from the start (default: 0).
        limit: Maximum number of todos to return (default: 20, max: 100).

    Returns:
        A formatted list of todos with their ID, title, status, priority,
        and completion state. Returns a message if no todos exist.
    """
    with Session(engine) as session:
        service = TodoService(session)
        todos = service.get_all(offset=offset, limit=min(limit, 100))

    if not todos:
        return "No todos found. The list is empty."

    lines = [f"Found {len(todos)} todo(s):\n"]
    for todo in todos:
        lines.append(_format_todo(todo))
    return "\n\n".join(lines)


@function_tool
def get_todo(todo_id: int) -> str:
    """
    Get a single todo by its ID.

    Args:
        todo_id: The unique numeric ID of the todo to retrieve.

    Returns:
        Detailed information about the todo including title, description,
        status, priority, completion state, and timestamps.
        Returns an error message if the todo is not found.
    """
    with Session(engine) as session:
        service = TodoService(session)
        try:
            todo = service.get_by_id(todo_id)
        except Exception:
            return f"Error: Todo with ID {todo_id} not found."
    return _format_todo(todo)


@function_tool
def create_todo(
    title: str,
    description: str = "",
    priority: str = "medium",
    status: str = "pending",
) -> str:
    """
    Create a new todo item in the database.

    Args:
        title: The title of the todo (1-200 characters, required).
        description: Optional detailed description of the todo.
        priority: Priority level — one of "low", "medium", or "high"
                  (default: "medium").
        status: Initial status — one of "pending", "in_progress", or
                "completed" (default: "pending").

    Returns:
        The newly created todo with its assigned ID and all fields.
        Returns an error message if validation fails.
    """
    try:
        data = TodoCreate(
            title=title,
            description=description or None,
            priority=priority,
            status=status,
        )
    except Exception as e:
        return f"Validation error: {e}"

    with Session(engine) as session:
        service = TodoService(session)
        todo = service.create(data)
    return f"Todo created successfully!\n\n{_format_todo(todo)}"


@function_tool
def update_todo(
    todo_id: int,
    title: str = "",
    description: str = "",
    priority: str = "",
    status: str = "",
    completed: bool = False,
) -> str:
    """
    Update an existing todo by its ID. Only provided fields are changed.

    Args:
        todo_id: The unique numeric ID of the todo to update.
        title: New title (1-200 characters). Leave empty to keep current.
        description: New description. Leave empty to keep current.
        priority: New priority — "low", "medium", or "high".
                  Leave empty to keep current.
        status: New status — "pending", "in_progress", or "completed".
                Leave empty to keep current.
        completed: Set to true to mark as completed, false to keep current.

    Returns:
        The updated todo with all fields. Returns an error message
        if the todo is not found or validation fails.
    """
    update_fields: dict = {}
    if title:
        update_fields["title"] = title
    if description:
        update_fields["description"] = description
    if priority:
        update_fields["priority"] = priority
    if status:
        update_fields["status"] = status
    if completed:
        update_fields["completed"] = completed

    if not update_fields:
        return (
            "Error: No fields provided to update. Specify at least one field to change."
        )

    try:
        data = TodoUpdate(**update_fields)
    except Exception as e:
        return f"Validation error: {e}"

    with Session(engine) as session:
        service = TodoService(session)
        try:
            todo = service.update(todo_id, data)
        except Exception:
            return f"Error: Todo with ID {todo_id} not found."
    return f"Todo updated successfully!\n\n{_format_todo(todo)}"


@function_tool
def delete_todo(todo_id: int) -> str:
    """
    Permanently delete a todo by its ID.

    Args:
        todo_id: The unique numeric ID of the todo to delete.

    Returns:
        A confirmation message if deleted successfully.
        Returns an error message if the todo is not found.
    """
    with Session(engine) as session:
        service = TodoService(session)
        try:
            service.delete(todo_id)
        except Exception:
            return f"Error: Todo with ID {todo_id} not found."
    return f"Todo with ID {todo_id} deleted successfully."


