import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "books")

client = MongoClient(MONGO_URL)


def get_db():
    return client[MONGO_DB_NAME]
