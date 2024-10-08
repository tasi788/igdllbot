import logging
import os
from datetime import datetime, timezone, timedelta

import coloredlogs

from bot import config

opts = config.load()

def watchlog(name: str, level: str = None) -> logging.getLogger:
    """
    :param name: default to __name__
    :type name: str
    :param level: logger level from [DEBUG, INFO, WARNING]
    :type level: str
    :return: logging.getLogger
    :rtype: logging.getLogger
    """
    directory = 'log'
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)

    # 記錄檔路徑
    tzinfo = timezone(timedelta(hours=8))
    now = datetime.now(tz=tzinfo).strftime('%Y-%m-%d')
    filename = f'{now}.log'
    if not os.path.isfile(directory + '/' + filename):
        with open(directory + '/' + filename, 'w') as file:
            pass

    # log 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)

    file = logging.FileHandler(filename='./log/tmp.log')
    file.setFormatter(formatter)
    logger.addHandler(file)

    # colored
    if not level:
        level = opts.log.level

    coloredlogs.install(logger=logger, level=level)
    return logger
