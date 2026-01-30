# git_tools.py
import os
import subprocess
from github import Github, Auth
from config import Config

def setup_git():
    subprocess.run(["git", "config", "--global", "user.name", Config.GIT_USER], check=False)
    subprocess.run(["git", "config", "--global", "user.email", Config.GIT_EMAIL], check=False)

def get_repo():
    auth = Auth.Token(Config.GITHUB_TOKEN)
    g = Github(auth=auth)
    return g.get_repo(Config.REPO_NAME)

def checkout_branch(branch_name, create_new=False):
    try:
        if create_new:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        else:
            subprocess.run(["git", "fetch", "origin"], check=False)
            subprocess.run(["git", "checkout", branch_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git checkout error: {e}")

def commit_and_push(branch_name, message):
    subprocess.run(["git", "add", "."], check=True)
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push", "origin", branch_name], check=True)
        return True
    return False

def get_project_files(ext=".py"):
    """Читает все файлы проекта для контекста"""
    content = ""
    for root, _, files in os.walk("."):
        if ".git" in root: continue
        for file in files:
            if file.endswith(ext):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content += f"\n--- {path} ---\n{f.read()}\n"
    return content

def get_pr_diff(pr_number):
    """Получает изменения в файлах из PR"""
    repo = get_repo()
    pr = repo.get_pull(pr_number)
    
    diff_text = f"PR #{pr_number}: {pr.title}\n\n"
    
    # Получаем список измененных файлов
    for file in pr.get_files():
        # Пропускаем удаленные файлы или конфиги
        if file.status == "removed" or not file.filename.endswith(".py"):
            continue
            
        diff_text += f"FILE: {file.filename} (Status: {file.status})\n"
        if file.patch:
            diff_text += f"PATCH:\n{file.patch}\n"
        else:
            diff_text += "Content: (Binary or too large)\n"
        diff_text += "-" * 30 + "\n"
        
    return diff_text

def post_pr_comment(pr_number, body):
    """Публикует комментарий в PR"""
    repo = get_repo()
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(body)
    return pr.html_url

def get_ci_status(pr_number):
    """(Опционально) Получает статус последних проверок"""
    repo = get_repo()
    pr = repo.get_pull(pr_number)
    # Берем последний коммит
    last_commit = pr.get_commits().reversed[0]
    statuses = last_commit.get_statuses()
    
    if statuses.totalCount > 0:
        return f"Latest CI Status: {statuses[0].state} - {statuses[0].description}"
    return "No CI status found."