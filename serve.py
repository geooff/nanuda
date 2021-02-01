from fastapi import FastAPI
from pydantic import BaseModel

from fastai.learner import load_learner

from prettytable import PrettyTable
from typing import Optional
from pathlib import Path

from model_fetcher import download_file_from_google_drive

# Warm up
FILE_ID = "1tzQB9IzrlRdpS5nbHJ3OLkvALgYAXrVw"
MODEL_PATH = "model.pkl"
if not Path(MODEL_PATH).is_file():
    download_file_from_google_drive(FILE_ID, MODEL_PATH)

# Load Learner from model
learn = load_learner(MODEL_PATH)
labels = learn.dls.vocab[1]

app = FastAPI()


class Text(BaseModel):
    body: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/")
async def classify_text(text: Text, max_n=5):
    output_grid = PrettyTable(format=True)
    output_grid.field_names = ["Emoji", "Confidence"]
    # Get List of predictions from fastai
    confidences = learn.predict(text.body)[2].tolist()
    # Wrap labels and confidences into dictionary
    results = {l: c for l, c in zip(labels, confidences)}
    results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    top_results = results[:max_n]
    # TODO: Use this to display confidence in pred
    total_confidence = sum([x[1] for x in top_results])
    for row in top_results:
        output_grid.add_row(row)
    return output_grid.get_html_string()
