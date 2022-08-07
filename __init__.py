import shlex
import base64
from typing import List
from .utils import help_image
from hoshino.typing import CQEvent, MessageSegment
from nonebot import on_startup
from hoshino import Service, priv, HoshinoBot
from .data_source import make_image, commands
from .download import DownloadError, ResourceError
from .models import UserInfo, Command

sv = Service('头像表情包', help_='''
![](https://s2.loli.net/2022/08/07/vwe2TlP8IWMJ3u4.jpg)
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

        # if event.reply:
        #     reply_imgs = event.reply.message["image"]
        #     for reply_img in reply_imgs:
        #         users.append(UserInfo(img_url=reply_img.data["url"]))

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

