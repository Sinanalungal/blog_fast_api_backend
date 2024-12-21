from fastapi import FastAPI
from app import models
from app.db.database import engine
from app.api.v1 import auth,user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:5173"],  # Your frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/auth', tags=["Authentication Related Routes"])
app.include_router(user.router, prefix='/user_routes', tags=["User Related Routes"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
