from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.ext.declarative import declarative_base
from settings import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def get_async_session():
    async with async_session() as session:
        yield session
