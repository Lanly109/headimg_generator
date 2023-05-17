from meme_generator import MemeArgsModel, MemeArgsParser, add_meme, MemeArgsType
from meme_generator.utils import make_jpg_or_gif, BuildImage, save_gif
from io import BytesIO
from PIL import Image, ImageOps, ImageFilter
from pydantic import Field
from typing import List

help_fliph = "水平翻转图片"
help_flipv = "垂直翻转图片"
help_binary = "图片转换为黑白"
help_rotate = "旋转图片，空格后带旋转角度（不能为0）"
help_invert = "图片做反相处理"
help_emboss = "图片转换为浮雕"
help_contour = "提取图片轮廓"
help_sharpen = "锐化图片"
help_reverse = "如果是动图，反转动图序列"

parser = MemeArgsParser(prefix_chars="-/")
parser.add_argument("--fliph", "/水平翻转", action="store_true", help=help_fliph)
parser.add_argument("--flipv", "/垂直翻转", action="store_true", help=help_flipv)
parser.add_argument("--binary", "/黑白", action="store_true", help=help_binary)
parser.add_argument("--rotate", "/旋转", action="store", help=help_rotate)
parser.add_argument("--invert", "/反相", action="store_true", help=help_invert)
parser.add_argument("--emboss", "/浮雕", action="store_true", help=help_emboss)
parser.add_argument("--contour", "/轮廓", action="store_true", help=help_contour)
parser.add_argument("--sharpen", "/锐化", action="store_true", help=help_sharpen)
parser.add_argument("--reverse", "/倒放", action="store_true", help=help_reverse)


class Model(MemeArgsModel):
    fliph: bool = Field(False, description=help_fliph)
    flipv: bool = Field(False, description=help_flipv)
    binary: bool = Field(False, description=help_binary)
    rotate: int = Field(90, description=help_rotate)
    invert: bool = Field(False, description=help_invert)
    emboss: bool = Field(False, description=help_emboss)
    contour: bool = Field(False, description=help_contour)
    sharpen: bool = Field(False, description=help_sharpen)
    reverse: bool = Field(False, description=help_reverse)


# noinspection PyUnusedLocal
def operations(images: List[BuildImage], texts: List[str], args) -> BytesIO:
    user_img = images[0]
    if args.reverse and getattr(user_img.image, "is_animated", False):
        duration = user_img.image.info["duration"] / 5000
        frames = []
        for i in range(user_img.image.n_frames):
            user_img.image.seek(i)
            frames.append(user_img.image.convert("RGB"))
        frames.reverse()
        return save_gif(frames, duration)

    def make(img: BuildImage) -> BuildImage:
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
            frame = ImageOps.invert(img.image)
        elif args.emboss:
            frame = img.filter(ImageFilter.EMBOSS)
        elif args.contour:
            frame = img.filter(ImageFilter.CONTOUR)
        elif args.sharpen:
            frame = img.filter(ImageFilter.SHARPEN)
        else:
            raise ValueError("旋转角度不能为0")
        return frame

    return make_jpg_or_gif(user_img, make)


add_meme(
    "operations",
    operations,
    min_images=1,
    max_images=1,
    args_type=MemeArgsType(
        parser, Model,
        [
            Model(fliph=False), Model(fliph=True),
            Model(flipv=False), Model(flipv=True),
            Model(binary=False), Model(binary=True),
            # Model(rotate=0), Model(rotate=90),
            Model(invert=False), Model(invert=True),
            Model(emboss=False), Model(emboss=True),
            Model(contour=False), Model(contour=True),
            Model(sharpen=False), Model(sharpen=True),
            Model(reverse=False), Model(reverse=True),
        ]
    ),
    keywords=["图片操作"],
)
