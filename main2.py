from routers import router
import datetime
import os.path
from contextlib import asynccontextmanager
from db.models import User, Publication, Followers, Like, Attachments
from db.database import Base, async_session, engine
from fastapi import FastAPI, Depends, Body, Header, UploadFile, File, Path
import uvicorn
from sqlalchemy.future import select
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.sql import text
from settings import STATIC_PATH
import aiofiles
from schemas import UserAddIn, UserAddOut, TweetAddIn, TweetAddOut, MediasAddOut, OutputSchema, GetAllTweetsOut, UserProfileInfoOut
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from settings import ERROR_RESPONSES, API_KEY


async def get_async_session():
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(
            text("PRAGMA foreign_keys = ON;"),
            execution_options={"isolation_level": "AUTONOMOUS"}
        )
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_session.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"result": False, "error_type": str(exc.__class__.__name__), "error_message": str(exc.errors()[0]["msg"])})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": False, "error_type": str(exc.__class__.__name__), "error_message": str(exc.detail)})


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("main2:app", host="127.0.0.1", port=8000, reload=True)