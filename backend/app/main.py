'''FastAPI application entry point.'''

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base

# Add project root to path for cross-module imports (engine)
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.api.auth import router as auth_router
from app.api.templates import router as templates_router
from app.api.variables import router as variables_router
from app.api.documents import router as documents_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    import app.models  # noqa: ensure models are registered
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(variables_router)
app.include_router(documents_router)
app.include_router(tasks_router)
app.include_router(users_router)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.APP_VERSION}
