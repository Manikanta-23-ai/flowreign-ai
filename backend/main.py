
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from backend.api.reports import router as reports_router
from backend.api.operations import router as operations_router

from fastapi import FastAPI

from backend.api.workflows import router as workflow_router
from backend.api.data import router as data_router
from backend.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("FlowReign AI database initialized.")
    yield


app = FastAPI(
    title="FlowReign AI",
    description=(
        "Intelligence That Executes. "
        "An open-source business operations intelligence platform."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

app.include_router(workflow_router)
app.include_router(reports_router)
app.include_router(operations_router)
app.include_router(data_router)


@app.get("/")
def root():
    return {
        "name": "FlowReign AI",
        "tagline": "Intelligence That Executes.",
        "version": "0.3.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FlowReign AI API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
