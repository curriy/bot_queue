FROM python:3.12-slim-buster

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]