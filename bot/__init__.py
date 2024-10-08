import asyncio
from asyncio import AbstractEventLoop
from typing import Union, Optional
import sys

from pyrogram import Client
from pyrogram.errors import ApiIdInvalid, AuthKeyUnregistered
from pyrogram.session import Session
from pyrogram.types import User
from bot import config
from bot.utils import watchlog

opt = config.load(initial=True)
logger = watchlog(__name__)


class Bot(Client):
    _instance: Union[None, "Bot"] = None
    me: Optional[User] = None

    def __init__(self):
        super().__init__(
            name='bot',
            api_id=opt.bot.api_id,
            api_hash=opt.bot.api_hash,
            bot_token=opt.bot.bot_token,
            plugins=dict(root='bot/plugins'),
        )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def __get_me(self):
        me: User = await self.get_me()
        info_str: str = f'[Listening] {me.first_name}'
        info_str += f' {me.last_name}' if me.last_name else ''
        info_str += f' (@{me.username})' if me.username else ''
        info_str += f' ID: {me.id}'

        logger.info(info_str)
        self.me: User = me

    async def __self_test(self):
        # Disable notice
        Session.notice_displayed = True
        try:
            await self.start()
        except (ApiIdInvalid, AttributeError):
            logger.critical('!!! API ID is invalid !!!')
            sys.exit(1)
        except AuthKeyUnregistered:
            logger.critical('!!! Session expired !!!')
            logger.critical("      Removing old session and exiting!")
            await self.storage.delete()
            exit(1)

        try:
            await self.__get_me()
        except Exception as e:
            logger.exception(e)
            sys.exit(1)

        await self.stop()

    @property
    def config(self) -> config.Config:
        return opt

    def start_serve(self):
        loop: AbstractEventLoop = asyncio.get_event_loop()
        run = loop.run_until_complete
        run(self.__self_test())
        self.run()
