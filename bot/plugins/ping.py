from pyrogram import filters
from pyrogram.types import Message

from bot import Bot


@Bot.on_message(filters.command('ping'))
async def ping(_, message: Message):
    await message.reply_text('Pong!')