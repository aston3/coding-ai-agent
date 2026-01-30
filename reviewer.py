import argparse
import sys
from configs.config import Config
from configs.llm import invoke_llm, PROMPTS
from configs.git_tools import get_pr_diff, post_pr_comment, get_ci_status

def run_reviewer():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True, help="PR number to review")
    args = parser.parse_args()

    Config.validate()
    print(f"🕵️  Запуск AI Reviewer для PR #{args.pr}")

    try:
        diff_content = get_pr_diff(args.pr)
        ci_status = get_ci_status(args.pr)
    except Exception as e:
        print(f"❌ Ошибка при получении данных PR: {e}")
        sys.exit(1)

    print(f"📄 Анализ {len(diff_content)} символов...")

    user_content = f"""
    CONTEXT:
    {ci_status}

    CHANGES TO REVIEW:
    {diff_content}
    """

    try:
        review_result = invoke_llm(PROMPTS["reviewer"], user_content)
    except Exception as e:
        print(f"❌ Ошибка LLM: {e}")
        sys.exit(1)

    print("🤖 Ревью сгенерировано. Публикация...")

    # ЛОГИКА ОПРЕДЕЛЕНИЯ СТАТУСА
    # Если LLM написала "LGTM" или "Looks Good To Me" -> успех
    is_lgtm = "LGTM" in review_result or "Looks Good To Me" in review_result
    
    # Добавляем системный маркер в конец комментария, чтобы Fixer понял сигнал
    if is_lgtm:
        final_comment = review_result + "\n\n✅ **LGTM** - No further changes required."
        exit_code = 0
    else:
        final_comment = review_result + "\n\n⚠️ **Review Status:** Changes requested."
        exit_code = 1

    try:
        url = post_pr_comment(args.pr, final_comment)
        print(f"✅ Комментарий опубликован: {url}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Не удалось опубликовать комментарий: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_reviewer()