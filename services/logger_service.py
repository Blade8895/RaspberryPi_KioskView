import os
import logging
from logging.handlers import RotatingFileHandler


def get_logger(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("kioskview")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = RotatingFileHandler(os.path.join(log_dir, "kioskview.log"), maxBytes=2_000_000, backupCount=3)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
