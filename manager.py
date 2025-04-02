import re
from enum import IntEnum
from typing import Any, Dict, Tuple, Union, List

import yaml
from meme_generator.manager import get_memes
from meme_generator.meme import Meme
from pydantic import BaseModel

import hoshino
from .config import meme_disabled_list
import os

from .data_source.compat import PYDANTIC_V2

from pathlib import Path

config_file_path = Path(os.path.join(os.path.dirname(__file__), "config.yml"))


class MemeMode(IntEnum):
    BLACK = 0
    WHITE = 1


class MemeConfig(BaseModel):
    mode: int = MemeMode.BLACK.value
    white_list: List[str] = []
    black_list: List[str] = []

    class Config:
        use_enum_values = True


class ActionResult(IntEnum):
    SUCCESS = 0
    FAILED = 1
    NOTFOUND = 2


class MemeManager:
    def __init__(self, path: Path = config_file_path):
        self.__path = path
        self.__meme_list: Dict[str, MemeConfig] = {}
        self.memes = list(
            filter(
                lambda meme: meme.key not in meme_disabled_list,
                sorted(get_memes(), key=lambda meme: meme.key),
            )
        )
        self.__load()
        self.__dump()

    def block(self, user_id: str, meme_names=None) -> Dict[str, ActionResult]:
        if meme_names is None:
            meme_names = []
        results = {}
        for name in meme_names:
            meme, _ = self.find(name)
            if not meme:
                results[name] = ActionResult.NOTFOUND
                continue
            config = self.__meme_list[meme.key]
            if user_id not in config.black_list:
                config.black_list.append(user_id)
            if user_id in config.white_list:
                config.white_list.remove(user_id)
            results[name] = ActionResult.SUCCESS
        self.__dump()
        return results

    def unblock(self, user_id: str, meme_names=None) -> Dict[str, ActionResult]:
        if meme_names is None:
            meme_names = []
        results = {}
        for name in meme_names:
            meme, _ = self.find(name)
            if not meme:
                results[name] = ActionResult.NOTFOUND
                continue
            config = self.__meme_list[meme.key]
            if user_id not in config.white_list:
                config.white_list.append(user_id)
            if user_id in config.black_list:
                config.black_list.remove(user_id)
            results[name] = ActionResult.SUCCESS
        self.__dump()
        return results

    def change_mode(self, mode: int, meme_names=None) -> Dict[str, ActionResult]:
        if meme_names is None:
            meme_names = []
        results = {}
        for name in meme_names:
            meme, _ = self.find(name)
            if not meme:
                results[name] = ActionResult.NOTFOUND
                continue
            config = self.__meme_list[meme.key]
            config.mode = mode
            results[name] = ActionResult.SUCCESS
        self.__dump()
        return results

    def find(self, meme_name: str) -> Tuple[Union[Meme, None], bool]:
        for meme in self.memes:
            if meme_name.lower() == meme.key.lower():
                return meme, False
            for keyword in sorted(meme.keywords, reverse=True):
                if meme_name.lower() == keyword.lower():
                    return meme, False
            if meme.shortcuts:
                for shortcut in meme.shortcuts:
                    if re.search(shortcut.key, meme_name, re.IGNORECASE):
                        return meme, True
        return None, False

    def check(self, user_id: str, meme_key: str) -> bool:
        if meme_key not in self.__meme_list:
            return False
        config = self.__meme_list[meme_key]
        if config.mode == MemeMode.BLACK.value:
            if user_id in config.black_list:
                return False
            return True
        elif config.mode == MemeMode.WHITE.value:
            if user_id in config.white_list:
                return True
            return False
        return False

    def __load(self):
        raw_list: Dict[str, Any] = {}
        if self.__path.exists():
            with self.__path.open("r", encoding="utf-8") as f:
                try:
                    raw_list = yaml.safe_load(f)
                except UnicodeDecodeError:
                    hoshino.logger.warning("表情列表解析失败，将重新生成")
        try:
            meme_list = {
                name: MemeConfig.model_validate(config)
                for name, config in raw_list.items()
            }
        except AttributeError:
            meme_list = {}
            hoshino.logger.warning("表情列表解析失败，将重新生成")
        self.__meme_list = {meme.key: MemeConfig() for meme in self.memes}
        self.__meme_list.update(meme_list)

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        if PYDANTIC_V2:
            meme_list = {
                name: config.model_dump() for name, config in self.__meme_list.items()
            }
        else:
            meme_list = {
                name: config.dict() for name, config in self.__meme_list.items()
            }
        with self.__path.open("w", encoding="utf-8") as f:
            yaml.dump(meme_list, f, allow_unicode=True)


meme_manager = MemeManager()
