# server.py
from flask import Flask, request, jsonify
import threading
import subprocess
import os
from auth import get_installation_token

app = Flask(__name__)

def run_agent_process(mode, token, repo_name, issue_number):
    """Запускает coder.py или reviewer.py в отдельном потоке"""
    env = os.environ.copy()
    env["GH_PAT"] = token # Подменяем токен на временный токен App!
    env["GITHUB_REPOSITORY"] = repo_name
    
    # Команда запуска (предполагаем, что скрипты в той же папке)
    cmd = ["python3", "coder.py" if mode == "coder" else "reviewer.py"]
    
    if mode == "coder":
        cmd.extend(["--issue", str(issue_number)])
    elif mode == "reviewer":
        cmd.extend(["--pr", str(issue_number)]) # В PR номер issue = номер PR
    elif mode == "fixer":
        cmd.extend(["--pr", str(issue_number), "--fix"])

    print(f"🚀 Запуск агента для {repo_name} #{issue_number}")
    subprocess.run(cmd, env=env)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event = request.headers.get('X-GitHub-Event')
    
    # Проверка, что это событие от нашей установки
    if 'installation' not in data:
        return jsonify({"msg": "No installation data"}), 200

    installation_id = data['installation']['id']
    repo_name = data['repository']['full_name']
    
    # Получаем токен для этого репозитория
    try:
        token = get_installation_token(installation_id)
    except Exception as e:
        print(f"Auth Error: {e}")
        return jsonify({"error": "Auth failed"}), 500

    # ЛОГИКА ТРИГГЕРОВ
    
    # 1. New Issue -> Coder
    if event == 'issues' and data['action'] == 'opened':
        threading.Thread(target=run_agent_process, args=("coder", token, repo_name, data['issue']['number'])).start()
        return jsonify({"msg": "Coder started"}), 200

    # 2. PR Opened/Sync -> Reviewer
    if event == 'pull_request' and data['action'] in ['opened', 'synchronize']:
        threading.Thread(target=run_agent_process, args=("reviewer", token, repo_name, data['number'])).start()
        return jsonify({"msg": "Reviewer started"}), 200

    # 3. Comment -> Fixer
    if event == 'issue_comment' and data['action'] == 'created':
        # Если это PR и коммент не содержит LGTM и не от бота
        if 'pull_request' in data['issue'] and "LGTM" not in data['comment']['body']:
             threading.Thread(target=run_agent_process, args=("fixer", token, repo_name, data['issue']['number'])).start()
             return jsonify({"msg": "Fixer started"}), 200

    return jsonify({"msg": "Event ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80) # Слушаем порт 80 для облака