import asyncio
import copy
import hashlib
import os
import random
import traceback
from io import BytesIO
from itertools import chain
from pathlib import Path
from typing import List, Union, Tuple

from aiocqhttp.exceptions import ActionFailed
from meme_generator.download import check_resources
from meme_generator.exception import MemeGeneratorException
from meme_generator.meme import Meme
from meme_generator.utils import render_meme_list, MemeProperties
from pypinyin import Style, pinyin

from hoshino import HoshinoBot, Service, priv
from hoshino.aiorequests import run_sync_func
from hoshino.typing import CQEvent, MessageSegment, Message
from .config import memes_prompt_params_error, meme_command_start
from .data_source import ImageSource, UserInfo
from .depends import split_msg_v11
from .exception import NetworkError, PlatformUnsupportError
from .manager import ActionResult, MemeMode, meme_manager
from .utils import meme_info, bytesio2b64

memes_cache_dir = Path(os.path.join(os.path.dirname(__file__), "memes_cache_dir"))

sv_help = """
[表情包制作] 发送全部功能帮助
[表情帮助 + 表情] 发送选定表情功能帮助
[更新表情包制作] 更新表情包资源
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


@sv.on_fullmatch(["帮助头像表情包"])
async def bangzhu_text(bot: HoshinoBot, ev: CQEvent):
    await bot.send(ev, sv_help, at_sender=True)


def get_user_id(ev: CQEvent, permit: Union[int, None] = None):
    if permit is None or permit < 21:
        cid = f"{ev.self_id}_{ev.group_id}_{ev.user_id}"
    else:
        cid = f"{ev.self_id}_{ev.group_id}"
    return cid


@sv.on_fullmatch(("表情包制作", "头像表情包", "文字表情包"))
async def help_cmd(bot: HoshinoBot, ev: CQEvent):
    memes = sorted(
        meme_manager.memes,
        key=lambda meme: "".join(
            chain.from_iterable(pinyin(meme.keywords[0], style=Style.TONE3))
        ),
    )
    meme_list: List[Tuple[Meme, MemeProperties]] = []
    for single_meme in memes:
        disabled = not meme_manager.check(get_user_id(ev), single_meme.key)
        meme_list.append((single_meme, MemeProperties(disabled=disabled)))
    # cache rendered meme list
    meme_list_hashable = [
        (
            {
                "key": meme.key,
                "keywords": meme.keywords,
                "shortcuts": [
                    shortcut.humanized or shortcut.key for shortcut in meme.shortcuts
                ],
                "tags": sorted(meme.tags),
            },
            prop,
        )
        for meme, prop in meme_list
    ]
    meme_list_hash = hashlib.md5(str(meme_list_hashable).encode("utf8")).hexdigest()
    meme_list_cache_file = memes_cache_dir / f"{meme_list_hash}.jpg"
    if not meme_list_cache_file.exists():
        img: BytesIO = await run_sync_func(render_meme_list, meme_list)
        with open(meme_list_cache_file, "wb") as f:
            f.write(img.getvalue())
    else:
        img = BytesIO(meme_list_cache_file.read_bytes())

    msg = "触发方式：“关键词 + 图片/文字”\n发送 “表情详情 + 关键词” 查看表情参数和预览\n目前支持的表情列表："

    await bot.finish(ev, msg + MessageSegment.image(bytesio2b64(img)))


@sv.on_prefix(("表情帮助", "表情示例", "表情详情"))
async def info_cmd(bot: HoshinoBot, ev: CQEvent):
    meme_name = ev.message.extract_plain_text().strip()
    if not meme_name:
        await bot.finish(ev, "参数出错，请重新输入")

    meme, _ = meme_manager.find(meme_name)
    if not meme:
        await bot.send(ev, f"表情 {meme_name} 不存在！")
        return

    info = await meme_info(meme)
    await bot.finish(ev, info)


@sv.on_prefix("禁用表情")
async def block_cmd(bot: HoshinoBot, ev: CQEvent):
    meme_names = ev.message.extract_plain_text().strip().split()
    user_id: str = get_user_id(ev)
    if not meme_names:
        await bot.finish(ev, "参数出错，请重新输入")
    results = meme_manager.block(user_id, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 禁用成功"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 禁用失败"
        messages.append(message)
    await bot.finish(ev, "\n".join(messages))


@sv.on_prefix("启用表情")
async def unblock_cmd(bot: HoshinoBot, ev: CQEvent):
    meme_names = ev.message.extract_plain_text().strip().split()
    user_id: str = get_user_id(ev)
    if not meme_names:
        await bot.finish(ev, "参数出错，请重新输入")
    results = meme_manager.unblock(user_id, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 启用成功"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 启用失败"
        messages.append(message)
    await bot.finish(ev, "\n".join(messages))


@sv.on_prefix("全局禁用表情")
async def block_cmd_gl(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '此命令仅群管可用~')
    meme_names = ev.message.extract_plain_text().strip().split()
    if not meme_names:
        await bot.finish(ev, "参数出错，请重新输入")
    results = meme_manager.change_mode(MemeMode.WHITE, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 已设为白名单模式"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 设置失败"
        messages.append(message)
    await bot.finish(ev, "\n".join(messages))


@sv.on_prefix("全局启用表情")
async def unblock_cmd_gl(bot: HoshinoBot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '此命令仅群管可用~')
    meme_names = ev.message.extract_plain_text().strip().split()
    if not meme_names:
        await bot.finish(ev, "参数出错，请重新输入")
    results = meme_manager.change_mode(MemeMode.BLACK, meme_names)
    messages = []
    for name, result in results.items():
        if result == ActionResult.SUCCESS:
            message = f"表情 {name} 已设为黑名单模式"
        elif result == ActionResult.NOTFOUND:
            message = f"表情 {name} 不存在！"
        else:
            message = f"表情 {name} 设置失败"
        messages.append(message)
    await bot.finish(ev, "\n".join(messages))


async def process(
        bot: HoshinoBot,
        ev: CQEvent,
        meme: Meme,
        image_sources: List[ImageSource],
        texts: List[str],
        user_infos: List[UserInfo],
        args=None,
):
    if args is None:
        args = {}
    images: List[bytes] = []

    try:
        for image_source in image_sources:
            images.append(await image_source.get_image())
    except NotImplementedError:
        await bot.send(ev, "当前平台可能不支持获取图片")
        return
    except NetworkError:
        sv.logger.warning(traceback.format_exc())
        await bot.send(ev, "图片下载出错，请稍后再试")
        return

    args_user_infos = []
    for user_info in user_infos:
        name = user_info.user_displayname or user_info.user_name
        gender = str(user_info.user_gender)
        if gender not in ("male", "female"):
            gender = "unknown"
        args_user_infos.append({"name": name, "gender": gender})
    args["user_infos"] = args_user_infos

    try:
        result = await run_sync_func(meme, images=images, texts=texts, args=args)
    except MemeGeneratorException as e:
        await bot.send(ev, e.message)
        return

    try:
        await bot.send(ev, MessageSegment.image(bytesio2b64(result)))
    except ActionFailed:
        await bot.send(ev, "发送失败……消息可能被风控")


async def find_meme(
        trigger: str, raw_trigger: str, bot: HoshinoBot, ev: CQEvent
) -> Union[Union[Tuple[Meme, bool], Tuple[None, None]]]:
    if trigger == "随机表情":
        meme = random.choice(meme_manager.memes)
        uid = get_user_id(ev)
        if not meme_manager.check(uid, meme.key):
            await bot.send(ev, "随机到的表情不可用了捏qwq\n再试一次吧~")
            return None, None

        await bot.send(ev, f"随机到了【{meme.keywords[0]}】")
        return meme, False
    meme, regex = meme_manager.find(trigger)
    if meme is None:
        meme, regex = meme_manager.find(raw_trigger)
    return meme, regex


@sv.on_message('group')
async def handle(bot: HoshinoBot, ev: CQEvent):
    msg: Message = copy.deepcopy(ev.message)
    if not msg:
        sv.logger.debug("Empty msg, skip")
        return
    if msg[0].type == "reply":
        # 当回复目标是自己时，去除隐式at自己
        msg_id = msg[0].data["id"]
        source_msg = await bot.get_msg(message_id=int(msg_id))
        source_qq = str(source_msg['sender']['user_id'])
        # 隐式at和显示at之间还有一个文本空格
        while len(msg) > 1 and (
                msg[1].type == 'at' or msg[1].type == 'text' and msg[1].data['text'].strip() == ""):
            if msg[1].type == 'at' and msg[1].data['qq'] == source_qq \
                    or msg[1].type == 'text' and msg[1].data['text'].strip() == "":
                msg.pop(1)
            else:
                break
    for each_msg in msg:
        if not each_msg.type == "text":
            continue
        if not each_msg.data["text"].strip().startswith(meme_command_start):
            continue
        trigger = each_msg
        break
    else:
        for each_msg in msg:
            if not each_msg.type == "text":
                continue
            trigger = each_msg
            break
        else:
            sv.logger.debug("Empty trigger, skip")
            return

    uid = get_user_id(ev)
    try:
        trigger_text: str = trigger.data["text"].split()[0]
        raw_trigger_text: str = trigger.data["text"].strip()
    except IndexError:
        sv.logger.debug("Empty trigger, skip")
        return
    if not trigger_text.startswith(meme_command_start):
        # sv.logger.debug("Empty prefix, skip")
        return
    meme, is_regex = await find_meme(
        trigger_text.replace(meme_command_start, "").strip(),
        raw_trigger_text.replace(meme_command_start, "").strip(),
        bot, ev
    )
    if meme is None:
        sv.logger.debug("Empty meme, skip")
        return
    if not meme_manager.check(uid, meme.key):
        sv.logger.debug("Blocked meme, skip")
        return

    split_msg = await split_msg_v11(bot, ev, msg, meme, trigger, is_regex)
    if not split_msg:
        await bot.send(ev, f"表情 {meme.keywords[0]} 不存在！")
        return

    raw_texts: List[str] = split_msg["texts"]
    user_infos: List[UserInfo] = split_msg["user_infos"]
    image_sources: List[ImageSource] = split_msg["image_sources"]
    args: dict = split_msg["args"]
    texts = raw_texts if raw_texts else meme.params_type.default_texts

    await process(bot, ev, meme, image_sources, texts, user_infos, args)


@sv.on_fullmatch(("更新表情包制作", "更新头像表情包", "更新文字表情包"))
async def update_res(bot: HoshinoBot, ev: CQEvent):
    sv.logger.info("正在检查资源文件...")
    try:
        await asyncio.create_task(check_resources())
    except Exception as e:
        await bot.send(ev, f"更新资源出错：\n{e}")
        return
    await bot.send(ev, f"更新资源完成")
