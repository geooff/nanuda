import os

import databases
from sqlalchemy import create_engine, MetaData


metadata = MetaData()

db_args = {"ssl": True, "min_size": 5, "max_size": 20}

if os.getenv("DB_CONN_STR"):
    DATABASE_URL = os.getenv("DB_CONN_STR")
    db = databases.Database(DATABASE_URL, **db_args)
    engine = create_engine(DATABASE_URL)
else:
    DATABASE_URL = "sqlite:///./sql_app.db"
    db = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)
