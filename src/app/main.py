from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup: performing lightweight app checks")
    yield
    print("shutdown: cleaning up")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
