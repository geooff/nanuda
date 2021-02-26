from fastai.learner import load_learner
import boto3
import json
import os
from pathlib import Path

LOCAL_ENV_FILE = "webapp/S3_keys.json"

# Set S3 keys for local testing
if Path(LOCAL_ENV_FILE).is_file():
    with open(LOCAL_ENV_FILE) as f:
        creds = json.load(f)
        os.environ["SPACES_KEY"] = creds["SPACES_KEY"]
        os.environ["SPACES_SECRET"] = creds["SPACES_SECRET"]
        os.environ["MODEL_S3_PATH"] = creds["MODEL_S3_PATH"]
        os.environ["SPACE_NAME"] = creds["SPACE_NAME"]

# Init S3 Session
session = boto3.session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url='https://nyc3.digitaloceanspaces.com',
                        aws_access_key_id=os.getenv('SPACES_KEY'),
                        aws_secret_access_key=os.getenv('SPACES_SECRET'))


class EmojiClassifier:
    def __init__(self):
        self.MODEL_PATH = "model.pkl"
        self.model_origin = self.MODEL_PATH 
        if (MODEL_S3_PATH := os.environ.get("MODEL_S3_PATH")):
            self.MODEL_S3_PATH = MODEL_S3_PATH
            self.model_origin = self.MODEL_S3_PATH 
            print(f"Fetching model from: {self.MODEL_S3_PATH}")
            client.download_file(os.getenv('SPACE_NAME'),
                    self.MODEL_S3_PATH,
                    self.MODEL_PATH)

        print(f"Loading model: {self.MODEL_PATH}")
        self.learn = load_learner(self.MODEL_PATH)
        self.labels = self.learn.dls.vocab[1]


    def classify_emoji(self, text: str):
        """Classify tweet like string to emoji representation using model

        Args:
            text (str): String of tweet 

        Returns:
            [list{dict}]: List of dictionaries containing emoji prediction confidences
        """
        confidences = self.learn.predict(text)[2].tolist()
        # Wrap labels and confidences into dictionary
        return [{"emoji": l, "confidence": c} for l, c in zip(self.labels, confidences)]