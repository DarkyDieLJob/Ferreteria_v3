import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
loglevel = "info"
accesslog = "-"
errorlog = "-"
