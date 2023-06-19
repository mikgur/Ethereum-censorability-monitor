import os
from multiprocessing import cpu_count

# The socket to bind.
host = os.environ["API_HOST"]
port = int(os.environ["API_PORT"])
bind = f"{host}:{port}"

# The maximum number of pending connections.
backlog = 2048

# The number of worker processes for handling requests.
workers = cpu_count()

# The type of workers to use.
worker_class = "uvicorn.workers.UvicornWorker"

# The maximum number of requests a worker will process before restarting.
max_requests = 1024

# Workers silent for more than this many seconds are killed and restarted.
timeout = 3600

# Timeout for graceful workers restart.
graceful_timeout = 5

# The number of seconds to wait for requests on a Keep-Alive connection.
keepalive = 5

# The maximum size of HTTP request line in bytes.
# This parameter can be used to prevent any DDOS attack.
limit_request_line = 512

# Load application code before the worker processes are forked.
preload_app = False

# Detaches the server from the controlling terminal and enters the background.
daemon = False
