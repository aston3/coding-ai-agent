FROM python:3.11-slim

# Устанавливаем git
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код агента
COPY . .

# Переменные окружения (будут переопределены через docker-compose или CI)
ENV PYTHONUNBUFFERED=1

# Точка входа по умолчанию (можно переопределять)
CMD ["python", "coder.py"]