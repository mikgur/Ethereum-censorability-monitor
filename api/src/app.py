import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import uvloop
from fastapi import FastAPI

from .middleware import add_middlewares
from .mongo import load_mongo_collections
from .views import add_routing


def setup_asyncio(thread_name_prefix: str) -> None:
    uvloop.install()

    loop = asyncio.get_event_loop()

    executor = ThreadPoolExecutor(thread_name_prefix=thread_name_prefix)
    loop.set_default_executor(executor)


def init_app() -> FastAPI:
    app = FastAPI()

    setup_asyncio(thread_name_prefix="Neutrality Watch API")
    load_mongo_collections()
    add_routing(app)
    add_middlewares(app)

    return app
