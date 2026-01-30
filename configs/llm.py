# llm.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config import Config

# Промпты вынесены отдельно
PROMPTS = {
    "coder_new": """Ты - Python-разработчик. Напиши код для задачи.
ФОРМАТ ОТВЕТА:
<FILE path="имя_файла.py">
код
</FILE>""",
    
    "coder_fix": """Ты - разработчик, исправляющий ошибки.
Тебе дан код и критика Ревьюера. Перепиши код, исправляя замечания.
Верни ПОЛНОСТЬЮ исправленный файл в тегах <FILE>.""",

    "reviewer": """Ты - строгий Code Reviewer. Проверь код на ошибки, уязвимости и стиль (PEP8).
1. Если код хороший, напиши ТОЛЬКО: "LGTM".
2. Если есть ошибки, напиши список с рекомендациями."""
}

def get_llm(temp=None):
    """Возвращает настроенный инстанс LLM"""
    return ChatOpenAI(
        model=Config.MODEL_NAME,
        openai_api_key=Config.API_KEY,
        base_url=Config.BASE_URL,
        temperature=temp if temp is not None else Config.TEMPERATURE
    )

def invoke_llm(system_prompt: str, user_content: str):
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    try:
        return llm.invoke(messages).content
    except Exception as e:
        print(f"LLM Error: {e}")
        raise e