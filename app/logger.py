import os
import logging
from logging.handlers import RotatingFileHandler

os.makedirs("app/logs", exist_ok=True)
logger = logging.getLogger("FinanceTracker")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s ", datefmt="%Y-%m-%d %H:%M:%S")

console_handler = logging.StreamHandler()

console_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)


filehandler = RotatingFileHandler("app/logs/app.log", maxBytes = 5*1024*1024, backupCount=3)

filehandler.setLevel(logging.DEBUG)

filehandler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(filehandler)

