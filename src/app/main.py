from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.apps.auth.router import router as auth_router
from src.app.core.deps import get_db_session
from src.app.db.session import Database
from src.app.settings import settings


def create_app() -> FastAPI:
    db = Database(settings.ASYNC_DATABASE_URL, echo=settings.DEBUG)

    async def _get_db_session():
        async for session in db.get_session():
            yield session

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("startup: performing lightweight app checks")
        yield
        print("shutdown: cleaning up")
        await db.dispose()

    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.dependency_overrides[get_db_session] = _get_db_session
    app.include_router(auth_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
