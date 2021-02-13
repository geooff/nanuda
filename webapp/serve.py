from fastapi import FastAPI
from pydantic import BaseModel

from webapp.emoji_classifier import EmojiClassifier

# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = EmojiClassifier()


class Text(BaseModel):
    body: str
    emoji_returned: int


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/classify_text")
async def classify_text(text: Text):
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
        model_path = model.MODEL_S3_PATH 
    else:
        model_path = model.MODEL_PATH
    return f"Emoji classifier from path {model_path} is ready to go!"