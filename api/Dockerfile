FROM python:3.8.16-bullseye


WORKDIR /api
COPY . .

ENV PATH="${PATH}:/api"
ENV MONGO_HOST=localhost
ENV MONGO_PORT=27017
ENV MONGO_USER=root
ENV MONGO_PASSWORD=3akFUZ8x
ENV API_HOST=localhost
ENV API_PORT=8000

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT python ./src/main.py

