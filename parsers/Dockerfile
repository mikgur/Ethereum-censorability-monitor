FROM python:3.8-slim-buster
WORKDIR /app

COPY . .
RUN pip3 install poetry & poetry install

#RUN chmod +x ./start_autoupdate.sh & chmod +x ./lido_parser.py & chmod +x ./ofac_parser.py & ./start_autoupdate.sh