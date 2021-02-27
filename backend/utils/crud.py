from sqlalchemy import Table
import databases
from uuid import uuid4
from datetime import datetime
import json

from utils import schemas


async def create_prediction(
    db: databases, table: Table, classify: schemas.ClassifyCreate
):
    classify = classify.dict()
    json_result = json.dumps(classify.pop("result"))
    query = table.insert().values(
        id=uuid4(), created_at=datetime.now(), result=json_result, **classify
    )
    last_record_id = await db.execute(query)
    return last_record_id
