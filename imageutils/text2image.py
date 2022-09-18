import re
from bbcode import Parser
from PIL import Image, ImageDraw
from PIL.Image import Image as IMG
from PIL.ImageColor import colormap
from typing import List, Optional, Iterator

from .types import *
from .fonts import Font, get_proper_font


class Char:
    def __init__(
        self,
        char: str,
        font: Font,
        fontsize: int = 16,
        fill: ColorType = "black",
        stroke_width: int = 0,
        stroke_fill: Optional[ColorType] = None,
    ):
        self.char = char
        self.font = font
        self.fontsize = fontsize
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill

        if self.font.valid_size:
            self.stroke_width = 0
            self.pilfont = self.font.load_font(self.font.valid_size)
        else:
            self.pilfont = self.font.load_font(fontsize)

        self.ascent, self.descent = self.pilfont.getmetrics()
        self.width, self.height = self.pilfont.getsize(
            self.char, stroke_width=self.stroke_width
        )

        if self.font.valid_size:
            ratio = fontsize / self.font.valid_size
            self.ascent *= ratio
            self.descent *= ratio
            self.width *= ratio
            self.height *= ratio

    def draw_on(self, img: IMG, pos: PosTypeInt):
        if self.font.valid_size:
            ratio = self.font.valid_size / self.fontsize
            new_img = Image.new(
                "RGBA", (int(self.width * ratio), int(self.height * ratio))
            )
            draw = ImageDraw.Draw(new_img)
            draw.text(
                (0, 0),
                self.char,
                font=self.pilfont,
                fill=self.fill,
                embedded_color=True,
            )
            new_img = new_img.resize(
                (int(self.width), int(self.height)), resample=Image.ANTIALIAS
            )
            img.paste(new_img, pos, mask=new_img)
        else:
            draw = ImageDraw.Draw(img)
            draw.text(
                pos,
                self.char,
                font=self.pilfont,
                fill=self.fill,
                stroke_width=self.stroke_width,
                stroke_fill=self.stroke_fill,
                embedded_color=True,
            )


class Line:
    def __init__(
        self, chars: List[Char], align: HAlignType = "left", fontsize: int = 16
    ):
        self.chars: List[Char] = chars
        self.align: HAlignType = align
        self.fontsize = fontsize

    @property
    def width(self) -> int:
        if not self.chars:
            return 0
        return (
            sum([char.width - char.stroke_width * 2 for char in self.chars])
            + self.chars[0].stroke_width
            + self.chars[-1].stroke_width
        )

    @property
    def height(self) -> int:
        if not self.chars:
            return Char("A", get_proper_font("A"), fontsize=self.fontsize).height
        return max([char.height for char in self.chars])

    @property
    def ascent(self) -> int:
        if not self.chars:
            return Char("A", get_proper_font("A"), fontsize=self.fontsize).ascent
        return max([char.ascent for char in self.chars])

    @property
    def descent(self) -> int:
        if not self.chars:
            return Char("A", get_proper_font("A"), fontsize=self.fontsize).descent
        return max([char.descent for char in self.chars])

    def wrap(self, width: float) -> Iterator["Line"]:
        last_idx = 0
        for idx in range(len(self.chars)):
            if Line(self.chars[last_idx : idx + 1]).width > width:
                yield Line(self.chars[last_idx:idx], self.align)
                last_idx = idx
        yield Line(self.chars[last_idx:], self.align)


