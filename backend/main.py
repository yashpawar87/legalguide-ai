from fastapi import FastAPI
import firebase_admin
from firebase_admin import credentials
from backend.config import settings
from backend.api.v1.documents import (
    router as document_router
)
from backend.api.v1.analysis import (
    router as analysis_router
)
from backend.api.v1.chats import (
    router as chat_router
)
from backend.db.session import engine
from backend.db.base import Base

Base.metadata.create_all(bind=engine)

# Initialize Firebase Admin
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Warning: Failed to initialize Firebase: {e}")

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "frontend": settings.FRONTEND_URL
        }

app.include_router(
    document_router, 
    prefix="/api/v1/documents"
)

app.include_router(
    analysis_router,
    prefix="/api/v1/analysis"
)

app.include_router(
    chat_router,
    prefix="/api/v1/chats"
)

