import os
import argparse
import sys
from github import Github, Auth
from langchain_openai import ChatOpenAI # <-- ИЗМЕНЕНИЕ
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("OPENROUTER_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")

def main(pr_number):
    if not API_KEY or not GITHUB_TOKEN:
        print("Error: Keys are missing")
        sys.exit(1)

    print(f"--- Reviewing PR #{pr_number} ---")
    
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(int(pr_number))
    
    print(f"Title: {pr.title}")
    
    diff_content = []
    for file in pr.get_files():
        if file.patch:
            diff_content.append(f"File: {file.filename}\nDiff:\n{file.patch}\n")
    
    if not diff_content:
        print("No changes found.")
        sys.exit(0)

    full_diff = "\n".join(diff_content)
    
    # Настройка OpenRouter
    llm = ChatOpenAI(
        model="tngtech/deepseek-r1t2-chimera:free",
        openai_api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1",  # <-- Используем base_url
        temperature=0.2
    )

    system_prompt = """Ты - строгий Code Reviewer.
    Проверь код на ошибки.
    1. Если код хороший, напиши ТОЛЬКО: "LGTM".
    2. Если есть ошибки, напиши список."""
    
    user_prompt = f"""
    PR: {pr.title}
    ИЗМЕНЕНИЯ:
    {full_diff}
    """

    print("Asking DeepSeek Reviewer...")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    # DeepSeek R1 может выдавать мысли в <think>...</think>. Их лучше вырезать для чистоты,
    # но для комментария можно оставить или убрать простым replace.
    review_result = response.content.replace("<think>", "**Thinking:**\n").replace("</think>", "\n\n**Verdict:**")
    
    pr.create_issue_comment(f"🤖 **DeepSeek Reviewer Report**\n\n{review_result}")
    print(f"Comment posted to PR #{pr_number}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True, help="PR number")
    args = parser.parse_args()
    main(args.pr)