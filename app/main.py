from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.broker import broker_taskiq
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router
from app.api.comments import router as comments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not broker_taskiq.is_worker_process:
        await broker_taskiq.startup()
    yield
    if not broker_taskiq.is_worker_process:
        await broker_taskiq.shutdown()

app = FastAPI(title="Task Tracker Realtime", lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])
app.include_router(tasks_router, tags=["Tasks"])
app.include_router(comments_router, tags=["Comments"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}


