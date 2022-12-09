import hashlib
import json
import math
import os
import time
from enum import Enum
from io import BytesIO
from typing import Protocol, List, Union, Optional

import httpx
import pygtrie
from PIL.Image import Image as IMG  # noqa

from hoshino.typing import CQEvent
from . import config as petpet_config
from .download import get_image
from .models import Command
from .nonebot_plugin_imageutils import BuildImage, Text2Image


class TrieHandle:
    def __init__(self):
        self.trie = pygtrie.CharTrie()

    def add(self, prefix: str, handle: Command) -> bool:
        if prefix not in self.trie:
            self.trie[prefix] = handle
            return True
        else:
            return False

    def find(self, prefix: str):
        return self.trie.longest_prefix(prefix)

    def find_handle(self, event: CQEvent) -> Union[Command, None]:
        index = next((i for i, mes in enumerate(event.message) if mes.type == "text" and mes.data['text'].strip()), -1)

        if index == -1:
            # no text
            return None

        prefix = event.message[index].data["text"].lstrip()
        handle = self.find(prefix)
        if not handle:
            return None

        prefix = prefix[len(handle.key):]
        if not prefix and len(event.message) > 1:
            del event.message[index]
        else:
            event.message[index].data['text'] = prefix

        return handle.value


def save_gif(frames: List[IMG], duration: float) -> BytesIO:
    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration * 1000,
        loop=0,
        disposal=2,
        optimize=False
    )

    # 没有超出最大大小，直接返回
    nbytes = output.getbuffer().nbytes
    if nbytes <= petpet_config.petpet_gif_max_size * 10 ** 6:
        return output

    # 超出最大大小，帧数超出最大帧数时，缩减帧数
    n_frames = len(frames)
    gif_max_frames = petpet_config.petpet_gif_max_frames
    if n_frames > gif_max_frames:
        ratio = n_frames / gif_max_frames
        index = (int(i * ratio) for i in range(gif_max_frames))
        new_duration = duration * ratio
        new_frames = [frames[i] for i in index]
        return save_gif(new_frames, new_duration)

    # 超出最大大小，帧数没有超出最大帧数时，缩小尺寸
    new_frames = [
        frame.resize((int(frame.width * 0.9), int(frame.height * 0.9)))
        for frame in frames
    ]
    return save_gif(new_frames, duration)


class Maker(Protocol):
    async def __call__(self, img: BuildImage) -> BuildImage:
        ...


class GifMaker(Protocol):
    def __call__(self, i: int) -> Maker:
        ...


def get_avg_duration(image: IMG) -> float:
    if not getattr(image, "is_animated", False):
        return 0
    total_duration = 0
    for i in range(image.n_frames):
        image.seek(i)
        total_duration += image.info["duration"]
    return total_duration / image.n_frames


def split_gif(image: IMG) -> List[IMG]:
    frames: List[IMG] = []

    update_mode = "full"
    for i in range(image.n_frames):
        image.seek(i)
        if image.tile:  # type: ignore
            update_region = image.tile[0][1][2:]  # type: ignore
            if update_region != image.size:
                update_mode = "partial"
                break

    last_frame: Optional[IMG] = None
    for i in range(image.n_frames):
        image.seek(i)
        frame = image.copy()
        if update_mode == "partial" and last_frame:
            last_frame.copy().paste(frame)
        frames.append(frame)
        image.seek(0)
        if image.info.__contains__("transparency"):
            frames[0].info["transparency"] = image.info["transparency"]
    return frames


async def make_jpg_or_gif(
        img: BuildImage, func: Maker, keep_transparency: bool = False
) -> BytesIO:
    """
    制作静图或者动图
    :params
      * ``img``: 输入图片，如头像
      * ``func``: 图片处理函数，输入img，返回处理后的图片
      * ``keep_transparency``: 传入gif时，是否保留该gif的透明度
    """
    image = img.image
    if not getattr(image, "is_animated", False):
        return (await func(img)).save_jpg()
    else:
        frames = split_gif(image)
        duration = get_avg_duration(image) / 1000
        frames = [(await func(BuildImage(frame))).image for frame in frames]
        if keep_transparency:
            image.seek(0)
            if image.info.__contains__("transparency"):
                frames[0].info["transparency"] = image.info["transparency"]
        return save_gif(frames, duration)


class FrameAlignPolicy(Enum):
    """
    要叠加的gif长度大于基准gif时，是否延长基准gif长度以对齐两个gif
    """

    no_extend = 0
    """不延长"""
    extend_first = 1
    """延长第一帧"""
    extend_last = 2
    """延长最后一帧"""
    extend_loop = 3
    """以循环方式延长"""


