from pyrogram import filters
from pyrogram.types import Message, InputMediaVideo, InputMediaPhoto
from pyrogram.enums import ChatAction
from bot import Bot
import instaloader
from instaloader.exceptions import BadResponseException
import re
from bot.utils import watchlog
from ffmpeg.asyncio import FFmpeg
from io import BytesIO
import httpx
import time
from html import escape

logger = watchlog(__name__)
insta = instaloader.Instaloader()


async def transcode_video(video_url):
    r = httpx.get(video_url)
    filename = f'{time.time()}.mp4'
    outname = f'output_{filename}'
    with open(filename, 'wb') as f:
        f.write(r.content)
    # input_video = BytesIO(r.content)
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(filename, f="mp4")
        .output(
            outname,
            {"codec:v": "libx264"},
            preset="veryfast",
            crf=24,
        )
    )
    # ffmpeg = FFmpeg(executable='ffmpeg')
    # input_file = ffmpeg.input(video_url)
    # output_file = 'output.mp4'
    # ffmpeg.output(input_file, output_file).run_async()
    # return output_file

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def clean_url(url: str) -> str:
    return re.sub(r'\?igsh=.*$', '', url)


@Bot.on_message(filters.regex(r'https://www.instagram.com/.*'))
async def get_url(_, message: Message):
    url = message.text
    cleaned_url = clean_url(url)
    pattern = r"https://www\.instagram\.com/(?:stories/[\w-]+|reel|p|[\w-]+/p)/([\w-]+)/?"
    try:
        shortcode = re.search(pattern, url).group(1)
    except AttributeError:
        logger.error(f'Invalid URL: {url}')
        return
    try:
        post = instaloader.Post.from_shortcode(insta.context, shortcode)
    except BadResponseException:
        logger.error(f'Bad response: {url}')
        await message.reply_text('貼文解析失敗，無法下載。')
        return

    send = await message.reply_text('正在下載貼文，請稍後。')

    caption = '<a href="{url}">{author}</a>'.format(author=post.owner_username, url=cleaned_url)
    if post.mediacount > 1:
        await message.reply_chat_action(ChatAction.UPLOAD_VIDEO)
        media_list = []
        for img in post.get_sidecar_nodes():
            if img.is_video:
                media_list.append(InputMediaVideo(img.video_url))
            else:
                media_list.append(InputMediaPhoto(img.display_url))

        if len(media_list) > 10:
            chunks = list(chunk_list(media_list, 10))
            for i, chunk in enumerate(chunks):
                if i == 0:
                    chunk[0].caption = caption
                await message.reply_media_group(chunk)
    else:
        await message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        if post.is_video:
            logger.info(post.video_url)
            try:
                await message.reply_video(post.video_url, caption=post.caption)
            except Exception as _:
                logger.error(f'Error: {url}')
                await message.reply_text('貼文解析失敗，無法下載影片。')
        else:
            try:
                await message.reply_photo(post.url, caption=post.caption)
            except:
                logger.error(f'Error: {url}')
                await message.reply_text('貼文解析失敗，無法下載圖片。')
    await send.delete()
