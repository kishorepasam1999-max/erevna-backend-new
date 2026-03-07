import logging
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    handler = RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=5_000_000, backupCount=5
    )
    handler.setLevel(app.config["LOG_LEVEL"])
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
