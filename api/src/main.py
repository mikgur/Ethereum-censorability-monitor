import os

import uvicorn

from .app import init_app

API_HOST = os.environ["API_HOST"]
API_PORT = os.environ["API_PORT"]

app = init_app()

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=int(API_PORT))
