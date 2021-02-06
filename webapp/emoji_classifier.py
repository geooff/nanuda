from fastai.learner import load_learner
from webapp.model_fetcher import download_file_from_google_drive
import os
from pathlib import Path


class EmojiClassifier:
    def __init__(self):
        self.MODEL_PATH = "model.pkl"
        if not Path(self.MODEL_PATH).is_file():
            self.MODEL_STORAGE_ID = os.environ.get("MODEL_STORAGE_ID")
            if self.MODEL_STORAGE_ID:
                print(f"Fetching model of ID: {self.MODEL_STORAGE_ID}")
                download_file_from_google_drive(self.MODEL_STORAGE_ID, self.MODEL_PATH)
            else:
                raise KeyError("Error - MODEL_STORAGE_ID not set. Check Heroku config")

        print(f"Loading model {self.MODEL_PATH}")
        self.learn = load_learner(self.MODEL_PATH)
        self.labels = self.learn.dls.vocab[1]

    def classify_emoji(self, text: str):
        confidences = self.learn.predict(text)[2].tolist()
        # Wrap labels and confidences into dictionary
        return [{"emoji": l, "confidence": c} for l, c in zip(self.labels, confidences)]