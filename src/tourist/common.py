import logging
import time
from functools import wraps

logger = logging.getLogger("tourist.common")
logger.addHandler(logging.NullHandler())


DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 15.0
DEFAULT_WINDOW_SIZE = (1920, 1080)


def retry(n: int = 1):
    def do(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(n + 1):
                try:
                    result = func(*args, **kwargs)
                    return result
                except:
                    logger.exception(f"{func.__name__} error on attempt={attempt}")
                    # TODO/Contribution: this may not help
                    time.sleep(0.5)

            # return None after all attempts
            return None

        return wrapper

    return do
