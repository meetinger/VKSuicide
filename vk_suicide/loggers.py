import logging

import datetime as dt

def get_logger(name: str = "logger"):
    level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(module)s:%(lineno)d - %(message)s"
    )

    formatter_console = logging.Formatter(
        "[%(levelname)s] - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter_console)

    file_handler = logging.FileHandler(f"vk_suicide_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
                                       mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.getLogger().handlers.clear()

    if not logger.hasHandlers():
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger