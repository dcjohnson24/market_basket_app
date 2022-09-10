FROM python:3.8.12


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ARG FLASK_ENV

RUN apt-get update -y

RUN useradd -ms /bin/bash myuser

WORKDIR /home/myuser

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

ENV PATH="/home/myuser/.local/bin:${PATH}"

USER myuser

COPY --chown=myuser:myuser . .



