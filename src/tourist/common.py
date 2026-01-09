import logging

logger = logging.getLogger("tourist.common")
logger.addHandler(logging.NullHandler())

DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_RESULTS = 3
