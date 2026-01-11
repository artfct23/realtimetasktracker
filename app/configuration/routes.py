from fastapi import FastAPI
from app.internal.routes import auth, users, projects, tasks, comments

def setup_routes(app: FastAPI):
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(projects.router, prefix="/projects", tags=["Projects"])
    app.include_router(tasks.router, tags=["Tasks"])
    app.include_router(comments.router, tags=["Comments"])
