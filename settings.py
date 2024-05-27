import os
from schemas import ErrorResponses

STATIC_PATH = os.path.join(os.getcwd(), "static")

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

DATABASE_URL_POSTGRES = "postgresql+asyncpg://admin:admin@db/my_db"

ERROR_RESPONSES = {404: {"model": ErrorResponses}, 422: {"model": ErrorResponses}}

API_KEY = {"test": 1, "test2": 2, "test3": 3}
