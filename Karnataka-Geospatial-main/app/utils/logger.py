import logging
import os

# Create logs folder if missing
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("geo_logger")

# Prevent duplicate handlers
if not logger.handlers:

    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        "logs/app.log"
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)