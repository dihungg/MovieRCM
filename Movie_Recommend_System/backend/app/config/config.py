import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
