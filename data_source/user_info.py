from aiocqhttp.exceptions import ActionFailed
from dataclasses import dataclass
from hoshino import HoshinoBot
from hoshino.typing import CQEvent
from typing import TypedDict


class UserInfo(TypedDict):
    name: str
    gender: str


@dataclass
class User:
    async def get_info(self) -> UserInfo:
        raise NotImplementedError


@dataclass
class QQUser(User):
    bot: HoshinoBot
    event: CQEvent
    user_id: int

    async def get_info(self) -> UserInfo:
        try:
            info = await self.bot.get_group_member_info(
                group_id=self.event.group_id, user_id=self.user_id
            )
        except ActionFailed:
            info = await self.bot.get_stranger_info(user_id=self.user_id)
        name = info.get("card", "") or info.get("nickname", "")
        gender = info.get("sex", "")
        return UserInfo(name=name, gender=gender)
