import os

import databases
from sqlalchemy import create_engine, MetaData


metadata = MetaData()

if os.getenv("DB_CONN_STR"):
    DATABASE_URL = os.getenv("DB_CONN_STR")
    db = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL)
else:
    DATABASE_URL = "sqlite:///./sql_app.db"
    db = databases.Database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)
