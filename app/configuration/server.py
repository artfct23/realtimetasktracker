import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.broker import broker_taskiq
from app.configuration.routes import setup_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not broker_taskiq.is_worker_process:
        for i in range(15):
            try:
                await broker_taskiq.startup()
                print("--- Broker connected successfully! ---")
                break
            except Exception as e:
                print(f"Broker connection failed ({e}), retrying in 2s... (attempt {i + 1}/15)")
                await asyncio.sleep(2)
        else:
            print("Could not connect to broker after 15 attempts.")

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

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_routes(application)
    return application


app = get_app()

