import hashlib
import hoshino
import json
import os
from pathlib import Path

import aiofiles
import httpx
from aiocache import cached
from .config import *

data_path = Path() / os.path.dirname(__file__) / 'resources'


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
                hoshino.logger.warning(f"Error downloading {url}, retry {i}/3: {e}")
                # print(f"Error downloading {url}, retry {i}/3: {str(e)}")
    raise DownloadError


async def download_resource(path: str) -> bytes:
    return await download_url(f"{petpet_resource_url}{path}")


async def check_resources():
    resource_list = json.loads(
        (await download_resource("resource_list.json")).decode("utf-8")
    )
    for resource in resource_list:
        file_name = str(resource["path"])
        file_path = data_path / file_name
        file_hash = str(resource["hash"])
        if (
                file_path.exists()
                and hashlib.md5(file_path.read_bytes()).hexdigest() == file_hash
        ):
            continue
        print(f"Downloading {file_name} ...")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = await download_resource(file_name)
            with file_path.open("wb") as f:
                f.write(data)
        except Exception as e:
            print(str(e))


async def get_resource(path: str, name: str) -> bytes:
    file_path = data_path / path / name
    if not file_path.exists():
        await check_resources()
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
    url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if not data or hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = await download_url(url)
        if not data:
            raise DownloadError
    return data
