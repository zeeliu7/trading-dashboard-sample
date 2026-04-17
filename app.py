import os
import sqlite3
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from db import preprocess_data
from routes.db_routes import router as db_router, set_conn as db_set_conn
from routes.ai_routes import router as ai_router
from ai.tools import set_conn as ai_set_conn

DB_PATH = os.getenv('DB_PATH', 'db/transactions.db')
CSV_FILE = os.getenv('TRANSACTION_FILE_NAME', 'sample_transactions.csv')


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    preprocess_data(CSV_FILE, conn)
    db_set_conn(conn)
    ai_set_conn(conn)
    yield
    conn.close()


app = FastAPI(lifespan=lifespan)
app.include_router(db_router)
app.include_router(ai_router)
