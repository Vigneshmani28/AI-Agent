import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "TaskPilot - Agentic AI Task Manager"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL: str = "llama-3.1-8b-instant"


settings = Settings()
