from typing import List

from meme_generator.meme import Meme
from hoshino import HoshinoBot
from hoshino.typing import CQEvent, MessageSegment, Message

from .config import (
    memes_use_sender_when_no_image,
    memes_use_default_when_no_text
)
from .data_source import (
    ImageSource,
    ImageUrl,
    User,
    QQUser,
    check_user_id,
    user_avatar,
)
from .utils import split_text


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


async def split_msg_v11(bot: HoshinoBot, event: CQEvent, meme: Meme) -> dict:
    texts: List[str] = []
    users: List[User] = []
    image_sources: List[ImageSource] = []

    msg = event.message
    restore_last_at_me_seg(event, msg)

    if event.reply:
        for msg_seg in event.reply.message["image"]:
            image_sources.append(ImageUrl(url=msg_seg.data["url"]))

    for msg_seg in msg:
        if msg_seg.type == "at":
            image_sources.append(user_avatar(str(msg_seg.data["qq"])))
            users.append(QQUser(bot, event, int(msg_seg.data["qq"])))

        elif msg_seg.type == "image":
            image_sources.append(ImageUrl(url=msg_seg.data["url"]))

        elif msg_seg.type == "text":
            raw_text = msg_seg.data["text"]
            split_msg = split_text(raw_text)
            split_msg.pop(0)
            for text in split_msg:
                if text.startswith("@") and check_user_id(text[1:]):
                    user_id = text[1:]
                    image_sources.append(user_avatar(user_id))
                    users.append(QQUser(bot, event, int(user_id)))

                elif text == "自己":
                    image_sources.append(
                        user_avatar(str(event.user_id))
                    )
                    users.append(QQUser(bot, event, event.user_id))

                else:
                    texts.append(text)

    # 当所需图片数为 2 且已指定图片数为 1 时，使用 发送者的头像 作为第一张图
    if meme.params_type.min_images == 2 and len(image_sources) == 1:
        image_sources.insert(0, user_avatar(str(event.user_id)))
        users.insert(0, QQUser(bot, event, event.user_id))

    # 当所需图片数为 1 且没有已指定图片时，使用发送者的头像
    if memes_use_sender_when_no_image and (
            meme.params_type.min_images == 1 and len(image_sources) == 0
    ):
        image_sources.append(user_avatar(str(event.user_id)))
        users.append(QQUser(bot, event, event.user_id))

    # 当所需文字数 >0 且没有输入文字时，使用默认文字
    if memes_use_default_when_no_text and (
            meme.params_type.min_texts > 0 and len(texts) == 0
    ):
        texts = meme.params_type.default_texts
    return {
        "texts": texts,
        "users": users,
        "image_sources": image_sources
    }