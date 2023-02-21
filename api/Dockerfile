FROM python:3.8.16-bullseye


WORKDIR /api
COPY . .

ENV PATH="${PATH}:/api"

RUN python -m venv env
RUN . ./env/bin/activate
RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT python ./src/main.py

