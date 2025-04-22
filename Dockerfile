FROM python:3.10-slim

RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && apt-get clean

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "bot.py"]
