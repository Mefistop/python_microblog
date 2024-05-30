from contextlib import asynccontextmanager

import uvicorn  # type: ignore
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from db.database import Base, async_session, engine
from app.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_session.close()  # type: ignore
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "result": False,
            "error_type": str(exc.__class__.__name__),
            "error_message": str(exc.errors()[0]["msg"]),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": str(exc.__class__.__name__),
            "error_message": str(exc.detail),
        },
    )


app.include_router(router)
app.mount("/", StaticFiles(directory="static", html=True))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
