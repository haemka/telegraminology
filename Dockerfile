FROM python:3-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r /app/requirements.txt

COPY src/* ./

CMD [ "python3", "/app/bot.py", "-c", "/app/config.ini"]
