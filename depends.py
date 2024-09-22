import copy
import re
from typing import List, Dict, Any

from aiohttp import ClientSession
from meme_generator.meme import Meme

from hoshino import HoshinoBot
from hoshino.typing import CQEvent, MessageSegment, Message
from .config import (
    memes_use_sender_when_no_image,
    memes_use_default_when_no_text,
    meme_command_start
)
from .data_source import (
    ImageSource,
    UserInfo,
    check_qq_number,
    get_content,
    get_user_info,
)
from .utils import split_text


class AlcImage(ImageSource):
    url: str = ""

    async def get_image(self) -> bytes:
        if self.url:
            async with ClientSession() as session:
                result = await get_content(self.url, session)
            await session.close()
        else:
            raise NotImplementedError("image fetch not implemented")
        if isinstance(result, bytes):
            return result
        raise NotImplementedError("image fetch not implemented")


def restore_last_at_me_seg(event: CQEvent, msg: Message):
    def _is_at_me_seg(seg: MessageSegment):
        return seg.type == "at" and str(seg.data["qq"]) == str(event.self_id)

    if event.to_me:
        raw_msg = event.original_message
        i = -1
        last_msg_seg = raw_msg[i]
        if (
                last_msg_seg.type == "text"
                and not str(last_msg_seg.data["text"]).strip()
                and len(raw_msg) >= 2
        ):
            i -= 1
            last_msg_seg = raw_msg[i]

        if _is_at_me_seg(last_msg_seg):
            msg.append(last_msg_seg)


async def split_msg_v11(
        bot: HoshinoBot, event: CQEvent, msg: Message, meme: Meme, trigger: MessageSegment, is_regex: bool
) -> dict:
    texts: List[str] = []
    user_infos: List[UserInfo] = []
    image_sources: List[ImageSource] = []
    trigger_text_with_trigger: str = trigger.data["text"].strip()
    if is_regex:
        regex_args = []
        raw_args = ""
        for shortcut in meme.shortcuts:
            raw_text = trigger_text_with_trigger.replace(meme_command_start, "")
            regex_args = re.findall(shortcut.key, raw_text)
            if regex_args:
                regex_args = regex_args[0]
                break
        for each_arg in regex_args:
            raw_args += f"{each_arg} "
        trigger_text_seg = Message(f"{raw_args.strip()} ")
    else:
        for keyword in meme.keywords:
            if re.search(rf"^{meme_command_start}{keyword}", trigger_text_with_trigger):
                trigger_text = re.sub(rf"^{meme_command_start}{keyword}", "", trigger_text_with_trigger)
                trigger_text_seg = Message(f"{trigger_text.strip() }")
                break
        else:
            return {}
    msg.remove(trigger)
    msg: Message = trigger_text_seg.extend(msg)

    restore_last_at_me_seg(event, msg)

    for msg_seg in msg:
        if msg_seg.type == "at":
            if user_info := await get_user_info(bot, event, msg_seg.data["qq"]):
                if image_source := user_info.user_avatar:
                    image_sources.append(image_source)
                user_infos.append(user_info)

        elif msg_seg.type == "image":
            image_sources.append(
                AlcImage(url=msg_seg.data["url"])
            )

        elif msg_seg.type == "reply":
            msg_id = msg_seg.data["id"]
            source_msg = await bot.get_msg(message_id=int(msg_id))
            source_qq = str(source_msg['sender']['user_id'])
            source_msg = source_msg["message"]
            msgs = Message(source_msg)
            for each_msg in msgs:
                if each_msg.type == "image":
                    image_sources.append(AlcImage(url=each_msg.data["url"]))
                    break
            else:
                if user_info := await get_user_info(bot, event, source_qq):
                    if image_source := user_info.user_avatar:
                        image_sources.append(image_source)
                    user_infos.append(user_info)

        elif msg_seg.type == "text":
            raw_text = msg_seg.data["text"].strip()
            split_msg = split_text(raw_text)
            for text in split_msg:
                text = text.strip()
                user_id = text[1:]
                if text.startswith("@") and check_qq_number(user_id):
                    if user_info := await get_user_info(bot, event, user_id):
                        if image_source := user_info.user_avatar:
                            image_sources.append(image_source)
                        user_infos.append(user_info)

                elif text == "自己":
                    if user_info := await get_user_info(bot, event, event.user_id):
                        if image_source := user_info.user_avatar:
                            image_sources.append(image_source)
                        user_infos.append(user_info)

                elif text:
                    texts.append(text)

    args: Dict[str, Any] = {}
    if meme.params_type.args_type:
        raw_text_copy: List[str] = copy.deepcopy(texts)
        parser_options = meme.params_type.args_type.parser_options
        for i in range(len(raw_text_copy)):
            arg = raw_text_copy[i]
            if arg.startswith("/") or arg.startswith("--") or arg.startswith("-"):
                arg_key = arg.replace("/", "")
                for each_opt in parser_options:
                    if arg_key in each_opt.names:
                        for name in each_opt.names:
                            if name.startswith("--"):
                                real_arg_key = name.replace("--", "")
                                break
                        else:
                            await bot.send(event, f"参数错误！")
                            return {}
                        dest = each_opt.dest
                        action = each_opt.action
                        if action:
                            action_value = action.value
                        else:
                            try:
                                action_value = raw_text_copy[i + 1]
                                texts.remove(raw_text_copy[i + 1])
                            except IndexError:
                                await bot.send(event, f"参数错误！")
                                return {}
                        if dest:
                            args[dest] = action_value
                        else:
                            args[real_arg_key] = action_value
                        texts.remove(raw_text_copy[i])

    # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
    if meme.params_type.min_images == 2 and len(image_sources) == 1:
        if user_info := await get_user_info(bot, event, event.user_id):
            if image_source := user_info.user_avatar:
                image_sources.insert(0, image_source)
            user_infos.insert(0, user_info)

    # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
    if memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
    ):
        if user_info := await get_user_info(bot, event, event.user_id):
            if image_source := user_info.user_avatar:
                image_sources.append(image_source)
            user_infos.append(user_info)

    # 当所需文字数 > 0 且没有输入文字时，使用默认文字
    if memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
    ):
        texts = meme.params_type.default_texts

    # 当所需文字数 > 0 且没有输入文字，且仅存在一个参数时，使用默认文字
    # 为了防止误触发，参数必须放在最后一位，且该参数必须是bool，且参数前缀必须是--
    if memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 1 and texts[-1].startswith("--")
    ):
        temp = copy.deepcopy(meme.params_type.default_texts)
        temp.extend(texts)
        texts = temp
    return {
        "texts": texts,
        "user_infos": user_infos,
        "image_sources": image_sources,
        "args": args
    }
