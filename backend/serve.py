from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from utils import models, crud, database, schemas
from emoji_classifier import EmojiClassifier


# Bind webserver early to avoid timeout issue
app = FastAPI()

# Init our classifier
model = EmojiClassifier()

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


@app.on_event("startup")
async def startup():
    await database.db.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.db.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/classify_text")
async def classify_text(text: schemas.ClassifyBase, request: Request):
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
    await crud.create_prediction(
        database.db,
        models.prediction_table,
        schemas.ClassifyCreate(
            user=request.client.host,
            model=model.model_origin,
            result=truncated_results,
            **text.dict(),
        ),
    )
    return truncated_results


@app.post("/emojify")
async def emojify_text(text: schemas.Emojify):
    # Get List of predictions from fastai
    results = model.classify_emoji(text.tweet)
    sorted_results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    emoji = "".join([x["emoji"] for x in sorted_results[: int(text.emoji_returned)]])
    return " ".join([text.tweet, emoji])


@app.get("/healthcheck", status_code=200)
async def healthcheck():
    return f"Emoji classifier from path {model.model_origin} is ready to go!"
