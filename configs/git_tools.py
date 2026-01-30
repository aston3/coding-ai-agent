import os
import subprocess
from github import Github

# Импортируем настройки
try:
    from configs.config import Config
except ImportError:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPOSITORY")
    GIT_USER = "AI Agent"
    GIT_EMAIL = "agent@ai.com"
else:
    GITHUB_TOKEN = Config.GITHUB_TOKEN
    REPO_NAME = Config.REPO_NAME
    GIT_USER = Config.GIT_USER
    GIT_EMAIL = Config.GIT_EMAIL

# --- CONSTANTS ---
EXCLUDE_DIRS = {
    '.git', '.github', '.idea', '.vscode', '__pycache__', 
    'venv', 'env', 'node_modules', 'dist', 'build', 'coverage',
    '.pytest_cache', 'mypy_cache'
}

EXCLUDE_EXTENSIONS = {
    # Images & Media
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.mp4', '.mp3',
    # Binary & System
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin',
    # Archives & Docs
    '.zip', '.tar', '.gz', '.pdf', '.docx', '.xlsx',
    # Tech
    '.lock', '.ds_store'
}

MAX_FILE_SIZE = 30000 

# --- GIT OPERATIONS (Restored) ---

def setup_git():
    """Настраивает user.name и email для коммитов."""
    try:
        subprocess.run(["git", "config", "--global", "user.name", GIT_USER], check=False)
        subprocess.run(["git", "config", "--global", "user.email", GIT_EMAIL], check=False)
        # Добавляем safe.directory для GitHub Actions
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", "*"], check=False)
    except Exception as e:
        print(f"Git setup warning: {e}")

def checkout_branch(branch_name, create_new=False):
    """Переключает или создает ветку."""
    try:
        # Сначала фечим всё
        subprocess.run(["git", "fetch", "origin"], check=False)
        
        if create_new:
            # Создаем новую ветку от текущей (обычно main)
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            print(f"Created and switched to new branch: {branch_name}")
        else:
            # Переключаемся на существующую
            subprocess.run(["git", "checkout", branch_name], check=True)
            print(f"Switched to branch: {branch_name}")
            
    except subprocess.CalledProcessError as e:
        print(f"Git checkout error: {e}")
        # Если не получилось создать, возможно она уже есть, пробуем просто checkout
        if create_new:
            try:
                subprocess.run(["git", "checkout", branch_name], check=True)
                print(f"Switched to existing branch: {branch_name}")
            except:
                pass

def commit_and_push(branch_name, message):
    """Добавляет изменения, коммитит и пушит."""
    try:
        # Добавляем все изменения (включая новые файлы)
        subprocess.run(["git", "add", "."], check=True)
        
        # Проверяем статус
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        
        if not status.stdout.strip():
            print("No changes to commit.")
            return False
            
        # Коммит
        subprocess.run(["git", "commit", "-m", message], check=True)
        
        # Пуш
        # Используем токен для авторизации при пуше, если origin настроен через https
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git commit/push error: {e}")
        return False

# --- FILE & REPO OPERATIONS ---

def get_repo():
    """Авторизуется и возвращает объект репозитория GitHub."""
    if not GITHUB_TOKEN or not REPO_NAME:
        # Пытаемся взять из env напрямую, если конфиг не прогрузился
        token = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")
        if not token or not repo:
             raise ValueError("Не настроены GITHUB_TOKEN или REPO_NAME")
        g = Github(token)
        return g.get_repo(repo)
    
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def is_text_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() not in EXCLUDE_EXTENSIONS

def should_ignore_dir(dirname):
    return dirname in EXCLUDE_DIRS

def get_project_files():
    """Сканирует проект и возвращает содержимое файлов."""
    project_content = ""
    
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not is_text_file(file):
                continue
                
            rel_path = os.path.relpath(file_path, ".")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content.strip(): continue
                    
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n... [TRUNCATED]"
                    
                    project_content += f"\n<FILE path=\"{rel_path}\">\n{content}\n</FILE>\n"
            except:
                continue
                
    return project_content

def get_pr_diff(pr_number):
    """Получает diff PR."""
    repo = get_repo()
    pr = repo.get_pull(int(pr_number))
    diff_content = []
    
    for file in pr.get_files():
        if file.status == "removed":
            diff_content.append(f"File: {file.filename}\nStatus: REMOVED")
            continue
        if not is_text_file(file.filename):
            diff_content.append(f"File: {file.filename}\nStatus: BINARY CHANGED")
            continue
            
        if file.patch:
            diff_content.append(f"File: {file.filename}\nDiff:\n{file.patch}")
            
    return "\n\n".join(diff_content)

def post_pr_comment(pr_number, body):
    """Публикует комментарий в PR (используется reviewer.py)."""
    repo = get_repo()
    pr = repo.get_pull(pr_number)
    comment = pr.create_issue_comment(body)
    return comment.html_url

def get_ci_status(pr_number):
    """Получает статус CI (используется reviewer.py)."""
    try:
        repo = get_repo()
        pr = repo.get_pull(pr_number)
        last_commit = pr.get_commits().reversed[0]
        statuses = last_commit.get_statuses()
        if statuses.totalCount > 0:
            return f"Latest CI Status: {statuses[0].state} - {statuses[0].description}"
        return "No CI status found."
    except:
        return "Could not fetch CI status."