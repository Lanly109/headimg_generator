import asyncio
import re
from typing import Union

from aiohttp import ClientSession

from hoshino import aiorequests, logger
from .exception import NetworkError

headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-cn"
}


async def get_content(url: str, session: ClientSession) -> Union[Exception, bytes]:
    try:
        async with session.get(url, headers=headers) as resp:
            return await resp.content.read()
    except Exception as e:
        logger.warning(f"aiorequest error: {e}")
        return await (await aiorequests.get(url)).content

async def download_url(url: str) -> bytes:
    async with ClientSession() as session:
        for i in range(3):
            try:
                resp = await get_content(url, session)
                return resp
            except Exception as e:
                logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                await asyncio.sleep(3)
    raise NetworkError(f"{url} 下载失败！")


def check_qq_number(qq: str) -> bool:
    return bool(re.match(r"^\d{5,11}$", qq))
