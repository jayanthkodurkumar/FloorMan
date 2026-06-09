import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth.routes import router as auth_router
from api.chat.routes import router as chat_router

app = FastAPI(
    title="Manufacturing RAG API",
    description="Q&A over manufacturing SOPs, safety, maintenance, and compliance documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}
