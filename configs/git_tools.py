import os
from github import Github

# Импортируем настройки из config.py
# Убедитесь, что в config.py определены GITHUB_TOKEN и REPO_NAME
try:
    from configs.config import GITHUB_TOKEN, REPO_NAME
except ImportError:
    # Заглушка для локальных тестов без config.py
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("GITHUB_REPOSITORY")

# Списки для фильтрации ненужного контента
EXCLUDE_DIRS = {
    '.git', '.github', '.idea', '.vscode', '__pycache__', 
    'venv', 'env', 'node_modules', 'dist', 'build', 'coverage'
}

EXCLUDE_EXTENSIONS = {
    # Изображения и медиа
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.mp4', '.mp3',
    # Бинарные и системные
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin',
    # Архивы и документы
    '.zip', '.tar', '.gz', '.pdf', '.docx', '.xlsx',
    # Технические файлы
    '.lock', '.ds_store'
}

MAX_FILE_SIZE = 30000  # Максимальный размер файла для контекста (символов)

def get_repo():
    """Авторизуется и возвращает объект репозитория GitHub."""
    if not GITHUB_TOKEN or not REPO_NAME:
        raise ValueError("Не настроены GITHUB_TOKEN или REPO_NAME в configs/config.py")
    
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def is_text_file(filename):
    """Проверяет расширение файла на принадлежность к бинарным."""
    _, ext = os.path.splitext(filename)
    return ext.lower() not in EXCLUDE_EXTENSIONS

def should_ignore_dir(dirname):
    """Проверяет, нужно ли игнорировать папку."""
    return dirname in EXCLUDE_DIRS

def get_project_files():
    """
    Сканирует текущую директорию и возвращает содержимое всех текстовых файлов проекта.
    Используется для формирования контекста для LLM.
    """
    project_content = ""
    
    for root, dirs, files in os.walk("."):
        # Модифицируем dirs in-place, чтобы os.walk не заходил в игнорируемые папки
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Пропускаем бинарные расширения
            if not is_text_file(file):
                continue
                
            # Относительный путь для контекста LLM (clean path)
            rel_path = os.path.relpath(file_path, ".")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Если файл пустой - пропускаем
                    if not content.strip():
                        continue
                        
                    # Если файл слишком большой - обрезаем
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n... [TRUNCATED DUE TO SIZE] ..."
                    
                    project_content += f"\n<FILE path=\"{rel_path}\">\n{content}\n</FILE>\n"
                    
            except UnicodeDecodeError:
                # Если файл не читается в utf-8, считаем его бинарным и пропускаем
                print(f"Skipping binary file: {rel_path}")
            except Exception as e:
                print(f"Error reading {rel_path}: {e}")
                
    return project_content

def get_pr_diff(pr_number):
    """
    Получает diff (изменения) из Pull Request.
    Используется Reviewer Agent'ом.
    """
    repo = get_repo()
    pr = repo.get_pull(int(pr_number))
    
    diff_content = []
    
    # Получаем список измененных файлов
    for file in pr.get_files():
        # Игнорируем удаленные файлы
        if file.status == "removed":
            diff_content.append(f"File: {file.filename}\nStatus: REMOVED")
            continue
            
        # Игнорируем бинарные файлы в диффе
        if not is_text_file(file.filename):
            diff_content.append(f"File: {file.filename}\nStatus: BINARY FILE CHANGED (Diff hidden)")
            continue
            
        # Добавляем патч (сами изменения)
        # file.patch может быть None, если файл слишком большой или бинарный
        if file.patch:
            diff_content.append(f"File: {file.filename}\nDiff:\n{file.patch}")
        else:
            diff_content.append(f"File: {file.filename}\nDiff: [No patch available]")
            
    return "\n\n".join(diff_content)