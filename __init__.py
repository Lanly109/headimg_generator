import base64
import copy
import shlex
import traceback
from typing import List
from io import BytesIO

from hoshino import Service, HoshinoBot, priv
from hoshino.typing import CQEvent, MessageSegment, Message
from nonebot import on_startup

from .data_source import make_image, commands
from .models import UserInfo
from .utils import help_image

sv_help = """
[头像表情包] 发送全部功能帮助
"""

cmd_prefix = ""

sv = Service(
    name="头像表情包",
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
    bundle='娱乐',  # 属于哪一类
    help_=sv_help  # 帮助文本
)


# 绕了一圈弄帮助图片
# 主要是因为图片制作得在插件加载完成后才能生成
@sv.on_fullmatch(["帮助头像表情包"])
async def bangzhu_text(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

def bytesio2b64(im: BytesIO) -> str:
    img = im.getvalue()
    return f"base64://{base64.b64encode(img).decode()}"

@sv.on_fullmatch("头像表情包")
async def bangzhu_img(bot: HoshinoBot, ev: CQEvent):
    im = await help_image(commands)
    await bot.send(ev, MessageSegment.image(bytesio2b64(im)))


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

        # 回复前置处理
        if msg[0].type == "reply":
            # 当回复目标是自己时，去除隐式at自己
            msg_id = msg[0].data["id"]
            source_msg = await sv.bot.get_msg(message_id=int(msg_id))
            source_qq = str(source_msg['sender']['user_id'])
            # 隐式at和显示at之间还有一个文本空格
            while len(msg) > 1 and (msg[1].type == 'at' or msg[1].type == 'text' and msg[1].data['text'].strip() == ""):
                if msg[1].type == 'at' and msg[1].data['qq'] == source_qq \
                        or msg[1].type == 'text' and msg[1].data['text'].strip() == "":
                    msg.pop(1)
                else:
                    break

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
                msgs = Message(source_msg)
                for each_msg in msgs:
                    if each_msg.type == "image":
                        users.append(UserInfo(img_url=each_msg.data["url"]))
            elif msg_seg.type == "text":
                raw_text = str(msg_seg)
                try:
                    texts = shlex.split(raw_text)
                except Exception as e:
                    sv.logger.warning(f"{e}")
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

        if not args or args[0] not in self.command.prefix_keywords:
            return False
        sv.logger.info(f"Message {event.message_id} triggered {args[0].replace(cmd_prefix, '')}")
        args.pop(0)

        if len(args) > self.command.arg_num:
            sv.logger.info("arg num exceed limit")
            return False
        if event.raw_message.find(f"[CQ:at,qq={str(event.self_id)}") != -1:
            users.append(UserInfo(qq=str(event.self_id), group=str(event.group_id)))
        if not users:
            users.append(UserInfo(qq=str(event.self_id), group=str(event.group_id)))

        sender = UserInfo(qq=str(event.user_id))
        await get_user_info(bot, sender)

        for user in users:
            await get_user_info(bot, user)

        try:
            img = await make_image(command=self.command, sender=sender, users=users, args=args)
            img = bytesio2b64(img)
            img = str(MessageSegment.image(img))
        except Exception as e:
            print(traceback.format_exc())
            img = str(e)

        await bot.send(event, img)


@on_startup
async def register_handler():
    for command in commands:
        func = getattr(sv, "on_keyword")
        command.prefix_keywords = [f"{cmd_prefix}{each_key}" for each_key in command.keywords]
        func = func(command.prefix_keywords, only_to_me=False)
        func(Handler(command).handle)
    sv.logger.info('petpet register done.')
