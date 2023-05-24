from time import time

import psutil
from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

BYTE_TO_GB = 1024**3


def add_prometheus_middleware(outer_app: FastAPI, inner_app: FastAPI, moniroting_app: FastAPI):
    registry = CollectorRegistry()
    requests_count = Counter("API_requests_count", "App Request Count", registry=registry)
    response_time = Histogram("API_response_time", "Response time (in seconds)", registry=registry)
    cpu_usage_in_percents = Gauge("API_cpu_usage_in_percents", "CPU usage (in percents)", registry=registry)
    ram_usage = Gauge("API_ram_usage", "RAM usage (in GB)", registry=registry)
    ram_usage_in_percents = Gauge("API_ram_usage_in_percents", "RAM usage (in percents)", registry=registry)
    disk_usage = Gauge("API_disk_usage", "Disk usage (in GB)", registry=registry)
    disk_usage_in_percents = Gauge("API_disk_usage_in_percents", "Disk usage (in percents)", registry=registry)

    @inner_app.middleware("http")
    async def monitor_inner_requests(request: Request, call_next):
        requests_count.inc()

        start_time = time()
        response = await call_next(request)
        latency = time() - start_time

        response_time.observe(latency)

        return response

    @outer_app.middleware("http")
    async def monitor_outer_requests(request: Request, call_next):
        requests_count.inc()

        start_time = time()
        response = await call_next(request)
        latency = time() - start_time

        response_time.observe(latency)

        return response

    @moniroting_app.get("/metrics")
    async def get_metrics():
        """Prometheus endpoint"""
        cpu_usage_in_percents.set(psutil.cpu_percent())
        ram_usage.set(psutil.virtual_memory().used / BYTE_TO_GB)
        ram_usage_in_percents.set(psutil.virtual_memory().percent)
        disk_usage.set(psutil.disk_usage("/").used / BYTE_TO_GB)
        disk_usage_in_percents.set(psutil.disk_usage("/").percent)

        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


def add_middlewares(outer_app: FastAPI, inner_app: FastAPI, moniroting_app: FastAPI):
    add_prometheus_middleware(outer_app, inner_app, moniroting_app)

    outer_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    inner_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://frontend:5137",
            "https://frontend:5137",
            "http://eth.neutralitywatch.com",
            "https://eth.neutralitywatch.com",
            "http://eth.neutralitywatch.com:80",
            "https://eth.neutralitywatch.com:443",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    moniroting_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://monitoring.neutralitywatch.com",
            "https://monitoring.neutralitywatch.com",
            "http://monitoring.neutralitywatch.com:9090",
            "https://monitoring.neutralitywatch.com:9090",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
