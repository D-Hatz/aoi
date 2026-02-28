from flask import Flask
import time

app = Flask(__name__)


def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


@app.route("/cpu")
def cpu_bound_task():
    start_time = time.time()
    fib_number = fibonacci(35)
    end_time = time.time()
    duration = end_time - start_time
    return f"fib(35)={fib_number}, start_time={round(start_time, 2)}, end_time={round(end_time, 2)}, duration={round(duration, 2)}\n"

