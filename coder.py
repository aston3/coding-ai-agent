import os
import sys
import argparse
import subprocess
import time
from github import Github
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("GOOGLE_API_KEY")

def setup_git_user():
    """Настраиваем git user для коммитов"""
    subprocess.run(["git", "config", "--global", "user.name", "AI Agent"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "agent@ai.com"], check=True)

def get_file_structure():
    """Собираем структуру проекта"""
    files_list = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs: dirs.remove(".git")
        if ".github" in dirs: dirs.remove(".github")
        if "venv" in dirs: dirs.remove("venv") # Игнорируем venv
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        
        for file in files:
            if file.endswith((".py", ".md", ".txt", ".yml", ".yaml", ".json")):
                path = os.path.join(root, file)
                files_list.append(path)
    return "\n".join(files_list)

def parse_llm_response(response_text):
    """Парсим XML-теги <FILE>"""
    import re
    files = []
    pattern = re.compile(r'<FILE path="(.*?)">\n(.*?)\n</FILE>', re.DOTALL)
    matches = pattern.findall(response_text)
    for path, content in matches:
        files.append({"path": path, "content": content})
    return files

def generate_code_with_retry(llm, messages, max_retries=5):
    """Функция с защитой от Rate Limit (429)"""
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except Exception as e:
            error_str = str(e).lower()
            # Проверяем, связана ли ошибка с лимитами
            if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
                wait_time = 30 + (attempt * 10) # 30с, 40с, 50с...
                print(f"⚠️ Лимит запросов (429). Ждем {wait_time} сек... (Попытка {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # Если ошибка другая (например, нет ключа), падаем сразу
                raise e
    raise Exception("Не удалось получить ответ от нейросети после всех попыток.")

def main(issue_number):
    if not API_KEY:
        print("Error: GOOGLE_API_KEY is missing")
        sys.exit(1)

    print(f"--- Processing Issue #{issue_number} ---")
    
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    issue = repo.get_issue(number=int(issue_number))
    
    print(f"Task: {issue.title}")
    
    # Используем самую легкую модель для Free Tier
    # Если flash-latest падает, попробуйте gemini-1.5-flash-8b
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=API_KEY,
        temperature=0.1,
        max_retries=0 # Отключаем встроенные ретраи LangChain, используем свои
    )

    files_context = get_file_structure()
    
    system_prompt = """Ты - опытный Python-разработчик. 
    Твоя задача - написать код для решения Issue.
    
    ФОРМАТ ОТВЕТА (Строго соблюдай!):
    <FILE path="имя_файла.py">
    код файла целиком
    </FILE>
    
    Верни ВЕСЬ файл целиком, даже если меняешь одну строку.
    Не пиши маркдаун (```python), только теги <FILE>."""
    
    user_prompt = f"""
    ЗАДАЧА: {issue.title}
    ОПИСАНИЕ: {issue.body}
    
    ФАЙЛЫ В ПРОЕКТЕ:
    {files_context}
    """

    print("Asking Gemini...")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    # ВЫЗОВ С РЕТРАЯМИ
    response = generate_code_with_retry(llm, messages)
    
    generated_files = parse_llm_response(response.content)
    
    if not generated_files:
        print("No files generated. Raw response:")
        print(response.content)
        # Иногда модель пишет текст без тегов, можно попробовать добавить fallback, 
        # но пока просто выходим
        sys.exit(1)

    setup_git_user()
    branch_name = f"feature/issue-{issue_number}"
    
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "checkout", branch_name], check=True)

    for file_data in generated_files:
        path = file_data["path"]
        content = file_data["content"]
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {path}")

    # Git Push
    try:
        subprocess.run(["git", "add", "."], check=True)
        # Проверяем, есть ли что коммитить
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout.strip():
            subprocess.run(["git", "commit", "-m", f"Fix: {issue.title}"], check=True)
            subprocess.run(["git", "push", "origin", branch_name], check=True)
        else:
            print("No changes to commit.")
    except Exception as e:
        print(f"Git error: {e}")

    # PR Creation
    try:
        pr = repo.create_pull(
            title=f"Resolve: {issue.title}",
            body=f"Generated by AI Agent.\nFixes #{issue_number}",
            head=branch_name,
            base="main"
        )
        print(f"PR Created: {pr.html_url}")
    except Exception as e:
        print(f"PR creation failed (maybe exists?): {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True, help="Issue number")
    args = parser.parse_args()
    main(args.issue)