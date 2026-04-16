from fastapi import FastAPI

from classifier_agent.controllers import router
from classifier_agent.database import init_db

app = FastAPI(title="FinGuard Classifier Agent")

init_db()

app.include_router(router)


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to the FinGuard Classifier Agent!"}
