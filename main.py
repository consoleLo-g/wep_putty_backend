from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings

from api.health import router as health_router
from api.auth import router as auth_router
from api.terminal import router as terminal_router
from api.sessions import router as sessions_router


app = FastAPI(
    title=settings.APP_NAME
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(terminal_router)
app.include_router(sessions_router)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "running"
    }