from typing import Optional, Union
from aiocqhttp.exceptions import ActionFailed
from pydantic import BaseModel
from strenum import StrEnum
from hoshino import logger, HoshinoBot
from hoshino.typing import CQEvent
from .image_source import ImageSource, QQAvatar
from .utils import check_qq_number


class UserGender(StrEnum):
    male = "male"
    female = "female"
    unknown = "unknown"


class UserInfo(BaseModel):
    user_id: str
    user_name: str
    user_displayname: Optional[str] = None
    user_remark: Optional[str] = None
    user_avatar: Optional[ImageSource] = None
    user_gender: str = UserGender.unknown


def _sex_to_gender(sex: Optional[str]) -> UserGender:
    return (
        UserGender.male
        if sex == "male"
        else UserGender.female
        if sex == "female"
        else UserGender.unknown
    )


async def get_user_info(bot: HoshinoBot, event: CQEvent, user_id: Union[str, int]) -> Optional[UserInfo]:
    info = None
    user_id = str(user_id)
    if not check_qq_number(user_id):
        return None
    try:
        info = await bot.get_group_member_info(
            group_id=event.group_id, user_id=int(user_id)
        )
    except ActionFailed as e:
        logger.warning(f"Error calling get_group_member_info: {e}")

    if not info:
        try:
            info = await bot.get_stranger_info(user_id=int(user_id))
        except ActionFailed as e:
            logger.warning(f"Error calling get_stranger_info failed: {e}")

    if info:
        qq = info["user_id"]
        sex = info.get("sex")
        return UserInfo(
            user_id=str(qq),
            user_name=info.get("nickname", ""),
            user_displayname=info.get("card"),
            user_avatar=QQAvatar(qq=qq),
            user_gender=_sex_to_gender(sex),
        )

    return UserInfo(
        user_id=user_id,
        user_name="",
        user_avatar=QQAvatar(qq=int(user_id)),
    )
