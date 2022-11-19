import emoji
import random
import re
from collections import namedtuple
from datetime import datetime
from typing import Dict

from PIL import ImageOps, ImageEnhance, ImageFilter

import hoshino
from .models import UserInfo
from .nonebot_plugin_imageutils import Text2Image
from .nonebot_plugin_imageutils.fonts import Font
from .nonebot_plugin_imageutils.gradient import LinearGradient, ColorStop
from .utils import *

TEXT_TOO_LONG = "文字太长了哦，改短点再试吧~"
NAME_TOO_LONG = "名字太长了哦，改短点再试吧~"
REQUIRE_NAME = "找不到名字，加上名字再试吧~"
REQUIRE_ARG = "该表情至少需要一个参数"


# noinspection PyUnusedLocal
async def operations(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    user_img = users[0].img
    help_msg = "支持的操作：水平翻转、垂直翻转、黑白、旋转、反相、浮雕、轮廓、锐化"
    if not args:
        raise ValueError(help_msg)

    op = args[0]
    if op == "倒放" and getattr(user_img, "is_animated", False):
        duration = user_img.image.info["duration"] / 1000
        frames = []
        for i in range(user_img.image.n_frames):
            user_img.image.seek(i)
            frames.append(user_img.image.convert("RGB"))
        frames.reverse()
        return save_gif(frames, duration)

    async def make(img: BuildImage) -> BuildImage:
        if op == "水平翻转":
            frame = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif op == "垂直翻转":
            frame = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif op == "黑白":
            frame = img.convert("L")
        elif op == "旋转":
            angle = int(args[1]) if args[1:] and args[1].isdigit() else 90
            frame = img.rotate(angle=int(angle))
        elif op == "反相":
            img = img.convert("RGB")
            frame = ImageOps.invert(img.image)
        elif op == "浮雕":
            frame = img.filter(ImageFilter.EMBOSS)
        elif op == "轮廓":
            frame = img.filter(ImageFilter.CONTOUR)
        elif op == "锐化":
            frame = img.filter(ImageFilter.SHARPEN)
        else:
            raise ValueError(help_msg)
        return frame

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def universal(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    user_img = users[0].img

    async def make(img: BuildImage) -> BuildImage:
        img = img.resize_width(500)
        frames: List[BuildImage] = [img]
        for arg in args:
            text_img = BuildImage(
                Text2Image.from_bbcode_text(arg, fontsize=45, align="center")
                .wrap(480)
                .to_image()
            )
            frames.append(text_img.resize_canvas((500, text_img.height)))

        frame = BuildImage.new(
            "RGBA", (500, sum((f.height for f in frames)) + 10), "white"
        )
        current_h = 0
        for f in frames:
            frame.paste(f, (0, current_h), alpha=True)
            current_h += f.height
        return frame

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def petpet(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    img = img.convert("RGBA").square()
    if args and "圆" in args:
        img = img.circle()

    frames: List[IMG] = []
    locs = [
        (14, 20, 98, 98),
        (12, 33, 101, 85),
        (8, 40, 110, 76),
        (10, 33, 102, 84),
        (12, 20, 98, 98),
    ]
    for i in range(5):
        hand = await load_image(f"petpet/{i}.png")
        frame = BuildImage.new("RGBA", hand.size, (255, 255, 255, 0))
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), alpha=True)
        frame.paste(hand, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.06)


# noinspection PyUnusedLocal
async def kiss(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    if len(users) >= 2:
        self_img = users[0].img
        user_img = users[1].img
    else:
        self_img = sender.img
        user_img = users[0].img
    self_head = self_img.convert("RGBA").circle().resize((40, 40))
    user_head = user_img.convert("RGBA").circle().resize((50, 50))
    # fmt: off
    user_locs = [
        (58, 90), (62, 95), (42, 100), (50, 100), (56, 100), (18, 120), (28, 110),
        (54, 100), (46, 100), (60, 100), (35, 115), (20, 120), (40, 96)
    ]
    self_locs = [
        (92, 64), (135, 40), (84, 105), (80, 110), (155, 82), (60, 96), (50, 80),
        (98, 55), (35, 65), (38, 100), (70, 80), (84, 65), (75, 65)
    ]
    # fmt: on
    frames: List[IMG] = []
    for i in range(13):
        frame = await load_image(f"kiss/{i}.png")
        frame.paste(user_head, user_locs[i], alpha=True)
        frame.paste(self_head, self_locs[i], alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def rub(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    if len(users) >= 2:
        self_img = users[0].img
        user_img = users[1].img
    else:
        self_img = sender.img
        user_img = users[0].img
    # fmt: off
    self_head = self_img.convert("RGBA").circle()
    user_head = user_img.convert("RGBA").circle()
    # fmt: off
    user_locs = [
        (39, 91, 75, 75), (49, 101, 75, 75), (67, 98, 75, 75),
        (55, 86, 75, 75), (61, 109, 75, 75), (65, 101, 75, 75)
    ]
    self_locs = [
        (102, 95, 70, 80, 0), (108, 60, 50, 100, 0), (97, 18, 65, 95, 0),
        (65, 5, 75, 75, -20), (95, 57, 100, 55, -70), (109, 107, 65, 75, 0)
    ]
    # fmt: on
    frames: List[IMG] = []
    for i in range(6):
        frame = await load_image(f"rub/{i}.png")
        x, y, w, h = user_locs[i]
        frame.paste(user_head.resize((w, h)), (x, y), alpha=True)
        x, y, w, h, angle = self_locs[i]
        frame.paste(
            self_head.resize((w, h)).rotate(angle, expand=True), (x, y), alpha=True
        )
        frames.append(frame.image)
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def play(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [
        (180, 60, 100, 100), (184, 75, 100, 100), (183, 98, 100, 100),
        (179, 118, 110, 100), (156, 194, 150, 48), (178, 136, 122, 69),
        (175, 66, 122, 85), (170, 42, 130, 96), (175, 34, 118, 95),
        (179, 35, 110, 93), (180, 54, 102, 93), (183, 58, 97, 92),
        (174, 35, 120, 94), (179, 35, 109, 93), (181, 54, 101, 92),
        (182, 59, 98, 92), (183, 71, 90, 96), (180, 131, 92, 101)
    ]
    # fmt: on
    raw_frames: List[BuildImage] = [(await load_image(f"play/{i}.png")) for i in range(38)]
    img_frames: List[BuildImage] = []
    for i in range(len(locs)):
        frame = raw_frames[i]
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        img_frames.append(frame)
    frames = (
            img_frames[0:12]
            + img_frames[0:12]
            + img_frames[0:8]
            + img_frames[12:18]
            + raw_frames[18:38]
    )
    frames = [frame.image for frame in frames]
    return save_gif(frames, 0.06)


# noinspection PyUnusedLocal
async def pat(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    locs = [(11, 73, 106, 100), (8, 79, 112, 96)]
    img_frames: List[IMG] = []
    for i in range(10):
        frame = await load_image(f"pat/{i}.png")
        x, y, w, h = locs[1] if i == 2 else locs[0]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        img_frames.append(frame.image)
    # fmt: off
    seq = [0, 1, 2, 3, 1, 2, 3, 0, 1, 2, 3, 0, 0, 1, 2, 3, 0, 0, 0, 0, 4, 5, 5, 5, 6, 7, 8, 9]
    # fmt: on
    frames = [img_frames[n] for n in seq]
    return save_gif(frames, 0.085)


# noinspection PyUnusedLocal
async def rip(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    if len(users) >= 2:
        frame = await load_image("rip/1.png")
        self_img = users[0].img
        user_img = users[1].img
    else:
        frame = await load_image("rip/0.png")
        self_img = sender.img
        user_img = users[0].img

    if "滑稽" in args:
        _rip = await load_image("rip/0.png")

    user_img = user_img.convert("RGBA").square().resize((385, 385))
    if self_img:
        self_img = self_img.convert("RGBA").square().resize((230, 230))
        frame.paste(self_img, (408, 418), below=True)
    frame.paste(user_img.rotate(24, expand=True), (-5, 355), below=True)
    frame.paste(user_img.rotate(-11, expand=True), (649, 310), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def rip_angrily(users: List[UserInfo], **kwargs):
    img = users[0].img
    img = img.convert("RGBA").square().resize((105, 105))
    frame = await load_image("rip_angrily/0.png")
    frame.paste(img.rotate(-24, expand=True), (18, 170), below=True)
    frame.paste(img.rotate(24, expand=True), (163, 65), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def throw(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").circle().rotate(random.randint(1, 360)).resize((143, 143))
    frame = await load_image("throw/0.png")
    frame.paste(img, (15, 178), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def throw_gif(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").circle()
    locs = [
        [(32, 32, 108, 36)],
        [(32, 32, 122, 36)],
        [],
        [(123, 123, 19, 129)],
        [(185, 185, -50, 200), (33, 33, 289, 70)],
        [(32, 32, 280, 73)],
        [(35, 35, 259, 31)],
        [(175, 175, -50, 220)],
    ]
    frames: List[IMG] = []
    for i in range(8):
        frame = await load_image(f"throw_gif/{i}.png")
        for w, h, x, y in locs[i]:
            frame.paste(img.resize((w, h)), (x, y), alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.08)


# noinspection PyUnusedLocal
async def crawl(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    no_edit = False
    if users[0].qq == users[0].bot_qq:
        no_edit = True

    img = img.circle().resize((100, 100))
    crawl_total = 92
    crawl_num = random.randint(1, crawl_total)
    if args and args[0].isdigit() and 1 <= int(args[0]) <= crawl_total:
        crawl_num = int(args[0])
    frame = await load_image(f"crawl/{crawl_num:02d}.jpg")
    if not no_edit:
        frame.paste(img, (0, 400), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def support(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((815, 815)).rotate(23, expand=True)
    frame = await load_image("support/0.png")
    frame.paste(img, (-172, -17), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def always(users: List[UserInfo], **kwargs) -> BytesIO:
    user_img = users[0].img

    async def make(img: BuildImage) -> BuildImage:
        img_big = img.resize_width(500)
        img_small = img.resize_width(100)
        h1 = img_big.height
        h2 = max(img_small.height, 80)
        frame = BuildImage.new("RGBA", (500, h1 + h2 + 10), "white")
        frame.paste(img_big, alpha=True).paste(
            img_small, (290, h1 + 5 + (h2 - img_small.height) // 2), alpha=True
        )
        frame.draw_text(
            (20, h1 + 5, 280, h1 + h2 + 5), "要我一直", halign="right", max_fontsize=60
        )
        frame.draw_text(
            (400, h1 + 5, 480, h1 + h2 + 5), "吗", halign="left", max_fontsize=60
        )
        return frame

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def always_always(users: List[UserInfo], **kwargs):
    user_img = users[0].img
    tmp = user_img.convert("RGBA").resize_width(500)
    img_h = tmp.height
    text_h = tmp.resize_width(100).height + tmp.resize_width(20).height + 10
    text_h = max(text_h, 80)
    frame_h = img_h + text_h
    text_frame = BuildImage.new("RGBA", (500, frame_h), "white")
    text_frame.draw_text(
        (0, img_h, 280, frame_h), "要我一直", halign="right", max_fontsize=60
    ).draw_text((400, img_h, 500, frame_h), "吗", halign="left", max_fontsize=60)

    frame_num = 20
    coeff = 5 ** (1 / frame_num)

    def maker(i: int) -> Maker:
        async def make(img: BuildImage) -> BuildImage:
            img = img.resize_width(500)
            base_frame = text_frame.copy().paste(img, alpha=True)
            frame = BuildImage.new("RGBA", base_frame.size, "white")
            r = coeff ** i
            for _ in range(4):
                x = int(358 * (1 - r))
                y = int(frame_h * (1 - r))
                w = int(500 * r)
                h = int(frame_h * r)
                frame.paste(base_frame.resize((w, h)), (x, y))
                r /= 5
            return frame

        return make

    return await make_gif_or_combined_gif(
        user_img, maker, frame_num, 0.08, FrameAlignPolicy.extend_loop
    )


# noinspection PyUnusedLocal
async def loading(users: List[UserInfo], **kwargs) -> BytesIO:
    user_img = users[0].img

    img_big = user_img.convert("RGBA").resize_width(500)
    img_big = img_big.filter(ImageFilter.GaussianBlur(radius=3))
    h1 = img_big.height
    mask = BuildImage.new("RGBA", img_big.size, (0, 0, 0, 64))
    icon = await load_image("loading/icon.png")
    img_big.paste(mask, alpha=True).paste(icon, (200, int(h1 / 2) - 50), alpha=True)

    async def make(img: BuildImage) -> BuildImage:
        img_small = img.resize_width(100)
        h2 = max(img_small.height, 80)
        frame = BuildImage.new("RGBA", (500, h1 + h2 + 10), "white")
        frame.paste(img_big, alpha=True).paste(
            img_small, (100, h1 + 5 + (h2 - img_small.height) // 2), alpha=True
        )
        frame.draw_text(
            (210, h1 + 5, 480, h1 + h2 + 5), "不出来", halign="left", max_fontsize=60
        )
        return frame

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def turn(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").circle()
    frames: List[IMG] = []
    for i in range(0, 360, 10):
        frame = BuildImage.new("RGBA", (250, 250), "white")
        frame.paste(img.rotate(i).resize((250, 250)), alpha=True)
        frames.append(frame.image)
    if random.randint(0, 1):
        frames.reverse()
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def littleangel(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    img_w, img_h = img.convert("RGBA").resize_width(500).size
    frame = BuildImage.new("RGBA", (600, img_h + 230), "white")
    text = "非常可爱！简直就是小天使"
    frame.draw_text(
        (10, img_h + 120, 590, img_h + 185), text, max_fontsize=48, weight="bold"
    )

    ta = "他" if users[0].gender == "male" else "她"
    text = f"{ta}没失踪也没怎么样  我只是觉得你们都该看一下"
    frame.draw_text(
        (20, img_h + 180, 580, img_h + 215), text, max_fontsize=26, weight="bold"
    )

    name = args[0] if args else random.choice([users[0].name, ta])
    text = f"请问你们看到{name}了吗?"
    try:
        frame.draw_text(
            (20, 0, 580, 110), text, max_fontsize=70, min_fontsize=25, weight="bold"
        )
    except ValueError:
        raise ValueError(NAME_TOO_LONG)

    async def make(make_img: BuildImage) -> BuildImage:
        make_img = make_img.resize_width(500)
        return frame.copy().paste(make_img, (int(300 - img_w / 2), 110), alpha=True)

    return await make_jpg_or_gif(img, make)


# noinspection PyUnusedLocal
async def dont_touch(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((170, 170))
    frame = await load_image("dont_touch/0.png")
    frame.paste(img, (23, 231), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def alike(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((90, 90))
    frame = await load_image("alike/0.png")
    frame.paste(img, (131, 14), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def roll(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((210, 210))
    # fmt: off
    locs = [
        (87, 77, 0), (96, 85, -45), (92, 79, -90), (92, 78, -135),
        (92, 75, -180), (92, 75, -225), (93, 76, -270), (90, 80, -315)
    ]
    # fmt: on
    frames: List[IMG] = []
    for i in range(8):
        frame = await load_image(f"roll/{i}.png")
        x, y, a = locs[i]
        frame.paste(img.rotate(a), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.1)


# noinspection PyUnusedLocal
async def play_game(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    frame = await load_image("play_game/1.png")
    text = args[0] if args else "来玩休闲游戏啊"

    try:
        frame.draw_text(
            (20, frame.height - 70, frame.width - 20, frame.height),
            text,
            max_fontsize=40,
            min_fontsize=25,
            stroke_fill="white",
            stroke_ratio=0.06
        )
    except Exception as e:
        hoshino.logger.warning(f"{e}")
        raise ValueError(TEXT_TOO_LONG)

    async def make(make_img: BuildImage) -> BuildImage:
        points = ((0, 5), (227, 0), (216, 150), (0, 165))
        screen = make_img.resize((220, 160), keep_ratio=True).perspective(points)
        return frame.copy().paste(screen.rotate(9, expand=True), (161, 117), below=True)

    return await make_jpg_or_gif(img, make)


# noinspection PyUnusedLocal
async def worship(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA")
    points = ((0, -30), (135, 17), (135, 145), (0, 140))
    painting = img.square().resize((150, 150)).perspective(points)
    frames: List[IMG] = []
    for i in range(10):
        frame = await load_image(f"worship/{i}.png")
        frame.paste(painting, below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.04)


# noinspection PyUnusedLocal
async def eat(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((34, 34))
    frames = []
    for i in range(3):
        frame = await load_image(f"eat/{i}.png")
        frame.paste(img, (2, 38), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def bite(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    frames: List[IMG] = []
    # fmt: off
    locs = [
        (90, 90, 105, 150), (90, 83, 96, 172), (90, 90, 106, 148),
        (88, 88, 97, 167), (90, 85, 89, 179), (90, 90, 106, 151)
    ]
    # fmt: on
    for i in range(6):
        frame = await load_image(f"bite/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    for i in range(6, 16):
        frame = await load_image(f"bite/{i}.png")
        frames.append(frame.image)
    return save_gif(frames, 0.07)


# noinspection PyUnusedLocal
async def police(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((245, 245))
    frame = await load_image("police/0.png")
    frame.paste(img, (224, 46), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def police1(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((60, 75), keep_ratio=True).rotate(16, expand=True)
    frame = await load_image("police/1.png")
    frame.paste(img, (37, 291), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def ask(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    img = img.resize_width(640)
    img_w, img_h = img.size
    gradient_h = 150
    gradient = LinearGradient(
        (0, 0, 0, gradient_h),
        [ColorStop(0, (0, 0, 0, 220)), ColorStop(1, (0, 0, 0, 30))],
    )
    gradient_img = gradient.create_image((img_w, gradient_h))
    mask = BuildImage.new("RGBA", img.size)
    mask.paste(gradient_img, (0, img_h - gradient_h), alpha=True)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(mask, alpha=True)

    name = (args[0] if args else "") or users[0].name
    ta = "他" if users[0].gender == "male" else "她"
    if not name:
        raise ValueError(REQUIRE_NAME)

    start_w = 20
    start_h = img_h - gradient_h + 5
    text_img1 = Text2Image.from_text(
        f"{name}", 28, fill="orange", weight="bold"
    ).to_image()
    text_img2 = Text2Image.from_text(
        f"{name}不知道哦。", 28, fill="white", weight="bold"
    ).to_image()
    img.paste(
        text_img1,
        (start_w + 40 + (text_img2.width - text_img1.width) // 2, start_h),
        alpha=True,
    )
    img.paste(
        text_img2,
        (start_w + 40, start_h + text_img1.height + 10),
        alpha=True,
    )

    line_h = start_h + text_img1.height + 5
    img.draw_line(
        (start_w, line_h, start_w + text_img2.width + 80, line_h),
        fill="orange",
        width=2,
    )

    sep_w = 30
    sep_h = 80
    frame = BuildImage.new("RGBA", (img_w + sep_w * 2, img_h + sep_h * 2), "white")
    try:
        frame.draw_text(
            (sep_w, 0, img_w + sep_w, sep_h),
            f"让{name}告诉你吧",
            max_fontsize=35,
            halign="left",
        )
        frame.draw_text(
            (sep_w, img_h + sep_h, img_w + sep_w, img_h + sep_h * 2),
            f"啊这，{ta}说不知道",
            max_fontsize=35,
            halign="left",
        )
    except ValueError:
        raise ValueError(NAME_TOO_LONG)
    frame.paste(img, (sep_w, sep_h))
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def prpr(users: List[UserInfo], **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = await load_image("prpr/0.png")

    async def make(img: BuildImage) -> BuildImage:
        points = ((0, 19), (236, 0), (287, 264), (66, 351))
        screen = img.resize((330, 330), keep_ratio=True).perspective(points)
        return frame.copy().paste(screen, (56, 284), below=True)

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def twist(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((78, 78))
    # fmt: off
    locs = [
        (25, 66, 0), (25, 66, 60), (23, 68, 120),
        (20, 69, 180), (22, 68, 240), (25, 66, 300)
    ]
    # fmt: on
    frames: List[IMG] = []
    for i in range(5):
        frame = await load_image(f"twist/{i}.png")
        x, y, a = locs[i]
        frame.paste(img.rotate(a), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.1)


# noinspection PyUnusedLocal
async def wallpaper(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((515, 383), keep_ratio=True)
    frames: List[IMG] = []
    for i in range(8):
        frames.append((await load_image(f"wallpaper/{i}.png")).image)
    for i in range(8, 20):
        frame = await load_image(f"wallpaper/{i}.png")
        frame.paste(img, (176, -9), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.07)


# noinspection PyUnusedLocal
async def china_flag(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    frame = await load_image("china_flag/0.png")
    frame.paste(img.convert("RGBA").resize(frame.size, keep_ratio=True), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def make_friend(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img.convert("RGBA")
    bg = await load_image("make_friend/0.png")
    frame = img.resize_width(1000)
    frame.paste(
        img.resize_width(250).rotate(9, expand=True),
        (743, frame.height - 155),
        alpha=True,
    )
    frame.paste(
        img.square().resize((55, 55)).rotate(9, expand=True),
        (836, frame.height - 278),
        alpha=True,
    )
    frame.paste(bg, (0, frame.height - 1000), alpha=True)

    name = args[0] if args else users[0].name
    if not name:
        raise ValueError(REQUIRE_NAME)

    text_img = Text2Image.from_text(name, 20, fill="white").to_image()
    if text_img.width > 230:
        raise ValueError(NAME_TOO_LONG)

    text_img = BuildImage(text_img).rotate(9, expand=True)
    frame.paste(text_img, (710, frame.height - 308), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def back_to_work(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    frame = await load_image("back_to_work/0.png")
    img = img.convert("RGBA").resize((220, 310), keep_ratio=True, direction="north")
    frame.paste(img.rotate(25, expand=True), (56, 32), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def perfect(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    frame = await load_image("perfect/0.png")
    img = img.convert("RGBA").resize((310, 460), keep_ratio=True, inside=True)
    frame.paste(img, (313, 64), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def follow(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img

    img = img.circle().resize((200, 200))

    ta = "女同" if users[0].gender == "female" else "男同"
    name = args[0] if args else random.choice([users[0].name, ta])
    name_img = Text2Image.from_text(name, 60).to_image()
    follow_img = Text2Image.from_text("关注了你", 60, fill="grey").to_image()
    text_width = max(name_img.width, follow_img.width)
    if text_width >= 1000:
        raise ValueError(NAME_TOO_LONG)

    frame = BuildImage.new("RGBA", (300 + text_width + 50, 300), (255, 255, 255, 0))
    frame.paste(img, (50, 50), alpha=True)
    frame.paste(name_img, (300, 135 - name_img.height), alpha=True)
    frame.paste(follow_img, (300, 145), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def my_friend(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    if not args:
        raise ValueError(REQUIRE_ARG)
    elif len(args) <= 1:
        name = users[0].name or "朋友"
        texts = args
    else:
        name = args[0] or "朋友"
        texts = args[1:]

    img = img.convert("RGBA").circle().resize((100, 100))

    name_img = Text2Image.from_text(name, 25, fill="#868894").to_image()
    name_w, name_h = name_img.size
    if name_w >= 600:
        raise ValueError(NAME_TOO_LONG)

    corner1 = await load_image("my_friend/corner1.png")
    corner2 = await load_image("my_friend/corner2.png")
    corner3 = await load_image("my_friend/corner3.png")
    corner4 = await load_image("my_friend/corner4.png")
    label = await load_image("my_friend/label.png")

    async def make_dialog(text: str) -> BuildImage:
        text_img = Text2Image.from_text(text, 40).wrap(600).to_image()
        text_w, text_h = text_img.size
        box_w = max(text_w, name_w + 15) + 140
        box_h = max(text_h + 103, 150)
        box = BuildImage.new("RGBA", (box_w, box_h))
        box.paste(corner1, (0, 0))
        box.paste(corner2, (0, box_h - 75))
        box.paste(corner3, (text_w + 70, 0))
        box.paste(corner4, (text_w + 70, box_h - 75))
        box.paste(BuildImage.new("RGBA", (text_w, box_h - 40), "white"), (70, 20))
        box.paste(BuildImage.new("RGBA", (text_w + 88, box_h - 150), "white"), (27, 75))
        box.paste(text_img, (70, 17 + (box_h - 40 - text_h) // 2), alpha=True)

        dialog = BuildImage.new("RGBA", (box.width + 130, box.height + 60), "#eaedf4")
        dialog.paste(img, (20, 20), alpha=True)
        dialog.paste(box, (130, 60), alpha=True)
        dialog.paste(label, (160, 25))
        dialog.paste(name_img, (260, 22 + (35 - name_h) // 2), alpha=True)
        return dialog

    dialogs = [(await make_dialog(text)) for text in texts]
    frame_w = max((dialog.width for dialog in dialogs))
    frame_h = sum((dialog.height for dialog in dialogs))
    frame = BuildImage.new("RGBA", (frame_w, frame_h), "#eaedf4")
    current_h = 0
    for dialog in dialogs:
        frame.paste(dialog, (0, current_h))
        current_h += dialog.height
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def paint(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((117, 135), keep_ratio=True)
    frame = await load_image("paint/0.png")
    frame.paste(img.rotate(4, expand=True), (95, 107), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def shock(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((300, 300))
    frames: List[IMG] = []
    for i in range(30):
        frames.append(
            img.motion_blur(random.randint(-90, 90), random.randint(0, 50))
            .rotate(random.randint(-20, 20))
            .image
        )
    return save_gif(frames, 0.01)


# noinspection PyUnusedLocal
async def coupon(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img

    text = (args[0] if args else f"{users[0].name}陪睡券") + "\n（永久有效）"
    text_img = BuildImage.new("RGBA", (250, 100))
    try:
        text_img.draw_text(
            (0, 0, text_img.width, text_img.height),
            text,
            lines_align="center",
            max_fontsize=30,
            min_fontsize=15,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    frame = await load_image("coupon/0.png")
    img = img.convert("RGBA").circle().resize((60, 60)).rotate(22, expand=True)
    frame.paste(img, (164, 85), alpha=True)
    frame.paste(text_img.rotate(22, expand=True), (94, 108), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def listen_music(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA")
    frame = await load_image("listen_music/0.png")
    frames: List[IMG] = []
    for i in range(0, 360, 10):
        frames.append(
            frame.copy()
            .paste(img.rotate(-i).resize((215, 215)), (100, 100), below=True)
            .image
        )
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def dianzhongdian(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img

    text = args[0] if args else "救命啊"
    trans = await translate(text, lang_to="jp")
    img = img.convert("L").resize_width(500)
    text_img1 = BuildImage.new("RGBA", (500, 60))
    text_img2 = BuildImage.new("RGBA", (500, 35))
    try:
        text_img1.draw_text(
            (20, 0, text_img1.width - 20, text_img1.height),
            text,
            max_fontsize=50,
            min_fontsize=25,
            fill="white",
        )
        text_img2.draw_text(
            (20, 0, text_img2.width - 20, text_img2.height),
            trans,
            max_fontsize=25,
            min_fontsize=10,
            fill="white",
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    frame = BuildImage.new("RGBA", (500, img.height + 100), "black")
    frame.paste(img, alpha=True)
    frame.paste(text_img1, (0, img.height), alpha=True)
    frame.paste(text_img2, (0, img.height + 60), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def funny_mirror(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((500, 500))
    frames: List[IMG] = [img.image]
    coeffs = [0.01, 0.03, 0.05, 0.08, 0.12, 0.17, 0.23, 0.3, 0.4, 0.6]
    borders = [25, 52, 67, 83, 97, 108, 118, 128, 138, 148]
    for i in range(10):
        new_size = 500 - borders[i] * 2
        new_img = img.distort((coeffs[i], 0, 0, 0)).resize_canvas((new_size, new_size))
        frames.append(new_img.resize((500, 500)).image)
    frames.extend(frames[::-1])
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def love_you(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    frames: List[IMG] = []
    locs = [(68, 65, 70, 70), (63, 59, 80, 80)]
    for i in range(2):
        heart = await load_image(f"love_you/{i}.png")
        frame = BuildImage.new("RGBA", heart.size, "white")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), alpha=True).paste(heart, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.2)


# noinspection PyUnusedLocal
async def symmetric(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    arg = args[0] if args else ""

    img_w, img_h = img.size

    Mode = namedtuple(
        "Mode", ["method", "frame_size", "size1", "pos1", "size2", "pos2"]
    )
    modes: Dict[str, Mode] = {
        "left": Mode(
            Image.FLIP_LEFT_RIGHT,
            (img_w // 2 * 2, img_h),
            (0, 0, img_w // 2, img_h),
            (0, 0),
            (img_w // 2, 0, img_w // 2 * 2, img_h),
            (img_w // 2, 0),
        ),
        "right": Mode(
            Image.FLIP_LEFT_RIGHT,
            (img_w // 2 * 2, img_h),
            (img_w // 2, 0, img_w // 2 * 2, img_h),
            (img_w // 2, 0),
            (0, 0, img_w // 2, img_h),
            (0, 0),
        ),
        "top": Mode(
            Image.FLIP_TOP_BOTTOM,
            (img_w, img_h // 2 * 2),
            (0, 0, img_w, img_h // 2),
            (0, 0),
            (0, img_h // 2, img_w, img_h // 2 * 2),
            (0, img_h // 2),
        ),
        "bottom": Mode(
            Image.FLIP_TOP_BOTTOM,
            (img_w, img_h // 2 * 2),
            (0, img_h // 2, img_w, img_h // 2 * 2),
            (0, img_h // 2),
            (0, 0, img_w, img_h // 2),
            (0, 0),
        ),
    }

    mode = modes["left"]
    if arg == "右":
        mode = modes["right"]
    elif arg == "上":
        mode = modes["top"]
    elif arg == "下":
        mode = modes["bottom"]

    async def make(make_img: BuildImage) -> BuildImage:
        first = make_img
        second = make_img.transpose(mode.method)
        frame = BuildImage.new("RGBA", mode.frame_size)
        frame.paste(first.crop(mode.size1), mode.pos1)
        frame.paste(second.crop(mode.size2), mode.pos2)
        return frame

    return await make_jpg_or_gif(img, make, keep_transparency=True)


# noinspection PyUnusedLocal
async def safe_sense(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    img = img.convert("RGBA").resize((215, 343), keep_ratio=True)
    frame = await load_image(f"safe_sense/0.png")
    frame.paste(img, (215, 135))

    ta = "他" if users[0].gender == "male" else "她"
    text = args[0] if args else f"你给我的安全感\n远不及{ta}的万分之一"
    try:
        frame.draw_text(
            (30, 0, 400, 130),
            text,
            max_fontsize=50,
            allow_wrap=True,
            lines_align="center",
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def always_like(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img.convert("RGBA")
    name = (args[0] if args else "") or users[0].name
    if not name:
        raise ValueError(REQUIRE_NAME)
    text = f"我永远喜欢{name}"

    frame = await load_image(f"always_like/0.png")
    frame.paste(
        img.resize((350, 400), keep_ratio=True, inside=True), (25, 35), alpha=True
    )
    try:
        frame.draw_text(
            (20, 470, frame.width - 20, 570),
            text,
            max_fontsize=70,
            min_fontsize=30,
            weight="bold",
        )
    except ValueError:
        raise ValueError(NAME_TOO_LONG)

    def random_color():
        return random.choice(
            ["red", "darkorange", "gold", "darkgreen", "blue", "cyan", "purple"]
        )

    if len(users) > 1:
        text_w = Text2Image.from_text(text, 70).to_image().width
        ratio = min((frame.width - 40) / text_w, 1)
        text_w *= ratio
        name_w = Text2Image.from_text(name, 70).to_image().width * ratio
        start_w = text_w - name_w + (frame.width - text_w) // 2
        frame.draw_line(
            (start_w, 525, start_w + name_w, 525), fill=random_color(), width=10
        )

    current_h = 400
    for i, user in enumerate(users[1:], start=1):
        img = user.img.convert("RGBA")
        frame.paste(
            img.resize((350, 400), keep_ratio=True, inside=True),
            (10 + random.randint(0, 50), 20 + random.randint(0, 70)),
            alpha=True,
        )
        name = (args[i] if len(args) > i else "") or user.name
        if not name:
            raise ValueError("找不到对应的名字，名字数须与目标数一致")
        try:
            frame.draw_text(
                (400, current_h, frame.width - 20, current_h + 80),
                name,
                max_fontsize=70,
                min_fontsize=30,
                weight="bold",
            )
        except ValueError:
            raise ValueError(NAME_TOO_LONG)

        if len(users) > i + 1:
            name_w = min(Text2Image.from_text(name, 70).to_image().width, 380)
            start_w = 400 + (410 - name_w) // 2
            line_h = current_h + 40
            frame.draw_line(
                (start_w, line_h, start_w + name_w, line_h),
                fill=random_color(),
                width=10,
            )
        current_h -= 70
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def interview(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    if len(users) >= 2:
        self_img = users[0].img
        user_img = users[1].img
    else:
        self_img = await load_image("interview/huaji.png")
        user_img = users[0].img

    self_img = self_img.convert("RGBA").square().resize((124, 124))
    user_img = user_img.convert("RGBA").square().resize((124, 124))

    frame = BuildImage.new("RGBA", (600, 310), "white")
    microphone = await load_image("interview/microphone.png")
    frame.paste(microphone, (330, 103), alpha=True)
    frame.paste(self_img, (419, 40), alpha=True)
    frame.paste(user_img, (57, 40), alpha=True)
    try:
        frame.draw_text(
            (20, 200, 580, 310), args[0] if args else "采访大佬经验", max_fontsize=50, min_fontsize=20
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def punch(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((260, 260))
    frames: List[IMG] = []
    # fmt: off
    locs = [
        (-50, 20), (-40, 10), (-30, 0), (-20, -10), (-10, -10), (0, 0),
        (10, 10), (20, 20), (10, 10), (0, 0), (-10, -10), (10, 0), (-30, 10)
    ]
    # fmt: on
    for i in range(13):
        fist = await load_image(f"punch/{i}.png")
        frame = BuildImage.new("RGBA", fist.size, "white")
        x, y = locs[i]
        frame.paste(img, (x, y - 15), alpha=True).paste(fist, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.03)


# noinspection PyUnusedLocal
async def cyan(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    color = (78, 114, 184)
    frame = img.convert("RGB").square().resize((500, 500)).color_mask(color)
    frame.draw_text(
        (400, 40, 480, 280),
        "群\n青",
        max_fontsize=80,
        weight="bold",
        fill="white",
        stroke_ratio=0.04,
        stroke_fill=color,
    ).draw_text(
        (200, 270, 480, 350),
        "YOASOBI",
        halign="right",
        max_fontsize=40,
        fill="white",
        stroke_ratio=0.06,
        stroke_fill=color,
    )
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def pound(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [
        (135, 240, 138, 47), (135, 240, 138, 47), (150, 190, 105, 95), (150, 190, 105, 95),
        (148, 188, 106, 98), (146, 196, 110, 88), (145, 223, 112, 61), (145, 223, 112, 61)
    ]
    # fmt: on
    frames: List[IMG] = []
    for i in range(8):
        frame = await load_image(f"pound/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def thump(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [(65, 128, 77, 72), (67, 128, 73, 72), (54, 139, 94, 61), (57, 135, 86, 65)]
    # fmt: on
    frames: List[IMG] = []
    for i in range(4):
        frame = await load_image(f"thump/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.04)


# noinspection PyUnusedLocal
async def need(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((115, 115))
    frame = await load_image("need/0.png")
    frame.paste(img, (327, 232), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def cover_face(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    points = ((15, 15), (448, 0), (445, 456), (0, 465))
    img = img.convert("RGBA").square().resize((450, 450)).perspective(points)
    frame = await load_image("cover_face/0.png")
    frame.paste(img, (120, 150), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def knock(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [(60, 308, 210, 195), (60, 308, 210, 198), (45, 330, 250, 172), (58, 320, 218, 180),
            (60, 310, 215, 193), (40, 320, 250, 285), (48, 308, 226, 192), (51, 301, 223, 200)]
    # fmt: on
    frames: List[IMG] = []
    for i in range(8):
        frame = await load_image(f"knock/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.04)


# noinspection PyUnusedLocal
async def garbage(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((79, 79))
    # fmt: off
    locs = (
            [] + [(39, 40)] * 3 + [(39, 30)] * 2 + [(39, 32)] * 10
            + [(39, 30), (39, 27), (39, 32), (37, 49), (37, 64),
               (37, 67), (37, 67), (39, 69), (37, 70), (37, 70)]
    )
    # fmt: on
    frames: List[IMG] = []
    for i in range(25):
        frame = await load_image(f"garbage/{i}.png")
        frame.paste(img, locs[i], below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.04)


# noinspection PyUnusedLocal
async def whyatme(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((265, 265), keep_ratio=True)
    frame = await load_image("whyatme/0.png")
    frame.paste(img, (42, 13), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def decent_kiss(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((589, 340), keep_ratio=True)
    frame = await load_image("decent_kiss/0.png")
    frame.paste(img, (0, 91), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def jiujiu(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((75, 51), keep_ratio=True)
    frames: List[IMG] = []
    for i in range(8):
        frame = await load_image(f"jiujiu/{i}.png")
        frame.paste(img, below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.06)


# noinspection PyUnusedLocal
async def suck(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [(82, 100, 130, 119), (82, 94, 126, 125), (82, 120, 128, 99), (81, 164, 132, 55),
            (79, 163, 132, 55), (82, 140, 127, 79), (83, 152, 125, 67), (75, 157, 140, 62),
            (72, 165, 144, 54), (80, 132, 128, 87), (81, 127, 127, 92), (79, 111, 132, 108)]
    # fmt: on
    frames: List[IMG] = []
    for i in range(12):
        bg = await load_image(f"suck/{i}.png")
        frame = BuildImage.new("RGBA", bg.size, "white")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), alpha=True).paste(bg, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.08)


# noinspection PyUnusedLocal
async def hammer(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    # fmt: off
    locs = [(62, 143, 158, 113), (52, 177, 173, 105), (42, 192, 192, 92), (46, 182, 184, 100),
            (54, 169, 174, 110), (69, 128, 144, 135), (65, 130, 152, 124)]
    # fmt: on
    frames: List[IMG] = []
    for i in range(7):
        frame = await load_image(f"hammer/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.07)


# noinspection PyUnusedLocal
async def tightly(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((640, 400), keep_ratio=True)
    # fmt: off
    locs = [(39, 169, 267, 141), (40, 167, 264, 143), (38, 174, 270, 135), (40, 167, 264, 143), (38, 174, 270, 135),
            (40, 167, 264, 143), (38, 174, 270, 135), (40, 167, 264, 143), (38, 174, 270, 135), (28, 176, 293, 134),
            (5, 215, 333, 96), (10, 210, 321, 102), (3, 210, 330, 104), (4, 210, 328, 102), (4, 212, 328, 100),
            (4, 212, 328, 100), (4, 212, 328, 100), (4, 212, 328, 100), (4, 212, 328, 100), (29, 195, 285, 120)]
    # fmt: on
    frames: List[IMG] = []
    for i in range(20):
        frame = await load_image(f"tightly/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.08)


# noinspection PyUnusedLocal
async def distracted(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square().resize((500, 500))
    frame = await load_image("distracted/1.png")
    label = await load_image("distracted/0.png")
    frame.paste(img, below=True).paste(label, (140, 320), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def anyasuki(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    # Image
    if args is None:
        args = []
    user_img = users[0].img
    frame = await load_image("anyasuki/0.png")
    try:
        frame.draw_text(
            (5, frame.height - 60, frame.width - 5, frame.height - 10),
            args[0] if args else "阿尼亚喜欢这个",
            max_fontsize=40,
            fill="white",
            stroke_fill="black",
            stroke_ratio=0.06,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(
            img.resize((305, 235), keep_ratio=True), (106, 72), below=True
        )

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def thinkwhat(users: List[UserInfo], **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = await load_image("thinkwhat/0.png")

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(
            img.resize((534, 493), keep_ratio=True), (530, 0), below=True
        )

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def keepaway(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    imgs = [each.img for each in users]

    def trans(img: BuildImage, n: int) -> BuildImage:
        img = img.convert("RGBA").square().resize((100, 100))
        if n < 4:
            return img.rotate(n * 90)
        else:
            return img.transpose(Image.FLIP_LEFT_RIGHT).rotate((n - 4) * 90)

    def paste(img: BuildImage):
        nonlocal count
        y = 90 if count < 4 else 190
        frame.paste(img, ((count % 4) * 100, y))
        count += 1

    text = args[0] if args else "如何提高社交质量 : \n远离以下头像的人"
    frame = BuildImage.new("RGB", (400, 290), "white")
    frame.draw_text((10, 10, 390, 80), text, max_fontsize=40, halign="left")
    count = 0
    num_per_user = 8 // len(imgs)
    for each_img in imgs:
        for index in range(num_per_user):
            paste(trans(each_img, index))
    num_left = 8 - num_per_user * len(imgs)
    for i in range(num_left):
        paste(trans(imgs[-1], i + num_per_user))

    return frame.save_jpg()


# noinspection PyUnusedLocal
async def marriage(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize_height(1080)
    img_w, img_h = img.size
    if img_w > 1500:
        img_w = 1500
    elif img_w < 800:
        img_h = int(img_h * img_w / 800)
    frame = img.resize_canvas((img_w, img_h)).resize_height(1080)
    left = await load_image("marriage/0.png")
    right = await load_image("marriage/1.png")
    frame.paste(left, alpha=True).paste(
        right, (frame.width - right.width, 0), alpha=True
    )
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def painter(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((240, 345), keep_ratio=True, direction="north")
    frame = await load_image("painter/0.png")
    frame.paste(img, (125, 91), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def repeat(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []

    async def single_msg(user: UserInfo) -> BuildImage:
        user_img = user.img.convert("RGBA").circle().resize((100, 100))
        user_name_img = Text2Image.from_text(f"{user.name}", 40).to_image()
        time_str = datetime.now().strftime("%H:%M")
        time_img = Text2Image.from_text(time_str, 40, fill="gray").to_image()
        bg = BuildImage.new("RGB", (1079, 200), (248, 249, 251, 255))
        bg.paste(user_img, (50, 50), alpha=True)
        bg.paste(user_name_img, (175, 45), alpha=True)
        bg.paste(time_img, (200 + user_name_img.width, 50), alpha=True)
        bg.paste(text_img, (175, 100), alpha=True)
        return bg

    text = args[0] if args else "救命啊"
    text_img = Text2Image.from_text(text, 50).to_image()
    if text_img.width > 900:
        raise ValueError(TEXT_TOO_LONG)

    msg_img = BuildImage.new("RGB", (1079, 1000))
    for i in range(5):
        index = i % len(users)
        msg_img.paste(await single_msg(users[index]), (0, 200 * i))
    msg_img_twice = BuildImage.new("RGB", (msg_img.width, msg_img.height * 2))
    msg_img_twice.paste(msg_img).paste(msg_img, (0, msg_img.height))

    input_img = await load_image("repeat/0.jpg")
    self_img = sender.img.convert("RGBA").circle().resize((75, 75))
    input_img.paste(self_img, (15, 40), alpha=True)

    frames: List[IMG] = []
    for i in range(50):
        frame = BuildImage.new("RGB", (1079, 1192), "white")
        frame.paste(msg_img_twice, (0, -20 * i))
        frame.paste(input_img, (0, 1000))
        frames.append(frame.image)

    return save_gif(frames, 0.08)


# noinspection PyUnusedLocal
async def anti_kidnap(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    img = users[0].img.convert("RGBA")
    img = img.convert("RGBA").circle().resize((450, 450))
    bg = await load_image("anti_kidnap/0.png")
    frame = BuildImage.new("RGBA", bg.size, "white")
    frame.paste(img, (30, 78))
    frame.paste(bg, alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def charpic(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    user_img = users[0].img

    str_map = "@@$$&B88QMMGW##EE93SPPDOOU**==()+^,\"--''.  "
    num = len(str_map)
    font = Font.find("Consolas").load_font(15)

    async def make(img: BuildImage) -> BuildImage:
        img = img.convert("L").resize_width(150)
        img = img.resize((img.width, img.height // 2))
        lines = []
        for y in range(img.height):
            line = ""
            for x in range(img.width):
                gray = img.image.getpixel((x, y))
                line += str_map[int(num * gray / 256)]
            lines.append(line)
        text = "\n".join(lines)
        w, h = font.getsize_multiline(text)
        text_img = Image.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(text_img)
        draw.multiline_text((0, 0), text, font=font, fill="black")
        return BuildImage(text_img)

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def cuidao(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA")
    img_w, img_h = img.size
    max_len = max(img_w, img_h)
    img_w = int(img_w * 500 / max_len)
    img_h = int(img_h * 500 / max_len)
    img = img.resize((img_w, img_h))

    bg = BuildImage.new("RGB", (600, img_h + 230), (255, 255, 255))
    bg.paste(img, (int(300 - img_w / 2), 110))
    draw = bg.draw
    fontname = BOLD_FONT

    font = await load_font(fontname, 46)
    ta = "他" if users[0].gender == "male" else "她"
    text = f"{ta}好像失踪了，一刀都没出"
    text_w, _ = font.getsize(text)
    draw.text((300 - text_w / 2, img_h + 120), text, font=font, fill=(0, 0, 0))

    font = await load_font(fontname, 26)
    text = f"你们谁看见了麻烦叫{ta}赶紧回来出刀"
    text_w, _ = font.getsize(text)
    draw.text((300 - text_w / 2, img_h + 180), text, font=font, fill=(0, 0, 0))

    name = args[0] if args else random.choice([users[0].name, ta])
    text = f"请问你们看到{name}了吗?"
    text = re.sub(emoji.get_emoji_regexp(), "", text)

    fontsize = 70
    while True:
        font = await load_font(fontname, fontsize)
        width, height = font.getsize_multiline(text)
        if width > 560 or height > 110:
            fontsize -= 1
        else:
            break
        if fontsize < 25:
            fontsize = 0
            break

    if not fontsize:
        raise ValueError(NAME_TOO_LONG)

    font = await load_font(fontname, fontsize)
    text_w, text_h = font.getsize(text)
    x = 300 - text_w / 2
    y = 55 - text_h / 2
    draw.text((x, y), text, font=font, fill=(0, 0, 0))
    return bg.save_jpg()


# noinspection PyUnusedLocal
async def have_lunch(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    bg = await load_image("have_lunch/0.jpg")
    frame = BuildImage.new("RGBA", bg.size)
    frame.paste(bg, below=True)
    frame.paste(img.resize((324, 324)), (653, 30))
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def mywife(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    # 现在会根据参数决定是谁的老婆
    # 连续at两个人的情况下，user1为受害者，user2为user1的对象
    ta = args[0] if args else sender.name
    if len(users) > 1:
        ta = users[1].name
    img = users[0].img

    sex = '老婆' if users[0].gender == 'female' else '老公'

    img = img.convert("RGBA").resize_width(400)
    img_w, img_h = img.size
    frame = BuildImage.new("RGBA", (650, img_h + 500), "white")
    frame.paste(img, (int(325 - img_w / 2), 105), alpha=True)

    text = f"如果你的{sex}长这样"
    frame.draw_text(
        (27, 12, 27 + 596, 12 + 79),
        text,
        max_fontsize=70,
        min_fontsize=30,
        allow_wrap=True,
        lines_align="center",
        weight="bold",
    )
    text = f"那么这就不是你的{sex}\n这是{ta}的{sex}"
    frame.draw_text(
        (27, img_h + 120, 27 + 593, img_h + 120 + 135),
        text,
        max_fontsize=70,
        min_fontsize=30,
        allow_wrap=True,
        weight="bold",
    )
    text = f"滚去找你\n自己的{sex}去"
    frame.draw_text(
        (27, img_h + 295, 27 + 374, img_h + 295 + 135),
        text,
        max_fontsize=70,
        min_fontsize=30,
        allow_wrap=True,
        lines_align="center",
        weight="bold",
    )

    img_point = (await load_image("mywife/1.png")).resize_width(200)
    frame.paste(img_point, (421, img_h + 270))

    return frame.save_jpg()


# noinspection PyUnusedLocal
async def walnutpad(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = await load_image("walnutpad/0.png")

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(
            img.resize((540, 360), keep_ratio=True), (368, 65), below=True
        )

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def walnut_zoom(users: List[UserInfo], **kwargs) -> BytesIO:
    # fmt: off
    locs = (
        (-222, 30, 695, 430), (-212, 30, 695, 430), (0, 30, 695, 430), (41, 26, 695, 430),
        (-100, -67, 922, 570), (-172, -113, 1059, 655), (-273, -192, 1217, 753)
    )  # (-47, -12, 801, 495),
    seq = [0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 6, 6, 6]
    # fmt: on

    img = users[0].img

    def maker(i: int) -> Maker:
        async def make(m_img: BuildImage) -> BuildImage:
            frame = await load_image(f"walnut_zoom/{i}.png")
            x, y, w, h = locs[seq[i]]
            m_img = m_img.resize((w, h), keep_ratio=True).rotate(4.2, expand=True)
            frame.paste(m_img, (x, y), below=True)
            return frame

        return make

    return await make_gif_or_combined_gif(img, maker, 24, 0.2, FrameAlignPolicy.extend_last)


# noinspection PyUnusedLocal
async def teach(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = (await load_image("teach/0.png")).resize_width(960).convert("RGBA")
    text = args[0] if args else "我老婆"
    try:
        frame.draw_text(
            (10, frame.height - 80, frame.width - 10, frame.height - 5),
            text,
            max_fontsize=50,
            fill="white",
            stroke_fill="black",
            stroke_ratio=0.06,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(
            img.resize((550, 395), keep_ratio=True), (313, 60), below=True
        )

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def addition(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = await load_image("addiction/0.png")

    if args:
        expand_frame = BuildImage.new("RGBA", (246, 286), "white")
        expand_frame.paste(frame)
        try:
            expand_frame.draw_text(
                (10, 246, 236, 286),
                args[0],
                max_fontsize=45,
                lines_align="center",
            )
        except ValueError:
            raise ValueError(TEXT_TOO_LONG)
        frame = expand_frame

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(img.resize((70, 70), keep_ratio=True), (0, 0))

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def gun(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    frame = await load_image("gun/0.png")
    frame.paste(img.convert("RGBA").resize((500, 500), keep_ratio=True), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def blood_pressure(users: List[UserInfo], **kwargs) -> BytesIO:
    user_img = users[0].img
    frame = await load_image("blood_pressure/0.png")

    async def make(img: BuildImage) -> BuildImage:
        return frame.copy().paste(
            img.resize((414, 450), keep_ratio=True), (16, 17), below=True
        )

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def read_book(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    img = users[0].img
    frame = await load_image("read_book/0.png")
    points = ((0, 108), (1092, 0), (1023, 1134), (29, 1134))
    img = img.convert("RGBA").resize((1000, 1100), keep_ratio=True, direction="north")
    cover = img.perspective(points)
    frame.paste(cover, (1138, 1172), below=True)
    if args:
        chars = list(" ".join(args[0].splitlines()))
        pieces: List[BuildImage] = []
        for char in chars:
            piece = BuildImage(
                Text2Image.from_text(char, 200, fill="white", weight="bold").to_image()
            )
            if re.fullmatch(r"[a-zA-Z0-9\s]", char):
                piece = piece.rotate(-90, expand=True)
            else:
                piece = piece.resize_canvas((piece.width, piece.height - 40), "south")
            pieces.append(piece)
        w = max((piece.width for piece in pieces))
        h = sum((piece.height for piece in pieces))
        if w > 240 or h > 3000:
            raise ValueError(TEXT_TOO_LONG)
        text_img = BuildImage.new("RGBA", (w, h))
        h = 0
        for piece in pieces:
            text_img.paste(piece, ((w - piece.width) // 2, h), alpha=True)
            h += piece.height
        if h > 780:
            ratio = 780 / h
            text_img = text_img.resize((int(w * ratio), int(h * ratio)))
        text_img = text_img.rotate(3, expand=True)
        w, h = text_img.size
        frame.paste(text_img, (870 + (240 - w) // 2, 1500 + (780 - h) // 2), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def call_110(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    user_imgs = [each.img for each in users]
    sender_img = sender.img
    if len(user_imgs) >= 2:
        img1 = user_imgs[0]
        img0 = user_imgs[1]
    else:
        img1 = sender_img
        img0 = user_imgs[0]
    img1 = img1.convert("RGBA").square().resize((250, 250))
    img0 = img0.convert("RGBA").square().resize((250, 250))

    frame = BuildImage.new("RGB", (900, 500), "white")
    frame.draw_text((0, 0, 900, 200), "遇到困难请拨打", max_fontsize=100)
    frame.paste(img1, (50, 200), alpha=True)
    frame.paste(img1, (325, 200), alpha=True)
    frame.paste(img0, (600, 200), alpha=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def confuse(users: List[UserInfo], sender: UserInfo, args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    img = img.convert("RGBA").resize((500, 500), keep_ratio=True)
    frames: List[IMG] = []
    for i in range(100):
        mask = (await load_image(f"confuse/{i}.png")).resize(img.size, keep_ratio=True)
        frame = BuildImage.new("RGBA", img.size, (255, 255, 255, 0))
        avatar = img
        frame.paste(avatar)
        frame.paste(mask, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.015)


# noinspection PyUnusedLocal
async def hit_screen(users: List[UserInfo], **kwargs) -> BytesIO:
    params = (
        (((1, 10), (138, 1), (140, 119), (7, 154)), (32, 37)),
        (((1, 10), (138, 1), (140, 121), (7, 154)), (32, 37)),
        (((1, 10), (138, 1), (139, 125), (10, 159)), (32, 37)),
        (((1, 12), (136, 1), (137, 125), (8, 159)), (34, 37)),
        (((1, 9), (137, 1), (139, 122), (9, 154)), (35, 41)),
        (((1, 8), (144, 1), (144, 123), (12, 155)), (30, 45)),
        (((1, 8), (140, 1), (141, 121), (10, 155)), (29, 49)),
        (((1, 9), (140, 1), (139, 118), (10, 153)), (27, 53)),
        (((1, 7), (144, 1), (145, 117), (13, 153)), (19, 57)),
        (((1, 7), (144, 1), (143, 116), (13, 153)), (19, 57)),
        (((1, 8), (139, 1), (141, 119), (12, 154)), (19, 55)),
        (((1, 13), (140, 1), (143, 117), (12, 156)), (16, 57)),
        (((1, 10), (138, 1), (142, 117), (11, 149)), (14, 61)),
        (((1, 10), (141, 1), (148, 125), (13, 153)), (11, 57)),
        (((1, 12), (141, 1), (147, 130), (16, 150)), (11, 60)),
        (((1, 15), (165, 1), (175, 135), (1, 171)), (-6, 46)),
    )
    user_img = users[0].img
    frames = []

    def maker(i: int) -> Maker:
        async def make(img: BuildImage) -> BuildImage:
            img = img.resize((140, 120), keep_ratio=True)
            frame = await load_image(f"hit_screen/{i}.png")
            if 6 <= i < 22:
                points, pos = params[i - 6]
                frame.paste(img.perspective(points), pos, below=True)
            return frame

        return make

    return await make_gif_or_combined_gif(user_img, maker, 29, 0.1, FrameAlignPolicy.extend_first)


# noinspection PyUnusedLocal
async def fencing(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    if len(users) >= 2:
        self_img = users[0].img
        user_img = users[1].img
    else:
        self_img = sender.img
        user_img = users[0].img
    self_head = self_img.convert("RGBA").circle().resize((27, 27))
    user_head = user_img.convert("RGBA").circle().resize((27, 27))
    # fmt: off
    user_locs = [
        (57, 4), (55, 5), (58, 7), (57, 5), (53, 8), (54, 9),
        (64, 5), (66, 8), (70, 9), (73, 8), (81, 10), (77, 10),
        (72, 4), (79, 8), (50, 8), (60, 7), (67, 6), (60, 6), (50, 9)
    ]
    self_locs = [
        (10, 6), (3, 6), (32, 7), (22, 7), (13, 4), (21, 6),
        (30, 6), (22, 2), (22, 3), (26, 8), (23, 8), (27, 10),
        (30, 9), (17, 6), (12, 8), (11, 7), (8, 6), (-2, 10), (4, 9)
    ]
    # fmt: on
    frames = []
    for i in range(19):
        frame = await load_image(f"fencing/{i}.png")
        frame.paste(user_head, user_locs[i], alpha=True)
        frame.paste(self_head, self_locs[i], alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.05)


# noinspection PyUnusedLocal
async def hug_leg(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").square()
    locs = [
        (50, 73, 68, 92),
        (58, 60, 62, 95),
        (65, 10, 67, 118),
        (61, 20, 77, 97),
        (55, 44, 65, 106),
        (66, 85, 60, 98),
    ]
    frames = []
    for i in range(6):
        frame = await load_image(f"hug_leg/{i}.png")
        x, y, w, h = locs[i]
        frame.paste(img.resize((w, h)), (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.06)


# noinspection PyUnusedLocal
async def tankuku_holdsign(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((300, 230), keep_ratio=True)
    params = (
        (((0, 46), (320, 0), (350, 214), (38, 260)), (68, 91)),
        (((18, 0), (328, 28), (298, 227), (0, 197)), (184, 77)),
        (((15, 0), (294, 28), (278, 216), (0, 188)), (194, 65)),
        (((14, 0), (279, 27), (262, 205), (0, 178)), (203, 55)),
        (((14, 0), (270, 25), (252, 195), (0, 170)), (209, 49)),
        (((15, 0), (260, 25), (242, 186), (0, 164)), (215, 41)),
        (((10, 0), (245, 21), (230, 180), (0, 157)), (223, 35)),
        (((13, 0), (230, 21), (218, 168), (0, 147)), (231, 25)),
        (((13, 0), (220, 23), (210, 167), (0, 140)), (238, 21)),
        (((27, 0), (226, 46), (196, 182), (0, 135)), (254, 13)),
        (((27, 0), (226, 46), (196, 182), (0, 135)), (254, 13)),
        (((27, 0), (226, 46), (196, 182), (0, 135)), (254, 13)),
        (((0, 35), (200, 0), (224, 133), (25, 169)), (175, 9)),
        (((0, 35), (200, 0), (224, 133), (25, 169)), (195, 17)),
        (((0, 35), (200, 0), (224, 133), (25, 169)), (195, 17)),
    )
    frames = []
    for i in range(15):
        points, pos = params[i]
        frame = await load_image(f"tankuku_holdsign/{i}.png")
        frame.paste(img.perspective(points), pos, below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.1)


# noinspection PyUnusedLocal
async def no_response(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((1050, 783), keep_ratio=True)
    frame = await load_image("no_response/0.png")
    frame.paste(img, (0, 581), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def hold_tight(users: List[UserInfo], **kwargs) -> BytesIO:
    img = users[0].img
    img = img.convert("RGBA").resize((159, 171), keep_ratio=True)
    frame = await load_image("hold_tight/0.png")
    frame.paste(img, (113, 205), below=True)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def look_flat(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    user_img = users[0].img

    ratio = 2
    text = "可恶...被人看扁了"
    for arg in args:
        if arg.isdigit():
            ratio = int(arg)
            if ratio < 2 or ratio > 10:
                ratio = 2
        elif arg:
            text = arg

    img_w = 500
    text_h = 80
    text_frame = BuildImage.new("RGBA", (img_w, text_h), "white")
    try:
        text_frame.draw_text(
            (10, 0, img_w - 10, text_h),
            text,
            max_fontsize=55,
            min_fontsize=30,
            weight="bold",
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    async def make(img: BuildImage) -> BuildImage:
        img = img.convert("RGBA").resize_width(img_w)
        img = img.resize((img_w, img.height // ratio))
        img_h = img.height
        frame = BuildImage.new("RGBA", (img_w, img_h + text_h), "white")
        return frame.paste(img, alpha=True).paste(text_frame, (0, img_h), alpha=True)

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def look_this_icon(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    user_img = users[0].img
    text = args[0] if args else "朋友\n先看看这个图标再说话"
    frame = await load_image("look_this_icon/nmsl.png")
    try:
        frame.draw_text(
            (0, 933, 1170, 1143),
            text,
            lines_align="center",
            weight="bold",
            max_fontsize=100,
            min_fontsize=50,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    async def make(img: BuildImage) -> BuildImage:
        img = img.convert("RGBA").resize((515, 515), keep_ratio=True)
        return frame.copy().paste(img, (599, 403), below=True)

    return await make_jpg_or_gif(user_img, make)


# noinspection PyUnusedLocal
async def captain(users: List[UserInfo], sender: UserInfo, **kwargs) -> BytesIO:
    imgs: List[BuildImage] = []
    if len(users) == 1:
        imgs.append(sender.img)
        imgs.append(users[0].img)
        imgs.append(users[0].img)
    elif len(users) == 2:
        imgs.append(users[0].img)
        imgs.append(users[1].img)
        imgs.append(users[1].img)
    else:
        for each in users:
            imgs.append(each.img)

    bg0 = await load_image("captain/0.png")
    bg1 = await load_image("captain/1.png")
    bg2 = await load_image("captain/2.png")

    frame = BuildImage.new("RGBA", (640, 440 * len(imgs)), "white")
    for i in range(len(imgs)):
        bg = bg0 if i < len(imgs) - 2 else bg1 if i == len(imgs) - 2 else bg2
        imgs[i] = imgs[i].convert("RGBA").square().resize((250, 250))
        bg = bg.copy().paste(imgs[i], (350, 85))
        frame.paste(bg, (0, 440 * i))

    return frame.save_jpg()


# noinspection PyUnusedLocal
async def jiji_king(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []

    user_imgs = [each.img for each in users]
    block_num = 5
    if len(user_imgs) >= 7 or len(args) >= 7:
        block_num = max(len(user_imgs), len(args)) - 1

    chars = ["急"]
    text = "我是急急国王"
    if len(args) == 1:
        if len(user_imgs) == 1:
            chars = [args[0]] * block_num
            text = f"我是{args[0] * 2}国王"
        else:
            text = args[0]
    elif len(args) == 2:
        chars = [args[0]] * block_num
        text = args[1]
    elif args:
        chars = sum(
            [[arg] * math.ceil(block_num / len(args[:-1])) for arg in args[:-1]], []
        )
        text = args[-1]

    frame = BuildImage.new("RGBA", (10 + 100 * block_num, 400), "white")
    king = await load_image("jiji_king/0.png")
    king.paste(
        user_imgs[0].convert("RGBA").square().resize((125, 125)), (237, 5), alpha=True
    )
    frame.paste(king, ((frame.width - king.width) // 2, 0))

    if len(user_imgs) > 1:
        imgs = user_imgs[1:]
        imgs = [img.convert("RGBA").square().resize((90, 90)) for img in imgs]
    else:
        imgs = []
        for char in chars:
            block = BuildImage.new("RGBA", (90, 90), "black")
            try:
                block.draw_text(
                    (0, 0, 90, 90),
                    char,
                    lines_align="center",
                    weight="bold",
                    max_fontsize=60,
                    min_fontsize=30,
                    fill="white",
                )
            except ValueError:
                raise ValueError(TEXT_TOO_LONG)
            imgs.append(block)

    imgs = sum([[img] * math.ceil(block_num / len(imgs)) for img in imgs], [])
    for i in range(block_num):
        frame.paste(imgs[i], (10 + 100 * i, 200))

    try:
        frame.draw_text(
            (10, 300, frame.width - 10, 390),
            text,
            lines_align="center",
            weight="bold",
            max_fontsize=100,
            min_fontsize=30,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)

    return frame.save_jpg()


# noinspection PyUnusedLocal
async def incivilization(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    img = users[0].img
    frame = await load_image("incivilization/0.png")
    img = ImageEnhance.Brightness(img.convert("RGBA").circle().resize((150, 150)).image).enhance(0.8)
    frame.paste(img, (156, 165), alpha=True)
    text = args[0] if args else "你刚才说的话不是很礼貌！"
    try:
        frame.draw_text(
            (57, 42, 528, 117),
            text,
            weight="bold",
            max_fontsize=50,
            min_fontsize=20,
            allow_wrap=True,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def together(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    if args is None:
        args = []
    arg = args[0] if args else None
    img = users[0].img
    frame = await load_image("together/0.png")
    frame.paste(img.convert("RGBA").resize((63, 63)), (132, 36))
    text = arg if arg else f"一起玩{users[0].name}吧！"
    try:
        frame.draw_text(
            (10, 140, 190, 190),
            text,
            weight="bold",
            max_fontsize=50,
            min_fontsize=10,
            allow_wrap=True,
        )
    except ValueError:
        raise ValueError(TEXT_TOO_LONG)
    return frame.save_jpg()


# noinspection PyUnusedLocal
async def wave(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    user_img = users[0].img
    img_w = min(max(user_img.width, 360), 720)
    period = img_w / 6
    amp = img_w / 60
    frame_num = 8
    phase = 0
    sin = lambda x: amp * math.sin(2 * math.pi / period * (x + phase)) / 2  # noqa

    def maker(i: int) -> Maker:  # noqa
        async def make(img: BuildImage) -> BuildImage:
            img = img.resize_width(img_w)
            img_h = img.height
            frame = img.copy()
            for i in range(img_w):  # noqa
                for j in range(img_h):
                    dx = int(sin(i) * (img_h - j) / img_h)
                    dy = int(sin(j) * j / img_h)
                    if 0 <= i + dx < img_w and 0 <= j + dy < img_h:
                        frame.image.putpixel(
                            (i, j), img.image.getpixel((i + dx, j + dy))
                        )

            frame = frame.resize_canvas((int(img_w - amp), int(img_h - amp)))
            nonlocal phase
            phase += period / frame_num
            return frame

        return make

    return await make_gif_or_combined_gif(
        user_img, maker, frame_num, 0.01, FrameAlignPolicy.extend_loop
    )


# noinspection PyUnusedLocal
async def rise_dead(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    img = users[0].img
    locs = [
        ((81, 55), ((0, 2), (101, 0), (103, 105), (1, 105))),
        ((74, 49), ((0, 3), (104, 0), (106, 108), (1, 108))),
        ((-66, 36), ((0, 0), (182, 5), (184, 194), (1, 185))),
        ((-231, 55), ((0, 0), (259, 4), (276, 281), (13, 278))),
    ]
    img = img.convert("RGBA").square().resize((150, 150))
    imgs = [img.perspective(points) for _, points in locs]
    frames: List[IMG] = []
    for i in range(34):
        frame = await load_image(f"rise_dead/{i}.png")
        if i <= 28:
            idx = 0 if i <= 25 else i - 25
            x, y = locs[idx][0]
            if i % 2 == 1:
                x += 1
                y -= 1
            frame.paste(imgs[idx], (x, y), below=True)
        frames.append(frame.image)
    return save_gif(frames, 0.1)


# noinspection PyUnusedLocal
async def kirby_hammer(users: List[UserInfo], args=None, **kwargs) -> BytesIO:
    user_img = users[0].img
    if args is None:
        args = []
    arg = args[0] if args else None
    # fmt: off
    positions = [
        (318, 163), (319, 173), (320, 183), (317, 193), (312, 199),
        (297, 212), (289, 218), (280, 224), (278, 223), (278, 220),
        (280, 215), (280, 213), (280, 210), (280, 206), (280, 201),
        (280, 192), (280, 188), (280, 184), (280, 179)
    ]

    # fmt: on
    def maker(i: int) -> Maker:
        async def make(img: BuildImage) -> BuildImage:
            img = img.convert("RGBA")
            if arg == "圆":
                img = img.circle()
            img = img.resize_height(80)
            if img.width < 80:
                img = img.resize((80, 80), keep_ratio=True)
            frame = await load_image(f"kirby_hammer/{i}.png")
            if i <= 18:
                x, y = positions[i]
                x = x + 40 - img.width // 2
                frame.paste(img, (x, y), alpha=True)
            elif i <= 39:
                x, y = positions[18]
                x = x + 40 - img.width // 2
                frame.paste(img, (x, y), alpha=True)
            return frame

        return make

    return await make_gif_or_combined_gif(user_img, maker, 62, 0.05, FrameAlignPolicy.extend_loop)
