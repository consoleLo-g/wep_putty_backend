from fastapi import FastAPI
from api.health import router as health_router
from api.terminal import router as terminal_router
from core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router)
app.include_router(terminal_router)


@app.get("/")
def root():
    return {"message": "Web-Putty Backend Running"}