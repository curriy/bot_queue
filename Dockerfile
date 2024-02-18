FROM python:3.12.2-bookworm

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]