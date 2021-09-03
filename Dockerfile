FROM python:3.8.12

WORKDIR /usr/src/app

ARG LIST_OF_APPS "virtualenv supervisor nginx redis-server sqlite3"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN echo "Installing packages $LIST_OF_APPS" \
    && apt-get update -y \
    && apt-get install -y $LIST_OF_APPS

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .



