# auth.py
import os
import time
import jwt
import requests

def get_installation_token(installation_id):
    # 1. Читаем приватный ключ (который мы скачаем из настроек GitHub App)
    private_key_path = os.getenv("PRIVATE_KEY_PATH", "private-key.pem")
    with open(private_key_path, 'r') as f:
        private_key = f.read()

    # 2. Генерируем JWT (JSON Web Token)
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "iss": os.getenv("GITHUB_APP_ID")
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    # 3. Обмениваем JWT на токен доступа к конкретной установке (репозиторию)
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    resp = requests.post(url, headers=headers)
    
    if resp.status_code != 201:
        raise Exception(f"Auth failed: {resp.text}")
        
    return resp.json()["token"]