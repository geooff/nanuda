import os

from sqlalchemy import MetaData, Table, Column, String, DateTime, JSON, create_engine
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

import uuid
import databases


db_args = {"min_size": 5, "max_size": 20}

metadata = MetaData()


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


prediction_table = Table(
    "prediction",
    metadata,
    Column("id", GUID(), primary_key=True, default=uuid.uuid4),
    Column("created_at", DateTime, server_default=func.now(), index=True),
    Column("user", String, index=True),
    Column("model", String, index=True),
    Column("tweet", String(160), index=True),
    Column("result", JSON),
)


if os.getenv("DB_CONN_STR"):
    DATABASE_URL = os.getenv("DB_CONN_STR")
    db = databases.Database(DATABASE_URL, **db_args)
    engine = create_engine(DATABASE_URL)
else:
    DATABASE_URL = "sqlite:///./sql_app.db"
    db = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)
