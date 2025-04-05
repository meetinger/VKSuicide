import logging
import multiprocessing as mp
import datetime as dt
from typing import Union

from tqdm import tqdm
import sys
from logging.handlers import QueueHandler, QueueListener
from functools import wraps

LOG_QUEUE: Union[mp.Queue, None] = None


def worker_init(log_queue: mp.Queue):
    set_log_queue(log_queue)


def set_log_queue(queue: mp.Queue):
    global LOG_QUEUE
    LOG_QUEUE = queue


class TqdmLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg, file=sys.stderr)
        except Exception:
            self.handleError(record)


def _create_handlers():
    formatter_file = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(module)s:%(lineno)d - %(message)s"
    )
    formatter_console = logging.Formatter(
        "[%(levelname)s] [%(name)s] - %(message)s"
    )

    file_handler = logging.FileHandler(
        f"vk_suicide_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        mode="a", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter_file)

    console_handler = TqdmLoggingHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter_console)

    return file_handler, console_handler


def setup_main_logger(log_queue: mp.Queue, name: str = "logger"):
    global LOG_QUEUE
    LOG_QUEUE = log_queue

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler, console_handler = _create_handlers()
    queue_handler = QueueHandler(log_queue)

    logger.addHandler(queue_handler)

    listener = QueueListener(log_queue, file_handler, console_handler)
    listener.start()

    return logger, listener


def get_worker_logger(log_queue: Union[mp.Queue, None] = None, name: str = "logger"):
    if log_queue is None:
        global LOG_QUEUE
        log_queue = LOG_QUEUE
    if log_queue is None:
        raise RuntimeError("LOG_QUEUE is not set. Use set_log_queue(queue) before calling get_worker_logger.")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    return logger


def get_logger(name: str = "logger"):
    global LOG_QUEUE
    if LOG_QUEUE is None:
        raise RuntimeError("LOG_QUEUE is not set. Call set_log_queue(queue) first.")
    return get_worker_logger(LOG_QUEUE, name)


def with_logger(name: str = "logger"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_queue = kwargs.get("log_queue")

            if log_queue is None:
                raise ValueError("log_queue must be passed to function decorated with @with_logger")

            set_log_queue(log_queue)
            logger = get_logger(name)
            return func(*args, logger=logger, **kwargs)

        return wrapper
    return decorator