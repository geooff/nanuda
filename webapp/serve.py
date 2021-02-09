from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from webapp.emoji_classifier import EmojiClassifier

# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = EmojiClassifier()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    os.environ.get("FE_URL")
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Text(BaseModel):
    body: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/")
async def classify_text(text: Text, max_n=5):
    # Get List of predictions from fastai
    results = model.classify_emoji(text.body)
    top_results = results[: int(max_n)]
    return sorted(top_results, key=lambda x: x["confidence"], reverse=True)


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    return "Emoji classifier is all ready to go!"