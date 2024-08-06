import logging
import time
from functools import wraps

logger = logging.getLogger("tourist.utils")
logger.addHandler(logging.NullHandler())


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
