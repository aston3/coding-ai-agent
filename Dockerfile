# Используем легкий Python образ
FROM python:3.11-slim

# 1. Установка системных зависимостей
# git - нужен для клонирования репозиториев
# curl - полезен для проверок
RUN apt-get update && \
    apt-get install -y git curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Настройка рабочей директории
WORKDIR /app

# 3. Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь код проекта
COPY . .

# 5. Настройка переменных окружения
# PYTHONPATH позволяет питону видеть модули в корне (configs, coder.py) из папки server
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 6. Открываем порт (внутренний порт контейнера)
EXPOSE 5000

# 7. Точка входа: Запуск Flask сервера
# Мы запускаем server.py как модуль или напрямую
CMD ["python", "server/server.py"]