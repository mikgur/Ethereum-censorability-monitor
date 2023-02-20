FROM python:3.8.16-bullseye

WORKDIR /mongo_migrator
COPY . .

ENV MONGO_HOST localhost
ENV MONGO_PORT 27017
ENV MONGO_USER root
ENV MONGO_PASSWORD password

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.sh

ENTRYPOINT bash entrypoint.sh
