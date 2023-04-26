FROM python:3.10-buster

WORKDIR /app

ENV PYTHONOPTIMIZE true

# setup timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app

RUN apt update && apt install -y python3-pip                                  \
    && pip3 install poetry==1.2.2                                             \
    && poetry export -f requirements.txt -o requirements.txt                  \
    && pip3 install -r requirements.txt                                       \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list


CMD python mempool_collector.py