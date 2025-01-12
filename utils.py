import asyncio
import base64
import shlex
from io import BytesIO
from typing import Union

import httpx
from arclet.alconna import TextFormatter
from meme_generator.meme import Meme

import hoshino
from hoshino.typing import MessageSegment
from .config import *
from .exception import NetworkError


def bytesio2b64(img: Union[BytesIO, bytes]) -> str:
    if isinstance(img, BytesIO):
        img = img.getvalue()
    return f"base64://{base64.b64encode(img).decode()}"


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                hoshino.logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise NetworkError(f"{url} 下载失败！")


def split_text(text: str) -> List[str]:
    try:
        return shlex.split(text)
    except Exception as e:
        hoshino.logger.warning(f"{e}")
        return text.split()


async def meme_info(meme: Meme) -> str:
    keywords = "、".join([f'"{keyword}"' for keyword in meme.keywords])
    shortcuts = "、".join(
        [f'"{shortcut.humanized or shortcut.key}"' for shortcut in meme.shortcuts]
    )
    tags = "、".join([f'"{tag}"' for tag in meme.tags])

    image_num = f"{meme.params_type.min_images}"
    if meme.params_type.max_images > meme.params_type.min_images:
        image_num += f" ~ {meme.params_type.max_images}"

    text_num = f"{meme.params_type.min_texts}"
    if meme.params_type.max_texts > meme.params_type.min_texts:
        text_num += f" ~ {meme.params_type.max_texts}"

    default_texts = ", ".join([f'"{text}"' for text in meme.params_type.default_texts])

    args_info = ""
    if args_type := meme.params_type.args_type:
        formater = TextFormatter()
        for option in args_type.parser_options:
            opt = option.option()
            alias_text = (
                    " ".join(opt.requires)
                    + (" " if opt.requires else "")
                    + "│".join(sorted(opt.aliases, key=len))
            )
            args_info += (
                f"\n  * {alias_text}{opt.separators[0]}"
                f"{formater.parameters(opt.args)} {opt.help_text}"
            )

    info = (
            f"表情名：{meme.key}"
            + f"\n关键词：{keywords}"
            + (f"\n快捷指令：{shortcuts}" if shortcuts else "")
            + (f"\n标签：{tags}" if tags else "")
            + f"\n需要图片数目：{image_num}"
            + f"\n需要文字数目：{text_num}"
            + (f"\n默认文字：[{default_texts}]" if default_texts else "")
            + (f"\n可选参数：{args_info}" if args_info else "")
    )
    info += "\n表情预览：\n"
    img = MessageSegment.image(bytesio2b64(meme.generate_preview()))
    return f"{info}{img}"


if memes_check_resources_on_startup:
    from meme_generator.download import check_resources
    from nonebot import on_startup


    @on_startup
    async def _():
        hoshino.logger.info("正在检查资源文件...")
        await asyncio.create_task(check_resources())
