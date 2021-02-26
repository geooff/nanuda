from sqlalchemy.orm import Session
import json

from utils import models, schemas

def create_prediction(db: Session, classify: schemas.ClassifyCreate):
    classify = classify.dict()
    json_raw_result = json.dumps(classify.pop("raw_result"))
    json_result = json.dumps(classify.pop("result"))
    db_prediction = models.Prediction(raw_result= json_raw_result, result= json_result, **classify)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

