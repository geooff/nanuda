from typing import List
import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Model for classifying text WITH control of return
class Emojify(BaseModel):
    tweet: str
    emoji_returned: int


# Model for classifying text without control of return
class ClassifyBase(BaseModel):
    tweet: str


# Recursive model for single predictions of a larger output
class SinglePrediction(BaseModel):
    emoji: str
    confidence: float


# Model for classified text not commited to DB
class ClassifyCreate(ClassifyBase):
    user: str
    model: str
    result: List[SinglePrediction]


class Classify(ClassifyCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime.datetime

    class Config:
        orm_mode = True
