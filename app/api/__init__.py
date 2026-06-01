
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.weather import router as weather_router
from app.api.todos import router as todos_router

__all__ = ["auth_router", "chat_router", "weather_router", "todos_router"]