from fastapi import FastAPI
from pydantic import BaseModel

from typing import Optional
from prettytable import PrettyTable

from webapp.emoji_classifier import EmojiClassifier

# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = EmojiClassifier()


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
    # TODO: Use this to display confidence in pred
    total_confidence = sum([x[1] for x in top_results])
    return top_results


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    return "Emoji classifier is all ready to go!"