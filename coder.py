import argparse
import os
import re
import sys
from configs.config import Config
from configs.llm import invoke_llm, PROMPTS
from configs.git_tools import setup_git, get_repo, checkout_branch, commit_and_push, get_project_files

def parse_files(text):
    """
    Парсит ответ LLM на файлы.
    Исправленный REGEX: не захватывает переносы строк в имени файла.
    """
    # pattern: ищет <FILE path="имя"> ...контент... </FILE>
    # ([^"\n]+) - гарантирует, что имя файла не содержит кавычек и переносов
    pattern = re.compile(r'<FILE path="([^"\n]+)">\n(.*?)\n</FILE>', re.DOTALL)
    files = []
    for match in pattern.finditer(text):
        path = match.group(1)
        content = match.group(2)
        files.append({"path": path, "content": content})
    return files

def check_iteration_limit(pr_number):
    """
    Защита от бесконечных циклов.
    Если бот уже 5 раз пытался исправить код, останавливаемся.
    """
    try:
        repo = get_repo()
        pr = repo.get_pull(int(pr_number))
        comments = list(pr.get_issue_comments())
        
        bot_reviews = 0
        for comment in comments:
            # Считаем комментарии, где есть маркеры нашего ревью
            if "⚠️ Найдены замечания" in comment.body or "CHANGES TO REVIEW" in comment.body:
                bot_reviews += 1
        
        print(f"🔄 Текущая итерация исправлений: {bot_reviews}")
        
        if bot_reviews >= 5:
            msg = "⛔ Превышен лимит итераций (5). Агент останавливает работу, требуется вмешательство человека."
            pr.create_issue_comment(msg)
            print("❌ Limit reached. Exiting.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Warning: Could not check iteration limit: {e}")

def run_coder():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", help="Issue number")
    parser.add_argument("--pr", help="PR number (fix mode)")
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()

    Config.validate()
    setup_git()
    repo = get_repo()

    # Сценарий 1: Новая фича (Issue)
    if args.issue and not args.fix:
        issue = repo.get_issue(int(args.issue))
        print(f"🚀 Задача: {issue.title}")
        
        branch_name = f"feature/issue-{args.issue}"
        checkout_branch(branch_name, create_new=True)

        system_prompt = PROMPTS["coder_new"]
        user_prompt = f"TITLE: {issue.title}\nBODY: {issue.body}"

    # Сценарий 2: Исправление (PR + Review)
    elif args.pr and args.fix:
        print(f"🔧 Исправление PR #{args.pr}")
        
        # 1. Проверяем лимит попыток
        check_iteration_limit(args.pr)
        
        pr = repo.get_pull(int(args.pr))
        branch_name = pr.head.ref
        checkout_branch(branch_name) 
        
        comments = list(pr.get_issue_comments())
        last_feedback = comments[-1].body if comments else "Fix logic errors."
        
        current_code = get_project_files()
        
        system_prompt = PROMPTS["coder_fix"]
        user_prompt = f"CODE:\n{current_code}\n\nFEEDBACK:\n{last_feedback}"

    # Вызов модели
    print("🤖 Генерация кода...")
    response = invoke_llm(system_prompt, user_prompt)
    files = parse_files(response)

    if not files:
        print("⚠️ Код не сгенерирован (или неверный формат ответа)")
        return

    # Запись файлов
    for f in files:
        path = f["path"]
        
        # Защита: не даем агенту ломать свои же скрипты во время работы
        if path in ["coder.py", "reviewer.py", "configs/llm.py", "configs/git_tools.py"]:
            print(f"🛡️ Пропуск системного файла: {path}")
            continue

        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as file:
                file.write(f["content"])
            print(f"📝 Записан: {path}")
        except OSError as e:
            print(f"❌ Ошибка записи {path}: {e}")

    # Пуш изменений
    msg = f"AI Update: {issue.title if args.issue else 'Fixes based on review'}"
    if commit_and_push(branch_name, msg):
        print("✅ Изменения отправлены")
        
        # Создание PR только если это новая задача
        if args.issue and not args.fix:
            try:
                pr = repo.create_pull(
                    title=f"Resolve: {issue.title}",
                    body="Generated by AI Code Agent",
                    head=branch_name,
                    base="main"
                )
                print(f"🔗 PR создан: {pr.html_url}")
            except Exception as e:
                print(f"PR уже существует или ошибка: {e}")

if __name__ == "__main__":
    run_coder()