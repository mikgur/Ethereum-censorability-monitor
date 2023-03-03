FROM python:3.8.16-bullseye


WORKDIR /api
COPY . .

ENV PATH="${PATH}:/api"
ENV MONGO_HOST=127.0.0.1
ENV MONGO_PORT=27017
ENV MONGO_USER=root
ENV MONGO_PASSWORD=test_pass
ENV API_HOST=127.0.0.1
ENV API_PORT=8000
ENV AUTH_KEY=123

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT python ./src/main.py

