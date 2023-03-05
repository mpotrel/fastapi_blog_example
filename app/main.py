import os
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings


models.Base.metadata.create_all(
    bind=engine
)  # This will create the tables that don't exist from the models

# TODO Make typing better for the return types
app = FastAPI()

# Allow origins from domains
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pass origins if you want, ["*"] if you want to allow everyone
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


# This could be an async function
@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Updated hello world!"}