async def make_gif_or_combined_gif(
        img: BuildImage,
        maker: GifMaker,
        frame_num: int,
        duration: float,
        frame_align: FrameAlignPolicy = FrameAlignPolicy.no_extend,
        input_based: bool = False,
        keep_transparency: bool = False,
) -> BytesIO:
    """
    使用静图或动图制作gif
    :params
      * ``img``: 输入图片，如头像
      * ``maker``: 图片处理函数生成，传入第几帧，返回对应的图片处理函数
      * ``frame_num``: 目标gif的帧数
      * ``duration``: 相邻帧之间的时间间隔，单位为秒
      * ``frame_align``: 要叠加的gif长度大于基准gif时，gif长度对齐方式
      * ``input_based``: 是否以输入gif为基准合成gif，默认为`False`，即以目标gif为基准
      * ``keep_transparency``: 传入gif时，是否保留该gif的透明度
    """
    image = img.image
    if not getattr(image, "is_animated", False):
        return save_gif([(await maker(i)(img)).image for i in range(frame_num)], duration)

    frame_num_in = image.n_frames
    duration_in = get_avg_duration(image) / 1000
    total_duration_in = frame_num_in * duration_in
    total_duration = frame_num * duration

    if input_based:
        frame_num_base = frame_num_in
        frame_num_fit = frame_num
        duration_base = duration_in
        duration_fit = duration
        total_duration_base = total_duration_in
        total_duration_fit = total_duration
    else:
        frame_num_base = frame_num
        frame_num_fit = frame_num_in
        duration_base = duration
        duration_fit = duration_in
        total_duration_base = total_duration
        total_duration_fit = total_duration_in

    frame_idxs: List[int] = list(range(frame_num_base))
    diff_duration = total_duration_fit - total_duration_base
    diff_num = int(diff_duration / duration_base)

    if diff_duration >= duration_base:
        if frame_align == FrameAlignPolicy.extend_first:
            frame_idxs = [0] * diff_num + frame_idxs

        elif frame_align == FrameAlignPolicy.extend_last:
            frame_idxs += [frame_num_base - 1] * diff_num

        elif frame_align == FrameAlignPolicy.extend_loop:
            frame_num_total = frame_num_base
            # 重复基准gif，直到两个gif总时长之差在1个间隔以内，或总帧数超出最大帧数
            while (
                    frame_num_total + frame_num_base <= petpet_config.petpet_gif_max_frames
            ):
                frame_num_total += frame_num_base
                frame_idxs += list(range(frame_num_base))
                multiple = round(frame_num_total * duration_base / total_duration_fit)
                if (
                        math.fabs(
                            total_duration_fit * multiple - frame_num_total * duration_base
                        )
                        <= duration_base
                ):
                    break

    frames: List[IMG] = []
    frame_idx_fit = 0
    time_start = 0
    for i, idx in enumerate(frame_idxs):
        while frame_idx_fit < frame_num_fit:
            if (
                    frame_idx_fit * duration_fit
                    <= i * duration_base - time_start
                    < (frame_idx_fit + 1) * duration_fit
            ):
                if input_based:
                    idx_in = idx
                    idx_maker = frame_idx_fit
                else:
                    idx_in = frame_idx_fit
                    idx_maker = idx

                func = maker(idx_maker)
                image.seek(idx_in)
                frames.append((await func(BuildImage(image.copy()))).image)
                break
            else:
                frame_idx_fit += 1
                if frame_idx_fit >= frame_num_fit:
                    frame_idx_fit = 0
                    time_start += total_duration_fit

    if keep_transparency:
        image.seek(0)
        if image.info.__contains__("transparency"):
            frames[0].info["transparency"] = image.info["transparency"]

    return save_gif(frames, duration)


async def translate(text: str, lang_from: str = "auto", lang_to: str = "zh") -> str:
    salt = str(round(time.time() * 1000))
    appid = petpet_config.baidu_trans_appid
    apikey = petpet_config.baidu_trans_apikey
    sign_raw = appid + text + salt + apikey
    sign = hashlib.md5(sign_raw.encode("utf8")).hexdigest()
    params = {
        "q": text,
        "from": lang_from,
        "to": lang_to,
        "appid": appid,
        "salt": salt,
        "sign": sign,
    }
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        result = resp.json()
    return result["trans_result"][0]["dst"]


async def help_image(all_commands: List[Command], group_id: int) -> BytesIO:
    def cmd_text(commands: List[Command], start: int = 1) -> str:
        texts = []
        banned_config_path = os.path.join(os.path.dirname(__file__), "banned.json")
        if not os.path.exists(banned_config_path):
            open(banned_config_path, "w")
        try:
            banned_command = json.load(open(banned_config_path, encoding="utf-8"))
        except json.decoder.JSONDecodeError:
            banned_command = {
                "global": []
            }
        for i, command in enumerate(commands):
            return_text = f"{i + start}. " + "/".join(command.keywords)
            if command.keywords[0] in banned_command["global"]:
                return_text = f"[color=lightgrey]{return_text}[/color]"
            if str(group_id) in banned_command:
                if command.keywords[0] in banned_command[str(group_id)]:
                    return_text = f"[color=lightgrey]{return_text}[/color]"
            texts.append(return_text)
        return "\n".join(texts)

    head_text = f"摸头等头像相关表情制作\n触发方式：{petpet_config.petpet_command_start}指令 + @user/qq/自己/图片\n支持的指令："
    head = Text2Image.from_text(head_text, 30, weight="bold").to_image(padding=(20, 10))
    imgs: List[IMG] = []
    col_num = 3
    num_per_col = math.ceil(len(all_commands) / col_num)
    for idx in range(0, len(all_commands), num_per_col):
        text = cmd_text(all_commands[idx: idx + num_per_col], start=idx + 1)
        imgs.append(Text2Image.from_bbcode_text(text, 30).to_image(padding=(20, 10)))
    w = max(sum((img.width for img in imgs)), head.width)
    h = head.height + max((img.height for img in imgs))
    frame = BuildImage.new("RGBA", (w, h), "white")
    frame.paste(head, alpha=True)
    current_w = 0
    for img in imgs:
        frame.paste(img, (current_w, head.height), alpha=True)
        current_w += img.width
    return frame.save_jpg()


async def load_image(name: str) -> BuildImage:
    image = await get_image(name)
    return BuildImage.open(BytesIO(image)).convert("RGBA")
