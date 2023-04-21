FROM python:3.8.16-bullseye

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

WORKDIR /updater
COPY . .

ENV PATH="${PATH}:/updater"
ENV MONGO_HOST=127.0.0.1
ENV MONGO_PORT=27017
ENV MONGO_USER=root
ENV MONGO_PASSWORD=test_pass

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt
RUN chmod +x ./run_updater.sh
ENTRYPOINT sh run_updater.sh


