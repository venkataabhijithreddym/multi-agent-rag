
from fastmcp import FastMCP
from sqlalchemy.orm import Session
from app.database import SessionLocal, TodoItem
from datetime import datetime, timezone

mcp = FastMCP("Todo Server")


def _get_db() -> Session:
    return SessionLocal()


@mcp.tool()
def create_task(title: str, description: str = "", user_id: int = 1) -> dict:
    """Create a new todo task."""
    db = _get_db()
    try:
        item = TodoItem(user_id=user_id, title=title, description=description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"id": item.id, "title": item.title, "description": item.description, "completed": item.completed}
    finally:
        db.close()


@mcp.tool()
def list_tasks(user_id: int = 1) -> list[dict]:
    """List all todo tasks for a user."""
    db = _get_db()
    try:
        items = db.query(TodoItem).filter(TodoItem.user_id == user_id).all()
        return [
            {"id": i.id, "title": i.title, "description": i.description, "completed": i.completed}
            for i in items
        ]
    finally:
        db.close()


@mcp.tool()
def update_task(task_id: int, title: str = "", description: str = "", completed: bool = None, user_id: int = 1) -> dict:
    """Update a todo task by ID."""
    db = _get_db()
    try:
        item = db.query(TodoItem).filter(TodoItem.id == task_id, TodoItem.user_id == user_id).first()
        if not item:
            return {"error": f"Task {task_id} not found"}
        if title:
            item.title = title
        if description:
            item.description = description
        if completed is not None:
            item.completed = completed
        item.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(item)
        return {"id": item.id, "title": item.title, "description": item.description, "completed": item.completed}
    finally:
        db.close()


@mcp.tool()
def delete_task(task_id: int, user_id: int = 1) -> dict:
    """Delete a todo task by ID."""
    db = _get_db()
    try:
        item = db.query(TodoItem).filter(TodoItem.id == task_id, TodoItem.user_id == user_id).first()
        if not item:
            return {"error": f"Task {task_id} not found"}
        db.delete(item)
        db.commit()
        return {"deleted": True, "id": task_id}
    finally:
        db.close()