import base64
import json
import os
import random
import shlex
import traceback
from io import BytesIO
from typing import List

import aiocqhttp
from nonebot import on_startup

from hoshino import HoshinoBot, Service, priv, Message
from hoshino.typing import CQEvent, MessageSegment
from .config import petpet_command_start as cmd_prefix
from .data_source import commands, make_image, SPECIAL_DETAIL_HELP
from .download import DownloadError, ResourceError
from .models import UserInfo
from .utils import help_image

banned_command = {
    "global": [],
}
banned_config_path = os.path.join(os.path.dirname(__file__), "banned.json")

sv_help = """
[头像表情包] 发送全部功能帮助
[头像详解] 发送特殊用法帮助 
"""

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
    def __init__(self, all_commands):
        self.commands = all_commands

    async def handle(self, bot, event: CQEvent):
        users: List[UserInfo] = []
        args: List[str] = []
        msg = event.message
        raw_msg = event.message.extract_plain_text().strip().split()
        if not raw_msg:
            raw_msg = [""]
        handle_group = str(event.group_id)
        for command in self.commands:
            if raw_msg[0] in command.prefix_keywords or raw_msg[0] == "随机表情":
                if raw_msg[0] == "随机表情" is not None:
                    command = random.choice(commands)
                    await bot.send(event, f"随机到了{command.keywords[0]}")
                # 回复前置处理
                if msg[0].type == "reply":
                    # 当回复目标是自己时，去除隐式at自己
                    msg_id = msg[0].data["id"]
                    source_msg = await sv.bot.get_msg(message_id=int(msg_id))
                    source_qq = str(source_msg['sender']['user_id'])
                    # 隐式at和显示at之间还有一个文本空格
                    while len(msg) > 1 and (
                            msg[1].type == 'at' or msg[1].type == 'text' and msg[1].data['text'].strip() == ""):
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
                        source_qq = str(source_msg['sender']['user_id'])
                        source_msg = source_msg["message"]
                        msgs = Message(source_msg)
                        get_img = False
                        for each_msg in msgs:
                            if each_msg.type == "image":
                                users.append(UserInfo(img_url=each_msg.data["url"]))
                                get_img = True
                        else:
                            if not get_img:
                                users.append(UserInfo(qq=source_qq))
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

                if handle_group not in banned_command:
                    banned_command[handle_group] = []
                if command.keywords[0] in banned_command["global"]:
                    sv.logger.info(f"{args[0].replace(cmd_prefix, '')}已被全局禁用")
                    return
                if command.keywords[0] in banned_command[handle_group]:
                    sv.logger.info(f"{args[0].replace(cmd_prefix, '')}已被本群禁用")
                    return
                sv.logger.info(f"Message {event.message_id} triggered {args[0].replace(cmd_prefix, '')}")
                args.pop(0)
                if len(args) > command.arg_num:
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
                    img = await make_image(command=command, sender=sender, users=users, args=args)
                    img = bytesio2b64(img)
                    img = str(MessageSegment.image(img))
                except Exception as e:
                    print(traceback.format_exc())
                    img = str(e)

                try:
                    await bot.send(event, img)
                except aiocqhttp.ActionFailed:
                    await bot.send(event, "发送失败……消息可能被风控")

                return


petpet_handler = None


@sv.on_prefix("启用表情")
async def enable_pic(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '此命令仅群管可用~')
    global banned_command
    args = ev.message.extract_plain_text().strip().split()
    group = str(ev.group_id)
    if not args:
        await bot.finish(ev, "请输入需要启用的表情")

    if "全局" in args:
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '此命令仅机器人管理员可用~')
        if not banned_command["global"]:
            await bot.finish(ev, "没有被禁用的表情")
        args.remove("全局")
        for arg in args:
            for command in commands:
                if arg in command.keywords:
                    banned_command["global"].remove(command.keywords[0])
                    if group in banned_command:
                        try:
                            banned_command[group].remove(command.keywords[0])
                        except ValueError:
                            pass
                    break
        else:
            with open(banned_config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(banned_command, indent=4, ensure_ascii=False))
            await bot.finish(ev, "完成")

    else:
        if group in banned_command:
            if not banned_command[group]:
                await bot.finish(ev, "本群没有被禁用的表情")
            for arg in args:
                for command in commands:
                    if arg in command.keywords:
                        banned_command[group].remove(command.keywords[0])
                        break
            else:
                with open(banned_config_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(banned_command, indent=4, ensure_ascii=False))
                await bot.finish(ev, "完成")
        else:
            banned_command[group] = []
            with open(banned_config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(banned_command, indent=4, ensure_ascii=False))
            await bot.finish(ev, "本群没有被禁用的表情")


@sv.on_prefix("禁用表情")
async def disable_pic(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '此命令仅群管可用~')
    global banned_command
    args = ev.message.extract_plain_text().strip().split()
    group = str(ev.group_id)
    if not args:
        await bot.finish(ev, "请输入需要禁用的表情")

    if "全局" in args:
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '此命令仅机器人管理员可用~')
        args.remove("全局")
        for arg in args:
            for command in commands:
                if arg in command.keywords:
                    banned_command["global"].append(command.keywords[0])
                    break
        else:
            with open(banned_config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(banned_command, indent=4, ensure_ascii=False))
            await bot.finish(ev, "完成")

    else:
        for arg in args:
            for command in commands:
                if arg in command.keywords:
                    if command.keywords[0] in banned_command["global"]:
                        sv.logger.info(f"{arg}已被全局禁用，跳过")
                        break
                    if group not in banned_command:
                        banned_command[group] = []
                    banned_command[group].append(command.keywords[0])
                    break
        else:
            with open(banned_config_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(banned_command, indent=4, ensure_ascii=False))
            await bot.finish(ev, "完成")


@on_startup
async def register_handler():
    global banned_command, petpet_handler
    if not os.path.exists(banned_config_path):
        open(banned_config_path, "w")
    try:
        banned_command = json.load(open(banned_config_path, encoding="utf-8"))
    except json.decoder.JSONDecodeError:
        banned_command = {
            "global": [],
        }

    func = getattr(sv, "on_message")
    func = func()

    for command in commands:
        command.prefix_keywords = [f"{cmd_prefix}{each_key}" for each_key in command.keywords]

    petpet_handler = Handler(commands)
    func(petpet_handler.handle)
    sv.logger.info('petpet register done.')
