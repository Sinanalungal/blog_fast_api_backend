from fastapi import FastAPI
from app import models
from app.db.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def checking():
    return {"message": "API is up and running!"}