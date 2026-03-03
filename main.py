from fastapi import FastAPI
from api.health import router as health_router

app = FastAPI(title = "Web-Putty Backend")

app.include_router(health_router)

@app.get("/")
def root():
    return{"message": "web_putty backend is running"}