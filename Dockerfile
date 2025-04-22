FROM python:3.10-slim

# Установка зависимостей для сборки aiohttp
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && apt-get clean

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем код бота
COPY . /app
WORKDIR /app

# Запуск
CMD ["python", "bot.py"]
