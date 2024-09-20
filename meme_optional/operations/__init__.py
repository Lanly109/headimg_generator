from io import BytesIO
from typing import List
from arclet.alconna import store_true
from PIL import Image, ImageOps, ImageFilter
from meme_generator import (
    MemeArgsModel,
    MemeArgsType,
    add_meme,
    ParserOption,
    ParserArg
)
from meme_generator.utils import (
    make_jpg_or_gif,
    BuildImage,
    save_gif,
)
from pydantic import Field

help_fliph = "水平翻转图片"
help_flipv = "垂直翻转图片"
help_binary = "图片转换为黑白"
help_rotate = "旋转图片"
help_invert = "图片做反相处理"
help_emboss = "图片转换为浮雕"
help_contour = "提取图片轮廓"
help_sharpen = "锐化图片"
help_reverse = "如果是动图，反转动图序列"


class Model(MemeArgsModel):
    fliph: bool = Field(False, description=help_fliph)
    flipv: bool = Field(False, description=help_flipv)
    binary: bool = Field(False, description=help_binary)
    rotate: int = Field(0, description=help_rotate)
    invert: bool = Field(False, description=help_invert)
    emboss: bool = Field(False, description=help_emboss)
    contour: bool = Field(False, description=help_contour)
    sharpen: bool = Field(False, description=help_sharpen)
    reverse: bool = Field(False, description=help_reverse)


parser_options = [
    ParserOption(names=["--fliph", "水平翻转"], action=store_true, help=help_fliph),
    ParserOption(names=["--flipv", "垂直翻转"], action=store_true, help=help_flipv),
    ParserOption(names=["--binary", "黑白"], action=store_true, help=help_binary),
    ParserOption(names=["--rotate", "旋转"], args=[ParserArg(name="name", value="int", default=0)], help=help_rotate),
    ParserOption(names=["--invert", "反相"], action=store_true, help=help_invert),
    ParserOption(names=["--emboss", "浮雕"], action=store_true, help=help_emboss),
    ParserOption(names=["--contour", "轮廓"], action=store_true, help=help_contour),
    ParserOption(names=["--sharpen", "锐化"], action=store_true, help=help_sharpen),
    ParserOption(names=["--reverse", "倒放"], action=store_true, help=help_reverse)
]


# noinspection PyUnusedLocal
def operations(images: List[BuildImage], texts: List[str], args) -> BytesIO:
    user_img = images[0]
    if args.reverse and getattr(user_img.image, "is_animated", False):
        duration = user_img.image.info["duration"] / 1000
        frames = []
        for i in range(user_img.image.n_frames):
            user_img.image.seek(i)
            frames.append(user_img.image.convert("RGB"))
        frames.reverse()
        return save_gif(frames, duration)

    def make(imgs: List[BuildImage]) -> BuildImage:
        img = imgs[0]
        if args.fliph:
            frame = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif args.flipv:
            frame = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif args.binary:
            frame = img.convert("L")
        elif args.rotate:
            frame = img.rotate(angle=args.rotate)
        elif args.invert:
            img = img.convert("RGB")
            frame = BuildImage(ImageOps.invert(img.image))
        elif args.emboss:
            frame = img.filter(ImageFilter.EMBOSS)
        elif args.contour:
            frame = img.filter(ImageFilter.CONTOUR)
        elif args.sharpen:
            frame = img.filter(ImageFilter.SHARPEN)
        else:
            frame = img
        return frame

    return make_jpg_or_gif([user_img], make)


add_meme(
    "operations",
    operations,
    min_images=1,
    max_images=1,
    args_type=MemeArgsType(
        args_model=Model,
        args_examples=[Model(binary=True), Model(binary=False)],
        parser_options=parser_options
    ),
    keywords=["图片操作"],
)
