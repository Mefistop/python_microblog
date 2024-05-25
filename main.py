from routers import router
from contextlib import asynccontextmanager
from db.database import Base, async_session, engine
from fastapi import FastAPI
import uvicorn
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.sql import text
from fastapi.requests import Request


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
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"result": False, "error_type": str(exc.__class__.__name__), "error_message": str(exc.errors()[0]["msg"])})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": False, "error_type": str(exc.__class__.__name__), "error_message": str(exc.detail)})


app.include_router(router)
app.mount("/", StaticFiles(directory="static", html=True))


if __name__ == '__main__':

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)