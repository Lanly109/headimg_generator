from io import BytesIO
from dataclasses import dataclass, field
from typing import List, Tuple, Protocol
from .nonebot_plugin_imageutils import BuildImage


@dataclass
class UserInfo:
    def __init__(self, qq: str = "", group: str = "", img_url: str = "", bot_qq=""):
        self.qq: str = qq
        self.group: str = group
        self.name: str = ""
        self.gender: str = ""  # male 或 female 或 unknown
        self.img_url: str = img_url
        # self.img: IMG = Image.new("RGBA", (640, 640))
        self.bot_qq: str = bot_qq
        self.img: BuildImage = BuildImage.new("RGBA", (640, 640))


class Func(Protocol):
    async def __call__(self, users: List[UserInfo], **kwargs) -> BytesIO:
        ...


class FuncRandom(Protocol):
    async def __call__(self, commands: List, banned_command: dict, handle_group: str):
        ...


@dataclass
class Command:
    keywords: Tuple[str, ...]
    func: Func
    allow_gif: bool = False
    arg_num: int = 0
    prefix_keywords: list = field(default_factory=list),
    func_random: FuncRandom = None
