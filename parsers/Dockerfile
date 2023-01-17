FROM python:3.8-slim-buster

RUN apt update && \
    apt install -y build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    libbz2-dev \
    g++ \
    make\
    watch
RUN pip install --upgrade pip
RUN pip install poetry

RUN mkdir /parsers
ADD . /parsers
WORKDIR /parsers
RUN poetry install

RUN chmod +x ./start_autoupdate.sh
#RUN sh start_autoupdate.sh