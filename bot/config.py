import logging
import os
import sys

import coloredlogs
from pydantic import BaseModel
from yaml import safe_load
from yaml.error import Mark, YAMLError, MarkedYAMLError

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger)



class Config(BaseModel):
    class Bot(BaseModel):
        bot_token: str
        api_id: int
        api_hash: str


    class Log(BaseModel):
        level: str
        channel: int
        thread: int


    dev_mode: bool
    bot: Bot
    log: Log
    admin: int = 5440674042


def load(initial: bool = False):
    """
    讀取設定用的東西
    usage: bot.config.loads()
    tpyes: config 自己找找
    """
    filename = 'env_config.yml'
    if not os.path.isfile(f'./{filename}'):
        logger.critical('找不到 env_config.yml')
        sys.exit(1)

    with open(f'./{filename}', mode='r', encoding='utf8') as f:
        try:
            loads = safe_load(f.read())
        except (Mark, YAMLError, MarkedYAMLError):
            logger.critical('解讀 env_config.yml 錯誤')
            sys.exit(1)
        else:
            # check if set dev mode true.
            if loads.get('dev_mode'):
                if initial:
                    logger.warning('Set to Development mode.')
                if not os.path.isfile(f'./dev_{filename}'):
                    logger.critical('找不到 dev_env_config.yml')
                    sys.exit(1)
                with open(f'./dev_{filename}', mode='r', encoding='utf8') as f_dev:
                    try:
                        loads = safe_load(f_dev.read())
                        opts: Config = Config.from_dict(loads)
                        opts.dev_mode = True
                        return opts
                    except (Mark, YAMLError, MarkedYAMLError):
                        logger.critical('解讀 dev_env_config.yml 錯誤')
                        sys.exit(1)

            opts: Config = Config.parse_obj(loads)
            return opts
