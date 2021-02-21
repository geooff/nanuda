from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from emoji_classifier import EmojiClassifier

# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = EmojiClassifier()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "app.nanuda.ca",
    "http://app.nanuda.ca"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# DataClass for classifying text without control of return
class Classify(BaseModel):
    body: str

# DataClass for classifying text WITH control of return
class Text(BaseModel):
    body: str
    emoji_returned: int


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/classify_text")
async def classify_text(text: Classify):
    # Get List of predictions from fastai
    results = model.classify_emoji(text.body)
    sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    return sorted_results[:5]


@app.post("/emojify")
async def emojify_text(text: Text):
    # Get List of predictions from fastai
    results = model.classify_emoji(text.body)
    sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    emoji = "".join([x["emoji"] for x in sorted_results[: int(text.emoji_returned)]])
    return " ".join([text.body, emoji])


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    if hasattr(model, 'MODEL_S3_PATH'):
        # Model is served via S3 Path
        model_path = model.MODEL_S3_PATH 
    else:
        # Model comes from local
        model_path = model.MODEL_PATH
    return f"Emoji classifier from path {model_path} is ready to go!"