class Text2Image:
    def __init__(self, lines: List[Line], spacing: int = 4):
        self.lines = lines
        self.spacing = spacing

    @classmethod
    def from_text(
        cls,
        text: str,
        fontsize: int,
        style: FontStyle = "normal",
        weight: FontWeight = "normal",
        fill: ColorType = "black",
        spacing: int = 4,
        align: HAlignType = "left",
        stroke_width: int = 0,
        stroke_fill: Optional[ColorType] = None,
        font_fallback: bool = True,
        fontname: str = "",
        fallback_fonts: List[str] = [],
    ) -> "Text2Image":
        """
        从文本构建 `Text2Image` 对象

        :参数:
          * ``text``: 文本
          * ``fontsize``: 字体大小
          * ``style``: 字体样式，默认为 "normal"
          * ``weight``: 字体粗细，默认为 "normal"
          * ``fill``: 文字颜色
          * ``spacing``: 多行文字间距
          * ``align``: 多行文字对齐方式，默认为靠左
          * ``stroke_width``: 文字描边宽度
          * ``stroke_fill``: 描边颜色
          * ``font_fallback``: 是否使用后备字体，默认为 `True`
          * ``fontname``: 指定首选字体
          * ``fallback_fonts``: 指定备选字体
        """

        font = None
        if not font_fallback:
            if not fontname:
                raise ValueError("`font_fallback` 为 `False` 时必须指定 `fontname`")
            font = Font.find(fontname, fallback_to_default=False)

        lines: List[Line] = []
        chars: List[Char] = []

        text = "\n".join(text.splitlines())
        for char in text:
            if char == "\n":
                lines.append(Line(chars, align))
                chars = []
                continue
            if font_fallback:
                font = get_proper_font(char, style, weight, fontname, fallback_fonts)
            else:
                assert font
            chars.append(Char(char, font, fontsize, fill, stroke_width, stroke_fill))
        if chars:
            lines.append(Line(chars, align, fontsize))
        return cls(lines, spacing)

    @classmethod
    def from_bbcode_text(
        cls,
        text: str,
        fontsize: int = 30,
        fill: ColorType = "black",
        spacing: int = 6,
        align: HAlignType = "left",
        font_fallback: bool = True,
        fontname: str = "",
        fallback_fonts: List[str] = [],
    ) -> "Text2Image":
        """
        从含有 `BBCode` 的文本构建 `Text2Image` 对象

        目前支持的 `BBCode` 标签：
          * ``[align=left|right|center][/align]``: 文字对齐方式
          * ``[color=#66CCFF|red|black][/color]``: 字体颜色
          * ``[font=msyh.ttc][/font]``: 文字字体，需填写完整字体文件名
          * ``[size=30][/size]``: 文字大小
          * ``[b][/b]``: 文字加粗

        :参数:
          * ``text``: 文本
          * ``fontsize``: 字体大小，默认为 30
          * ``fill``: 文字颜色，默认为 `black`
          * ``spacing``: 多行文字间距
          * ``align``: 多行文字对齐方式，默认为靠左
          * ``font_fallback``: 是否使用后备字体，默认为 `True`
          * ``fontname``: 指定首选字体
          * ``fallback_fonts``: 指定备选字体
        """

        font = None
        if not font_fallback:
            if not fontname:
                raise ValueError("`font_fallback` 为 `False` 时必须指定 `fontname`")
            font = Font.find(fontname, fallback_to_default=False)

        lines: List[Line] = []
        chars: List[Char] = []

        def new_line():
            nonlocal lines
            nonlocal chars
            lines.append(Line(chars, last_align, fontsize))
            chars = []

        align_stack = []
        color_stack = []
        font_stack = []
        size_stack = []
        bold_stack = []
        last_align: HAlignType = align

        align_pattern = r"left|right|center"
        colors = "|".join(colormap.keys())
        color_pattern = rf"#[a-fA-F0-9]{{6}}|{colors}"
        font_pattern = r"\S+\.ttf|\S+\.ttc|\S+\.otf|\S+\.fnt"
        size_pattern = r"\d+"

        parser = Parser()
        parser.recognized_tags = {}
        parser.add_formatter("align", None)
        parser.add_formatter("color", None)
        parser.add_formatter("font", None)
        parser.add_formatter("size", None)
        parser.add_formatter("b", None)

        text = "\n".join(text.splitlines())
        tokens = parser.tokenize(text)
        for token_type, tag_name, tag_opts, token_text in tokens:
            if token_type == 1:
                if tag_name == "align":
                    if re.fullmatch(align_pattern, tag_opts["align"]):
                        align_stack.append(tag_opts["align"])
                elif tag_name == "color":
                    if re.fullmatch(color_pattern, tag_opts["color"]):
                        color_stack.append(tag_opts["color"])
                elif tag_name == "font":
                    if re.fullmatch(font_pattern, tag_opts["font"]):
                        font_stack.append(tag_opts["font"])
                elif tag_name == "size":
                    if re.fullmatch(size_pattern, tag_opts["size"]):
                        size_stack.append(tag_opts["size"])
                elif tag_name == "b":
                    bold_stack.append(True)
            elif token_type == 2:
                if tag_name == "align":
                    if align_stack:
                        align_stack.pop()
                elif tag_name == "color":
                    if color_stack:
                        color_stack.pop()
                elif tag_name == "font":
                    if font_stack:
                        font_stack.pop()
                elif tag_name == "size":
                    if size_stack:
                        size_stack.pop()
                elif tag_name == "b":
                    if bold_stack:
                        bold_stack.pop()
            elif token_type == 3:
                new_line()
            elif token_type == 4:
                char_align = align_stack[-1] if align_stack else align
                char_color = color_stack[-1] if color_stack else fill
                char_font = font_stack[-1] if font_stack else fontname
                char_size = size_stack[-1] if size_stack else fontsize
                char_bold = bold_stack[-1] if bold_stack else False

                if char_align != last_align:
                    if chars:
                        new_line()
                    last_align = char_align
                for char in token_text:
                    if font_fallback:
                        font = get_proper_font(
                            char,
                            weight="bold" if char_bold else "normal",
                            fontname=char_font,
                            fallback_fonts=fallback_fonts,
                        )
                    else:
                        assert font
                    chars.append(Char(char, font, int(char_size), char_color))

        if chars:
            new_line()

        return cls(lines, spacing)

    @property
    def width(self) -> int:
        if not self.lines:
            return 0
        return max([line.width for line in self.lines])

    @property
    def height(self) -> int:
        if not self.lines:
            return 0
        return (
            sum([line.ascent for line in self.lines])
            + self.lines[-1].descent
            + self.spacing * (len(self.lines) - 1)
        )

    def wrap(self, width: float) -> "Text2Image":
        new_lines: List[Line] = []
        for line in self.lines:
            new_lines.extend(line.wrap(width))
        self.lines = new_lines
        return self

    def to_image(
        self, bg_color: Optional[ColorType] = None, padding: SizeType = (0, 0)
    ) -> IMG:
        img = Image.new(
            "RGBA",
            (int(self.width + padding[0] * 2), int(self.height + padding[1] * 2)),
            bg_color,  # type: ignore
        )

        top = padding[1]
        for line in self.lines:
            left = padding[0]  # "left"
            if line.align == "center":
                left += (self.width - line.width) / 2
            elif line.align == "right":
                left += self.width - line.width

            x = left
            if line.chars:
                x += line.chars[0].stroke_width
            for char in line.chars:
                y = top + line.ascent - char.ascent
                char.draw_on(img, (int(x), int(y)))
                x += char.width - char.stroke_width * 2
            top += line.ascent + self.spacing

        return img


def text2image(
    text: str,
    bg_color: ColorType = "white",
    padding: SizeType = (10, 10),
    max_width: Optional[int] = None,
    font_fallback: bool = True,
    **kwargs,
) -> IMG:
    """
    文字转图片，支持少量 `BBCode` 标签，具体见 `Text2Image` 类的 `from_bbcode_text` 函数

    :参数:
        * ``text``: 文本
        * ``bg_color``: 图片背景颜色
        * ``padding``: 图片边距
        * ``max_width``: 图片最大宽度，不设置则不限宽度
        * ``font_fallback``: 是否使用后备字体，默认为 `True`
    """
    text2img = Text2Image.from_bbcode_text(text, font_fallback=font_fallback, **kwargs)
    if max_width:
        text2img.wrap(max_width)
    return text2img.to_image(bg_color, padding)
