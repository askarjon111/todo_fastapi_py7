import os

from fastapi.staticfiles import StaticFiles
from main import app


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")
