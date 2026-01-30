# reviewer.py
import argparse
import sys
from config import Config
from llm import invoke_llm, PROMPTS
from git_tools import get_pr_diff, post_pr_comment, get_ci_status

def run_reviewer():
    # 1. Парсинг аргументов
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True, help="PR number to review")
    args = parser.parse_args()

    Config.validate()
    
    print(f"🕵️  Запуск AI Reviewer для PR #{args.pr}")

    # 2. Сбор контекста (Diff + CI Status)
    try:
        diff_content = get_pr_diff(args.pr)
        ci_status = get_ci_status(args.pr)
    except Exception as e:
        print(f"❌ Ошибка при получении данных PR: {e}")
        sys.exit(1)

    print(f"📄 Получены изменения. Анализ {len(diff_content)} символов...")
    print(f"🚦 {ci_status}")

    # 3. Формирование промпта
    # Мы добавляем diff и статус CI в контекст
    user_content = f"""
    CONTEXT:
    {ci_status}

    CHANGES TO REVIEW:
    {diff_content}
    """

    # 4. Вызов LLM
    try:
        review_result = invoke_llm(PROMPTS["reviewer"], user_content)
    except Exception as e:
        print(f"❌ Ошибка LLM: {e}")
        sys.exit(1)

    print("🤖 Ревью сгенерировано. Отправка в GitHub...")

    # 5. Публикация результата
    try:
        url = post_pr_comment(args.pr, review_result)
        print(f"✅ Комментарий опубликован: {url}")
        
        # Логика принятия решения (примерная)
        if "LGTM" in review_result and "Recommendation" not in review_result:
            print("🎉 Код одобрен агентом.")
            sys.exit(0) # Success code
        else:
            print("⚠️ Найдены замечания. Требуются исправления.")
            sys.exit(1) # Error code (чтобы CI мог остановить мердж, если нужно)
            
    except Exception as e:
        print(f"❌ Не удалось опубликовать комментарий: {e}")

if __name__ == "__main__":
    run_reviewer()