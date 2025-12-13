from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.get("/")
def root():
    return {"message": "UpFlow API is running."}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
    }
