FROM python:3.8-slim-buster

RUN apt-get update \
    && apt-get install -y pkg-config default-libmysqlclient-dev awscli build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD [ "python3", "app.py" ]