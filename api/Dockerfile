FROM python:3.8.16-bullseye


WORKDIR /api
COPY . .

ENV MONGO_HOST localhost
ENV MONGO_PORT 27017
ENV MONGO_USER root
ENV MONGO_PASSWORD password
ENV API_HOST 127.0.0.1
ENV API_PORT 8000

EXPOSE 8000

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.sh

ENTRYPOINT bash entrypoint.sh

