import base64
import re
import shlex
import traceback
from typing import List

from hoshino import Service, HoshinoBot
from hoshino.typing import CQEvent, MessageSegment
from nonebot import on_startup

from .data_source import make_image, commands
from .models import UserInfo
from .utils import help_image

sv = Service('头像表情包', help_='''
![](https://s2.loli.net/2022/09/18/zrhvqdCMDyOSpZj.jpg)
'''.strip(), enable_on_default=True, bundle='娱乐', visible = True)

@sv.on_fullmatch(("帮助头像表情包"))
async def help(bot, ev):
    img = await help_image(commands)
    base64_str = base64.b64encode(img.getvalue()).decode()
    img =  'base64://' + base64_str
    img = str(MessageSegment.image(img))
    await bot.send(ev, img)

def is_qq(msg: str):
    return msg.isdigit() and 11 >= len(msg) >= 5


async def get_user_info(bot: HoshinoBot, user: UserInfo):
    if not user.qq:
        return

    if user.group:
        info = await bot.get_group_member_info(
            group_id=int(user.group), user_id=int(user.qq)
        )
        user.name = info.get("card", "") or info.get("nickname", "")
        user.gender = info.get("sex", "")
    else:
        info = await bot.get_stranger_info(user_id=int(user.qq))
        user.name = info.get("nickname", "")
        user.gender = info.get("sex", "")


class Handler:
    def __init__(self, command):
        self.command = command

    async def handle(self, bot, event: CQEvent):
        users: List[UserInfo] = []
        args: List[str] = []
        msg = event.message

        # 由于使用的trigger是prefix，回复时无法捕捉trigger，不兼容
        # 回复前置处理
        # if msg[0].type == "reply":
        #     # 当回复目标是自己时，去除隐式at自己
        #     if msg[0].data["qq"] == str(event.user_id):
        #         msg.pop(1)
        #     # 因为回复别人会默认多加一个at，需要跳过回复附带的显式at
        #     elif len(msg) > 3:
        #         temp_msg = [msg[0]] + [each for each in msg[3:]]
        #         at_sb = MessageSegment.at(msg[0].data["qq"])
        #         if temp_msg[1] == at_sb:
        #             temp_msg.pop(1)
        #         msg = temp_msg
        #     # 手机版可以去掉显式at，因此直接去除隐式at即可
        #     else:
        #         at_sb = MessageSegment.at(msg[0].data["qq"])
        #         if msg[1] == at_sb:
        #             msg.pop(1)

        for msg_seg in msg:
            if msg_seg.type == "at":
                users.append(
                    UserInfo(
                        qq=msg_seg.data["qq"],
                        group=str(event.group_id)
                    )
                )
            elif msg_seg.type == "image":
                users.append(UserInfo(img_url=msg_seg.data["url"]))
            elif msg_seg.type == "reply":
                msg_id = msg_seg.data["id"]
                source_msg = await sv.bot.get_msg(message_id=int(msg_id))
                source_msg = source_msg["message"]
                if source_msg.startswith("[CQ:image,"):
                    url = re.search(r"url=(.+)", str(source_msg))
                    if not url:
                        continue
                    users.append(UserInfo(img_url=url.group(1)))
                else:
                    qq = msg_seg.data["qq"]
                    users.append(UserInfo(qq=qq, group=str(event.group_id)))
            elif msg_seg.type == "text":
                raw_text = str(msg_seg)
                try:
                    texts = shlex.split(raw_text)
                except:
                    texts = raw_text.split()
                for text in texts:
                    if is_qq(text):
                        users.append(UserInfo(qq=text))
                    elif text == "自己":
                        users.append(
                            UserInfo(
                                qq=str(event.user_id),
                                group=str(event.group_id)
                            )
                        )
                    else:
                        text = text.strip()
                        if text:
                            args.append(text)

        if len(args) > self.command.arg_num:
            return False
        if event.raw_message.find(f"[CQ:at,qq={str(event.self_id)}") != -1:
            users.append(UserInfo(qq=str(event.self_id), group=str(event.group_id)))
        if not users:
            return False

        sender = UserInfo(qq=str(event.user_id))
        await get_user_info(bot, sender)

        for user in users:
            await get_user_info(bot, user)

        try:
            img = await make_image(command = self.command, sender = sender, users = users, args = args)
            base64_str = base64.b64encode(img.getvalue()).decode()
            img =  'base64://' + base64_str
            img = str(MessageSegment.image(img))
        except Exception as e:
            print(traceback.format_exc())
            img = str(e)

        await bot.send(event, img)

@on_startup
async def register_handler():
    for command in commands:
        func = getattr(sv, "on_prefix")
        key = command.keywords
        func = func(key, only_to_me=False)
        func(Handler(command).handle)
    print('petpet register done.')
