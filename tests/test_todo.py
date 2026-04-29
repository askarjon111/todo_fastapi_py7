import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL")


test_engine = create_async_engine(DATABASE_URL,
                       connect_args={'check_same_thread': False},
                       echo=True)

TestSession = async_sessionmaker(bind=test_engine, autoflush=False)

async def override_get_db():
    async with TestSession() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())


test_client = TestClient(app)


def test_create_user():
    response = test_client.post("/api/users/", json={"username": "testuser3",
                                                     "password": "testpassword",
                                                     "first_name": "Test",
                                                     "last_name": "User"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser3"


def test_create_todo():
    token = test_client.post("api/users/login/",
                             data={"username": "testuser3","password": "testpassword"})\
                                 .json()["access_token"]
    response = test_client.post("api/todo/",
                                headers={"Authorization": f"Bearer {token}"},
                                json={"name": "Test Todo","description": "This is a test todo"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Todo"
    assert data["description"] == "This is a test todo"

