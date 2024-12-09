import uvicorn
from fastapi import FastAPI
from src.api.health import health_router
from src.api.analyzer import analyzer_router
from src.api.task import task_router

app = FastAPI()
app.include_router(health_router)
app.include_router(analyzer_router)
app.include_router(task_router)

if __name__ == "__main__":
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)