from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.broker import broker_taskiq
from app.configuration.routes import setup_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not broker_taskiq.is_worker_process:
        await broker_taskiq.startup()
    yield
    if not broker_taskiq.is_worker_process:
        await broker_taskiq.shutdown()

def get_app() -> FastAPI:
    application = FastAPI(
        title="Task Tracker Layered",
        description="Clean Architecture implementation",
        version="1.0.0",
        lifespan=lifespan
    )
    setup_routes(application)
    return application

app = get_app()
