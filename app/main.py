from fastapi import FastAPI
from app.core.database import engine, Base


app = FastAPI(
    title="RAG - Contratações Públicas"
)


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "API funcionando"
    }