import os
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL,
                       connect_args={'check_same_thread': False},
                       echo=True)


Session = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass


def get_db():
    try:
        db_session = Session()
        yield db_session
    finally:
        db_session.close()
