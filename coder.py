import os
import sys
import argparse
import subprocess
import time
from github import Github, Auth
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("OPENROUTER_API_KEY")

def setup_git_user():
    subprocess.run(["git", "config", "--global", "user.name", "AI Agent"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "agent@ai.com"], check=True)

def parse_llm_response(response_text):
    import re
    files = []
    pattern = re.compile(r'<FILE path="(.*?)">\n(.*?)\n</FILE>', re.DOTALL)
    matches = pattern.findall(response_text)
    for path, content in matches:
        files.append({"path": path, "content": content})
    return files

def get_pr_files(pr):
    """Получает содержимое файлов из PR для контекста"""
    files_context = ""
    for file in pr.get_files():
        files_context += f"--- FILE: {file.filename} ---\n"
        # В реальном проекте лучше скачивать файл, но для текстовых файлов так ок
        # Или использовать requests.get(file.raw_url)
        # Здесь мы просто обозначим, что файл есть. Агент должен переписать его целиком.
    return files_context

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", help="Issue number (for new task)")
    parser.add_argument("--pr", help="PR number (for fixing bugs)")
    parser.add_argument("--fix", action="store_true", help="Enable fix mode")
    args = parser.parse_args()

    if not API_KEY:
        print("Error: OPENROUTER_API_KEY is missing")
        sys.exit(1)

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    
    setup_git_user()

    # Инициализация LLM
    llm = ChatOpenAI(
        model="tngtech/deepseek-r1t2-chimera:free",
        openai_api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.1
    )

    # --- РЕЖИМ 1: СОЗДАНИЕ НОВОГО КОДА (из Issue) ---
    if args.issue and not args.fix:
        print(f"--- Processing Issue #{args.issue} ---")
        issue = repo.get_issue(number=int(args.issue))
        
        system_prompt = """Ты - Python-разработчик. Напиши код для задачи.
        ФОРМАТ ОТВЕТА:
        <FILE path="имя_файла.py">
        код
        </FILE>
        """
        user_prompt = f"ЗАДАЧА: {issue.title}\nОПИСАНИЕ: {issue.body}"
        
        branch_name = f"feature/issue-{args.issue}"
        base_branch = "main"

    # --- РЕЖИМ 2: ИСПРАВЛЕНИЕ ОШИБОК (из PR + комментарии) ---
    elif args.pr and args.fix:
        print(f"--- Fixing PR #{args.pr} ---")
        pr = repo.get_pull(int(args.pr))
        
        # Получаем последние комментарии (критику ревьюера)
        comments = list(pr.get_issue_comments())
        last_comment = comments[-1].body if comments else "No comments"
        
        print(f"Last feedback: {last_comment[:100]}...")
        
        system_prompt = """Ты - разработчик, исправляющий ошибки.
        Тебе дан код и критика Ревьюера.
        Твоя задача: переписать код так, чтобы исправить замечания.
        Верни ПОЛНОСТЬЮ исправленный файл в тегах <FILE>."""
        
        # Получаем текущий код из ветки (через git checkout)
        branch_name = pr.head.ref
        base_branch = pr.base.ref # обычно main
        
        # Переключаемся на ветку PR
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "checkout", branch_name], check=True)
        
        # Читаем файлы, которые есть в ветке сейчас
        current_files_content = ""
        for root, _, files in os.walk("."):
            if ".git" in root: continue
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), "r") as f:
                        current_files_content += f"\n--- {file} ---\n{f.read()}\n"

        user_prompt = f"""
        ТЕКУЩИЙ КОД:
        {current_files_content}
        
        КРИТИКА РЕВЬЮЕРА:
        {last_comment}
        
        Исправь код согласно критике.
        """
    else:
        print("Use --issue <num> OR --pr <num> --fix")
        sys.exit(1)

    # --- ОБЩАЯ ЧАСТЬ: ГЕНЕРАЦИЯ И КОММИТ ---
    print("Asking AI...")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    
    try:
        response = llm.invoke(messages)
    except Exception as e:
        print(f"LLM Error: {e}")
        sys.exit(1)

    generated_files = parse_llm_response(response.content)
    
    if not generated_files:
        print("No code generated.")
        sys.exit(1)

    # Git операции
    # Если это новый issue, создаем ветку. Если fix - мы уже в ней.
    if args.issue and not args.fix:
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        except:
            subprocess.run(["git", "checkout", branch_name], check=True)

    for file_data in generated_files:
        path = file_data["path"]
        content = file_data["content"]
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {path}")

    # Commit & Push
    try:
        subprocess.run(["git", "add", "."], check=True)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        if status.stdout.strip():
            msg = f"Fix: {issue.title}" if args.issue else "Fixes based on review"
            subprocess.run(["git", "commit", "-m", msg], check=True)
            subprocess.run(["git", "push", "origin", branch_name], check=True)
            
            # Если создавали с нуля - делаем PR
            if args.issue and not args.fix:
                try:
                    pr = repo.create_pull(
                        title=f"Resolve: {issue.title}",
                        body=f"Generated by AI.\nFixes #{args.issue}",
                        head=branch_name,
                        base="main"
                    )
                    print(f"PR Created: {pr.html_url}")
                except:
                    print("PR already exists.")
        else:
            print("No changes to commit.")
            
    except Exception as e:
        print(f"Git error: {e}")

if __name__ == "__main__":
    main()