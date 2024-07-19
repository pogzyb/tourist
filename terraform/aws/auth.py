import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


X_SECRET_VALUE = os.getenv("X_SECRET_VALUE")


def lambda_handler(event, _):
    logger.info("Checking request for secret value.")
    x_secret = event["headers"].get("x-secret")
    response = {"isAuthorized": x_secret == X_SECRET_VALUE}
    return response
