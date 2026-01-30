# llm.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from configs.config import Config

# Промпты вынесены отдельно
PROMPTS = {
    "coder_new": """You are an expert Senior Software Engineer capable of writing code in any programming language.
Your task is to solve the User's Issue based on the provided project context.

1. ANALYZE the project structure and existing file extensions to determine the technology stack (e.g., Python, JavaScript, Go, C++).
2. ADAPT your coding style, naming conventions, and syntax to match the existing project.
3. IMPLEMENT the solution.

IMPORTANT: Return the full content of the created or modified files wrapped in XML-like tags:
<FILE path="path/to/file.ext">
code content here
</FILE>
""",

    "coder_fix": """You are a Code Fixer Agent.
Your goal is to fix errors reported by the Reviewer or Linter.
Analyze the provided code and the error report.
Return the FULLY CORRECTED file content in <FILE path="..."> tags.
Maintain the original language and style of the file.""",

    "reviewer": """You are a strict Code Reviewer & QA Engineer.
Analyze the Pull Request changes for logic errors, security vulnerabilities, and code style violations.
Do not assume a specific language; adapt your review based on the file extension (.py, .js, .go, etc.).

Output format:
- If the code is good and meets requirements: Write ONLY "LGTM" (Looks Good To Me).
- If there are issues: Provide a numbered list of critical issues and suggestions using markdown.
"""
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