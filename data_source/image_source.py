import hashlib
from pathlib import Path

import anyio
import emoji
from pydantic import BaseModel
from strenum import StrEnum
from .compat import PYDANTIC_V2
from .utils import download_url


class ImageSource(BaseModel):
    def get_url(self) -> str:
        raise NotImplementedError

    async def get_image(self) -> bytes:
        raise NotImplementedError


class ImageUrl(ImageSource):
    url: str

    def get_url(self) -> str:
        return self.url

    async def get_image(self) -> bytes:
        return await download_url(self.url)


class EmojiStyle(StrEnum):
    Apple = "apple"
    Google = "google"
    Microsoft = "microsoft"
    Samsung = "samsung"
    WhatsApp = "whatsapp"
    Twitter = "twitter"
    Facebook = "facebook"
    Messenger = "messenger"
    JoyPixels = "joypixels"
    OpenMoji = "openmoji"
    EmojiDex = "emojidex"
    LG = "lg"
    HTC = "htc"
    Mozilla = "mozilla"


class Emoji(ImageSource):
    data: str
    if PYDANTIC_V2:
        from pydantic import field_validator

        @field_validator("data")
        def check_emoji(cls, value: str) -> str:
            if not emoji.is_emoji(value):
                raise ValueError("Not a emoji")
            return value
    else:
        from pydantic import validator

        @validator("data")
        def check_emoji(cls, value: str) -> str:
            if not emoji.is_emoji(value):
                raise ValueError("Not a emoji")
            return value

    def get_url(self, style: EmojiStyle = EmojiStyle.Apple) -> str:
        return f"https://emojicdn.elk.sh/{self.data}?style={style}"

    async def get_image(self, style: EmojiStyle = EmojiStyle.Apple) -> bytes:
        url = self.get_url(style)
        return await download_url(url)


class QQAvatar(ImageSource):
    qq: int

    def get_url(self, size: int = 640) -> str:
        return f"https://q1.qlogo.cn/g?b=qq&nk={self.qq}&s={size}"

    async def get_image(self) -> bytes:
        url = self.get_url(size=640)
        data = await download_url(url)
        if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
            url = self.get_url(size=100)
            data = await download_url(url)
        return data


class QQAvatarOpenId(ImageSource):
    appid: str
    user_openid: str

    def get_url(self) -> str:
        return f"https://q.qlogo.cn/qqapp/{self.appid}/{self.user_openid}/100"

    async def get_image(self) -> bytes:
        url = self.get_url()
        return await download_url(url)


class TelegramFile(ImageSource):
    token: str
    file_path: str

    def get_url(self, api_server: str = "https://api.telegram.org/") -> str:
        if Path(self.file_path).exists():
            return f"file://{self.file_path}"
        return f"{api_server}file/bot{self.token}/{self.file_path}"

    async def get_image(self, api_server: str = "https://api.telegram.org/") -> bytes:
        if Path(self.file_path).exists():
            return await anyio.Path(self.file_path).read_bytes()
        url = self.get_url(api_server)
        return await download_url(url)


class DiscordImageFormat(StrEnum):
    JPEG = "jpeg"
    PNG = "png"
    WebP = "webp"
    GIF = "gif"
    Lottie = "json"


class DiscordUserAvatar(ImageSource):
    # https://discord.com/developers/docs/reference#image-formatting

    user_id: int
    image_hash: str

    def get_url(
        self,
        base_url: str = "https://cdn.discordapp.com/",
        image_format: DiscordImageFormat = DiscordImageFormat.PNG,
        image_size: int = 1024,
    ) -> str:
        return f"{base_url}avatars/{self.user_id}/{self.image_hash}.{image_format}?size={image_size}"

    async def get_image(
        self,
        base_url: str = "https://cdn.discordapp.com/",
        image_format: DiscordImageFormat = DiscordImageFormat.PNG,
        image_size: int = 1024,
    ) -> bytes:
        url = self.get_url(base_url, image_format, image_size)
        return await download_url(url)
