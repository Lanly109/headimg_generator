import httpx
import hashlib
import aiofiles
from aiocache import cached
import os


data_path = os.path.join(os.path.dirname(__file__), 'resources')


class DownloadError(Exception):
    pass


class ResourceError(Exception):
    pass


async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                return resp.content
            except Exception as e:
                # sv.logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                print(f"Error downloading {url}, retry {i}/3: {str(e)}")
    raise DownloadError


async def get_resource(path: str, name: str) -> bytes:
    file_path = os.path.join(data_path, path, name)
    if not os.path.exists(file_path):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://cdn.jsdelivr.net/gh/MeetWq/nonebot-plugin-petpet@master/resources/{path}/{name}"
        data = await download_url(url)
        if data:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(data)
    if not os.path.exists(file_path):
        raise ResourceError
    async with aiofiles.open(file_path, "rb") as f:
        return await f.read()


@cached(ttl=600)
async def get_image(name: str) -> bytes:
    return await get_resource("images", name)


@cached(ttl=600)
async def get_font(name: str) -> bytes:
    return await get_resource("fonts", name)


@cached(ttl=60)
async def download_avatar(user_id: str) -> bytes:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if not data or hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = await download_url(url)
        if not data:
            raise DownloadError
    return data
