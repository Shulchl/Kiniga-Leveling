import json
import logging
import logging.handlers
import os

from base.struct import Config

cfg = None
log = None


basePath = '.'
path = os.path.abspath(os.path.join(basePath, '_temp'))
isExist = os.path.exists(path)
if not isExist:
    os.mkdir(path)

def log_handler() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        filename='log.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotaciona em 5 arquivos
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


log = log_handler()


with open('config.json', 'r', encoding='utf-8') as f:
	cfg = Config(json.loads(f.read()))

	f.close()