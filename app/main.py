





from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables
from app.rag.ingestion import ingest_faqs
from app.api import auth, chat, weather, todos
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating database tables...")
    create_tables()
    logger.info("Ingesting FAQ data into ChromaDB (skipped if already indexed)...")
    count = ingest_faqs()
    logger.info("FAQ index ready with %d documents.", count)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Multi-Agent RAG System",
    description="A multi-agent AI system with RAG, weather, and todo management.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(todos.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}