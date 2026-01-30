# config.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub credentials
    GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPOSITORY")
    # Если запускаем локально для тестов, можно раскомментировать и вписать вручную:
    # if not REPO_NAME:
    #     REPO_NAME = "your-username/your-repo"
    
    # LLM Settings
    API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    # Модель вынесена в конфиг, чтобы легко менять при необходимости
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
    TEMPERATURE = 0.1

    # Git User (для коммитов в CI)
    GIT_USER = "AI Agent"
    GIT_EMAIL = "agent@ai.com"

    @staticmethod
    def validate():
        if not Config.API_KEY:
            print("Error: LLM_API_KEY is missing")
            sys.exit(1)
        if not Config.GITHUB_TOKEN:
            print("Error: GITHUB_TOKEN is missing")
            sys.exit(1)