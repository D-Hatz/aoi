bind = "0.0.0.0:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000

# Note: "Control server error: no running event loop" is a known harmless warning
# when using gevent workers. It doesn't affect application functionality.
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
loglevel = "info"
preload_app = False
