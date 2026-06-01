

from langchain_core.tools import tool
from app.database import SessionLocal, TodoItem
from datetime import datetime, timezone


@tool
def todo_create_task(title: str, description: str = "", user_id: int = 1) -> str:
    """Create a new todo task with a title and optional description."""
    db = SessionLocal()
    try:
        item = TodoItem(user_id=user_id, title=title, description=description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return f"Task created: [ID {item.id}] {item.title}"
    finally:
        db.close()


@tool
def todo_list_tasks(user_id: int = 1) -> str:
    """List all todo tasks for a user."""
    db = SessionLocal()
    try:
        items = db.query(TodoItem).filter(TodoItem.user_id == user_id).all()
        if not items:
            return "No tasks found."
        return "\n".join(
            f"[ID {i.id}] {'✓' if i.completed else '○'} {i.title}: {i.description}"
            for i in items
        )
    finally:
        db.close()


@tool
def todo_update_task(task_id: int, title: str = "", description: str = "", completed: bool = None, user_id: int = 1) -> str:
    """Update a todo task by its ID. Provide only the fields you want to change."""
    db = SessionLocal()
    try:
        item = db.query(TodoItem).filter(TodoItem.id == task_id, TodoItem.user_id == user_id).first()
        if not item:
            return f"Task {task_id} not found."
        if title:
            item.title = title
        if description:
            item.description = description
        if completed is not None:
            item.completed = completed
        item.updated_at = datetime.now(timezone.utc)
        db.commit()
        return f"Task {task_id} updated successfully."
    finally:
        db.close()


@tool
def todo_delete_task(task_id: int, user_id: int = 1) -> str:
    """Delete a todo task by its ID."""
    db = SessionLocal()
    try:
        item = db.query(TodoItem).filter(TodoItem.id == task_id, TodoItem.user_id == user_id).first()
        if not item:
            return f"Task {task_id} not found."
        db.delete(item)
        db.commit()
        return f"Task {task_id} deleted successfully."
    finally:
        db.close()