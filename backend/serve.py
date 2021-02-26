from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from utils import models, crud, database, schema
import emoji_classifier


# Create all model metadata in DB
models.Base.metadata.create_all(bind=database.engine)

# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = emoji_classifier.EmojiClassifier()

# Generate DB dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Do CORS stuff
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "localhost:3000",
        "app.nanuda.ca",
        "http://app.nanuda.ca",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/classify_text")
async def classify_text(
    text: schema.ClassifyBase, request: Request, db: Session = Depends(get_db)
):
    THRESH = 0.02

    # Get List of predictions from fastai
    results = model.classify_emoji(text.tweet)

    # Sort results by condifence and limit by THRESH
    sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    truncated_results = [elem for elem in sorted_results if elem["confidence"] > THRESH]

    # If results calculate and append unaccounted condifences
    if len(truncated_results) > 0:
        truncated_confidence = 1 - sum(
            [elem["confidence"] for elem in truncated_results]
        )
        truncated_results.append({"emoji": "Other", "confidence": truncated_confidence})

    # Log prediction to Database
    crud.create_prediction(
        db,
        schema.ClassifyCreate(
            user=request.client.host,
            model=model.model_origin,
            raw_result=results,
            result=truncated_results,
            **text.dict(),
        ),
    )
    return truncated_results


@app.post("/emojify")
async def emojify_text(text: schema.Emojify):
    # Get List of predictions from fastai
    results = model.classify_emoji(text.tweet)
    sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    emoji = "".join([x["emoji"] for x in sorted_results[: int(text.emoji_returned)]])
    return " ".join([text.tweet, emoji])


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    return f"Emoji classifier from path {model.model_origin} is ready to go!"
