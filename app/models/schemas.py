


from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Auth ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Chat ---
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    agent_used: str


# --- Weather ---
class WeatherResponse(BaseModel):
    city: str
    description: str
    temperature_c: float
    humidity: int
    wind_kmh: float
    raw: Optional[str] = None


# --- Todo ---
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = ""


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoOut(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}