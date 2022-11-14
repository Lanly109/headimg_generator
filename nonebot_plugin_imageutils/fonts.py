import shutil
import traceback
from collections import namedtuple
from functools import lru_cache
from typing import Optional, Set, Iterator

import anyio
import httpx
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from fontTools.ttLib import TTFont
from hoshino import logger
from matplotlib.font_manager import FontManager, FontProperties
from matplotlib.ft2font import FT2Font

from .config import *
from .types import *

FONT_PATH = custom_font_path

font_manager = FontManager()


def local_fonts() -> Iterator[str]:
    if not FONT_PATH.exists():
        return
    for f in FONT_PATH.iterdir():
        if f.is_file() and f.suffix in [".otf", ".ttf", ".ttc", ".afm"]:
            yield f.name


def add_font_to_manager(path: Union[str, Path]):
    try:
        if isinstance(path, Path):
            path = str(path.resolve())
        font_manager.addfont(path)
    except OSError as exc:
        logger.warning(f"Failed to open font file {path}: {exc}")
    except Exception as exc:
        logger.warning(f"Failed to extract font properties from {path}: {exc}")


for fontname in local_fonts():
    add_font_to_manager(FONT_PATH / fontname)


class Font:
    def __init__(self, family: str, fontpath: Path, valid_size: Optional[int] = None):
        self.family = family
        """字体族名字"""
        self.path = fontpath.resolve()
        """字体文件路径"""
        self.valid_size = valid_size
        """某些字体不支持缩放，只能以特定的大小加载"""
        self._glyph_table: Set[int] = set()
        for table in TTFont(self.path, fontNumber=0)["cmap"].tables:  # type: ignore
            for key in table.cmap.keys():
                self._glyph_table.add(key)

    @classmethod
    @lru_cache()
    def find(
        cls,
        family: str,
        style: FontStyle = "normal",
        weight: FontWeight = "normal",
        fallback_to_default: bool = True,
    ) -> "Font":
        """查找插件路径和系统路径下的字体"""
        font = cls.find_special_font(family)
        if font:
            return font
        font = cls.find_local_font(family)
        if font:
            return font
        font = cls.find_pil_font(family)
        if font:
            return font
        filepath = font_manager.findfont(
            FontProperties(family, style=style, weight=weight),  # type: ignore
            fallback_to_default=fallback_to_default,
        )
        font = FT2Font(filepath)
        return cls(font.family_name, Path(font.fname))

    @classmethod
    def find_local_font(cls, name: str) -> Optional["Font"]:
        """查找插件路径下的字体"""
        for fontname in local_fonts():  # noqa
            if name == fontname or name == fontname.split(".")[0]:
                fontpath = FONT_PATH / fontname
                return cls(fontname, fontpath)

    @classmethod
    def find_pil_font(cls, name: str) -> Optional["Font"]:
        """通过 PIL ImageFont 查找系统字体"""
        try:
            font = ImageFont.truetype(name, 20)
            fontpath = Path(str(font.path))
            return cls(name, fontpath)
        except OSError:
            pass

    @classmethod
    def find_special_font(cls, family: str) -> Optional["Font"]:
        """查找特殊字体，主要是不可缩放的emoji字体"""

        SpecialFont = namedtuple("SpecialFont", ["family", "fontname", "valid_size"])
        SPECIAL_FONTS = {
            "Apple Color Emoji": SpecialFont(
                "Apple Color Emoji", "AppleColorEmoji.ttf", 137
            ),
            "Noto Color Emoji": SpecialFont(
                "Noto Color Emoji", "NotoColorEmoji.ttf", 109
            ),
        }

        if family in SPECIAL_FONTS:
            prop = SPECIAL_FONTS[family]
            fontname = prop.fontname  # noqa
            valid_size = prop.valid_size
            fontpath = None
            if fontname in local_fonts():
                fontpath = FONT_PATH / fontname
            else:
                try:
                    font = ImageFont.truetype(fontname, valid_size)
                    fontpath = Path(str(font.path))
                except OSError:
                    pass
            if fontpath:
                return cls(family, fontpath, valid_size)

    @lru_cache()
    def load_font(self, fontsize: int) -> FreeTypeFont:
        """以指定大小加载字体"""
        return ImageFont.truetype(str(self.path), fontsize, encoding="utf-8")

    @lru_cache()
    def has_char(self, char: str) -> bool:
        """检查字体是否支持某个字符"""
        return ord(char) in self._glyph_table


default_fallback_fonts = default_fallback_fonts


def get_proper_font(
    char: str,
    style: FontStyle = "normal",
    weight: FontWeight = "normal",
    fontname: Optional[str] = None,  # noqa
    fallback_fonts: List[str] = [],  # noqa
) -> Font:
    """
    获取合适的字体，将依次检查备选字体是否支持想要的字符

    :参数:
        * ``char``: 字符
        * ``style``: 字体样式，默认为 "normal"
        * ``weight``: 字体粗细，默认为 "normal"
        * ``fontname``: 可选，指定首选字体
        * ``fallback_fonts``: 可选，指定备选字体
    """
    fallback_fonts = fallback_fonts or default_fallback_fonts.copy()
    if fontname:
        fallback_fonts.insert(0, fontname)

    for family in fallback_fonts:
        try:
            font = Font.find(family, style, weight, fallback_to_default=False)
        except ValueError as e:
            logger.info(str(e))
            try:
                default_fallback_fonts.remove(family)
            except:  # noqa
                pass
            continue
        if font.has_char(char):
            return font

    logger.warning(f"在当前字体列表中找不到可以显示字符“{char}”的字体")
    return Font.find("serif", style, weight)


async def add_font(fontname: str, source: Union[str, Path]):  # noqa
    """通过字体文件路径或下载链接添加字体到插件路径"""
    fontpath = FONT_PATH / fontname
    if fontpath.exists():
        return
    FONT_PATH.mkdir(parents=True, exist_ok=True)
    try:
        if isinstance(source, Path):
            if source.is_file():
                shutil.copyfile(source, fontpath)
        else:
            await download_font(source, fontpath)
        add_font_to_manager(fontpath)
    except:  # noqa
        logger.warning(
            f"Add font {fontname} from {source} failed\n{traceback.format_exc()}"
        )
        fontpath.unlink(missing_ok=True)


async def download_font(url: str, fontpath: Path):
    """下载字体到插件路径"""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", url) as resp:
            logger.info(f"Begin to download font from {url}")
            async with await anyio.open_file(fontpath, "wb") as file:
                async for chunk in resp.aiter_bytes():
                    await file.write(chunk)
