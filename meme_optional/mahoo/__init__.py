import os
import random
import textwrap
from io import BytesIO
from pathlib import Path
from typing import List

import opencc
from PIL import ImageDraw, ImageFont, ImageSequence
from arclet.alconna import store_true
from meme_generator import (
    MemeArgsModel,
    add_meme,
    ParserOption,
    MemeArgsType,
)
from meme_generator.utils import (
    # make_jpg_or_gif,
    BuildImage,
    save_gif
)
from pydantic import Field

img_dir = Path(__file__).parent / "images"


class Model(MemeArgsModel):
    monster: bool = Field(False, description="召唤怪兽卡")
    magic: bool = Field(False, description="发动魔法卡")
    trap: bool = Field(False, description="放置陷阱卡")


parser_options = [
    ParserOption(names=["--monster", "召唤怪兽卡"], action=store_true, help="召唤怪兽卡"),
    ParserOption(names=["--magic", "发动魔法卡"], action=store_true, help="发动魔法卡"),
    ParserOption(names=["--trap", "放置陷阱卡"], action=store_true, help="放置陷阱卡"),
]


def mahoo(images: List[BuildImage], texts: List[str], args) -> BytesIO:
    cc = opencc.OpenCC('s2t')
    word1 = cc.convert(texts[0])
    word2 = cc.convert(texts[1])
    if len(word2) >= 138:
        word2 = word2[0:138]
    if args.monster:  # '怪兽':
        bg = BuildImage.open(img_dir / 'png (怪兽).jpg')
    elif args.magic:  # '魔法':
        bg = BuildImage.open(img_dir / 'png (魔法).jpg')
    elif args.trap == 3:  # '陷阱':
        bg = BuildImage.open(img_dir / 'png (陷阱).jpg')
    else:
        bg = BuildImage.open(img_dir / 'png (怪兽).jpg')
        args.monster = True
    new_frames = []
    gif = images[0]
    draw = ImageDraw.Draw(bg.image)
    font1 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 20)
    font2 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 14)
    draw.text((27, 24), word1, fill=(0, 0, 0), font=font1)
    # draw.text((27, 319), word2, fill=(0 , 0, 0), font=font2)
    if args.monster:  # '怪兽':
        font3 = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '华康隶书体W3.TTC'), 14)
        mom_atk = f'{int(random.uniform(1, 100)) * 100}'
        mom_def = f'{int(random.uniform(1, 100)) * 100}'
        draw.text((179, 380), mom_atk, fill=(0, 0, 0), font=font3)
        draw.text((238, 380), mom_def, fill=(0, 0, 0), font=font3)
    para = textwrap.wrap(word2, width=16)
    current_h, pad = 319, 0
    for line in para:
        _, top, _, bottom = draw.multiline_textbbox((0, 0), line, font=font2)
        h = bottom - top
        draw.text((27, current_h), line, fill=(0, 0, 0), font=font2)
        current_h += h + pad
    try:
        gif.image.seek(1)
    except EOFError:
        isanimated = False
    else:
        isanimated = True
    if isanimated:
        top_bgwidth = 219
        top_width = 219
        for frame in ImageSequence.Iterator(gif.image):
            new_bg = bg.image.copy()
            frame = frame.convert('RGB')
            new_bg.paste(frame.resize((top_width, top_bgwidth)),
                         (34, 77))
            new_frames.append(new_bg)
        return save_gif(new_frames, images[0].image.info["duration"] / 1000)
    else:
        new_bg = bg.copy()
        frame = gif.copy()
        top_bgwidth = 219
        top_width = 219
        new_bg.paste(frame.resize((top_width, top_bgwidth)), (34, 77))
        return new_bg.save_png()


add_meme(
    "mahoo",
    mahoo,
    min_texts=2,
    max_texts=2,
    min_images=1,
    max_images=1,
    keywords=["游戏王搓卡", "游戏王", "ygo"],
    default_texts=["怪兽", "普通怪兽"],
    args_type=MemeArgsType(
        args_model=Model,
        args_examples=[Model(monster=True), Model(magic=True)],
        parser_options=parser_options
    ),
)
