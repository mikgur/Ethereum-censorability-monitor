from time import time

import psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.responses import Response

BYTE_TO_GB = 1024**3


def add_prometheus_middleware(app: FastAPI):
    registry = CollectorRegistry()
    requests_count = Counter("requests_count", "App Request Count", registry=registry)
    response_time = Histogram(
        "response_time", "Response time (in seconds)", registry=registry
    )
    cpu_usage_in_percents = Gauge(
        "cpu_usage_in_percents", "CPU usage (in percents)", registry=registry
    )
    ram_usage = Gauge("ram_usage", "RAM usage (in GB)", registry=registry)
    ram_usage_in_percents = Gauge(
        "ram_usage_in_percents", "RAM usage (in percents)", registry=registry
    )
    disk_usage = Gauge("disk_usage", "Disk usage (in GB)", registry=registry)
    disk_usage_in_percents = Gauge(
        "disk_usage_in_percents", "Disk usage (in percents)", registry=registry
    )

    @app.middleware("http")
    async def monitor_requests(request: Request, call_next):
        requests_count.inc()

        start_time = time()
        response = await call_next(request)
        latency = time() - start_time

        response_time.observe(latency)

        return response

    @app.get("/metrics")
    async def get_metrics():
        """Prometheus endpoint"""
        cpu_usage_in_percents.set(psutil.cpu_percent())
        ram_usage.set(psutil.virtual_memory().used / BYTE_TO_GB)
        ram_usage_in_percents.set(psutil.virtual_memory().percent)
        disk_usage.set(psutil.disk_usage("/").used / BYTE_TO_GB)
        disk_usage_in_percents.set(psutil.disk_usage("/").percent)

        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


def add_middlewares(app: FastAPI):
    add_prometheus_middleware(app)
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
