FROM python:3.8.12

ARG LIST_OF_APPS "virtualenv supervisor nginx redis-server sqlite3"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN echo "Installing packages $LIST_OF_APPS" \
    && apt-get update -y \
    && apt-get install -y $LIST_OF_APPS

RUN useradd -ms /bin/bash myuser
USER myuser

WORKDIR /home/myuser

COPY --chown=myuser:myuser requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

ENV PATH="/home/myuser/.local/bin:${PATH}"

COPY --chown=myuser:myuser . .



