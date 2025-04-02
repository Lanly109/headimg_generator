from io import BytesIO
from typing import List

from meme_generator import add_meme
from meme_generator.exception import TextOverLength
from meme_generator.utils import make_jpg_or_gif, BuildImage


# noinspection PyUnusedLocal
def cuidao(images: List[BuildImage], texts: List[str], args) -> BytesIO:
    img = images[0]
    img_w, img_h = img.convert("RGBA").resize_width(500).size
    frame = BuildImage.new("RGBA", (600, img_h + 230), "white")
    ta = "她"
    name = ta
    if texts:
        name = texts[0]
    elif args.user_infos:
        info = args.user_infos[0]
        ta = "他" if info.gender == "male" else "她"
        name = info.name or ta

    text = f"{ta}好像失踪了，一刀都没出"

    frame.draw_text(
        (10, img_h + 120, 590, img_h + 185), text, max_fontsize=48, font_style="bold"
    )

    text = f"你们谁看见了麻烦叫{ta}赶紧回来出刀"
    frame.draw_text(
        (20, img_h + 180, 580, img_h + 215), text, max_fontsize=26, font_style="bold"
    )

    text = f"请问你们看到{name}了吗?"
    try:
        frame.draw_text(
            (20, 0, 580, 110), text, max_fontsize=70, min_fontsize=25, font_style="bold"
        )
    except ValueError:
        raise TextOverLength(name)

    def make(make_img: List[BuildImage]) -> BuildImage:
        make_img = make_img[0].resize_width(500)
        return frame.copy().paste(make_img, (int(300 - img_w / 2), 110), alpha=True)

    return make_jpg_or_gif([img], make)


add_meme(
    "cuidao",
    cuidao,
    min_images=1,
    max_images=1,
    min_texts=0,
    max_texts=1,
    keywords=["催刀"],
)
