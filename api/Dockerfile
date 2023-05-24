FROM python:3.10.11-bullseye as build

COPY . .

RUN pip install -U --no-cache-dir pip setuptools wheel && \
    pip wheel -w dist -r requirements.txt


FROM python:3.10.11-bullseye as runtime

WORKDIR /api
COPY --from=build dist dist
COPY --from=build gunicorn.config.py ./
COPY --from=build src ./src

ENV PATH="${PATH}:/api"
ENV MONGO_HOST=127.0.0.1
ENV MONGO_PORT=27017
ENV MONGO_USER=root
ENV MONGO_PASSWORD=test_pass
ENV API_HOST=127.0.0.1
ENV API_PORT=8000
ENV AUTH_KEY=123

RUN pip install -U --no-cache-dir pip dist/*.whl && \
    rm -rf dist

EXPOSE 8000

CMD ["gunicorn", "src.main:app", "-c", "gunicorn.config.py"]

