from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.core.security import dummy_password_hash, validate_security_settings
from app.modules.admin.routes import router as admin_router
from app.modules.auth.routes import router as auth_router
from app.modules.query.routes import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_security_settings()
    dummy_password_hash()
    init_db()
    yield


app = FastAPI(
    title="RAG - Contratações Públicas",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }
