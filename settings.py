import os
from schemas import ErrorResponses
from config import DB_NAME, DB_PASS, DB_USER

STATIC_PATH = os.path.join(os.getcwd(), "static")

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# DATABASE_URL_POSTGRES = "postgresql+asyncpg://admin:admin@db/my_db"
DATABASE_URL_POSTGRES = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@db/{DB_NAME}"

ERROR_RESPONSES = {404: {"model": ErrorResponses}, 422: {"model": ErrorResponses}}

API_KEY = {"test": 1, "test2": 2, "test3": 3}
