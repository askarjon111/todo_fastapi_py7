import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(DATABASE_URL,
                             connect_args={'check_same_thread': False},
                             echo=True)


Session = async_sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with Session() as session:
        yield session
