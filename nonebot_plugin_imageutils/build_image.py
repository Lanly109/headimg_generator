from io import BytesIO
from pathlib import Path
from typing import List, Optional, Type

import cv2
import numpy as np
from PIL import Image, ImageDraw
from PIL.Image import Image as IMG  # noqa
from PIL.ImageColor import getrgb
from PIL.ImageDraw import ImageDraw as Draw
from PIL.ImageFilter import Filter

from .gradient import Gradient
from .text2image import Text2Image
from .types import *


class BuildImage:
    def __init__(self, image: IMG):
        self.image = image

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    @property
    def size(self) -> SizeType:
        return self.image.size

    @property
    def mode(self) -> ModeType:
        return self.image.mode  # type: ignore

    @property
    def draw(self) -> Draw:
        return ImageDraw.Draw(self.image)

    @classmethod
    def new(
            cls, mode: ModeType, size: SizeType, color: Optional[ColorType] = None
    ) -> "BuildImage":
        return cls(Image.new(mode, size, color))  # type: ignore

    @classmethod
    def open(cls, file: Union[str, bytes, BytesIO, Path]) -> "BuildImage":
        return cls(Image.open(file))

    def copy(self) -> "BuildImage":
        return BuildImage(self.image.copy())

    def resize(
            self,
            size: SizeType,
            resample: ResampleType = Image.ANTIALIAS,
            keep_ratio: bool = False,
            inside: bool = False,
            direction: DirectionType = "center",
            bg_color: Optional[ColorType] = None,
            **kwargs
    ) -> "BuildImage":
        """
        调整图片尺寸

        :参数:
          * ``size``: 期望图片大小
          * ``keep_ratio``: 是否保持长宽比，默认为 `False`
          * ``inside``: `keep_ratio` 为 `True` 时，
                        若 `inside` 为 `True`，则调整图片大小至包含于期望尺寸，不足部分设为指定颜色；
                        若 `inside` 为 `False`，则调整图片大小至包含期望尺寸，超出部分裁剪
          * ``direction``: 调整图片大小时图片的方位；默认为居中
          * ``bg_color``: 不足部分设置的颜色
        """
        width, height = size
        if keep_ratio:
            if inside:
                ratio = min(width / self.width, height / self.height)
            else:
                ratio = max(width / self.width, height / self.height)
            width = int(self.width * ratio)
            height = int(self.height * ratio)

        image = BuildImage(
            self.image.resize((width, height), resample=resample, **kwargs)
        )

        if keep_ratio:
            image = image.resize_canvas(size, direction, bg_color)
        return image

    def resize_canvas(
            self,
            size: SizeType,
            direction: DirectionType = "center",
            bg_color: Optional[ColorType] = None,
    ) -> "BuildImage":
        """
        调整“画布”大小，超出部分裁剪，不足部分设为指定颜色

        :参数:
          * ``size``: 期望图片大小
          * ``direction``: 调整图片大小时图片的方位；默认为居中
          * ``bg_color``: 不足部分设置的颜色
        """
        w, h = size
        x = int((w - self.width) / 2)
        y = int((h - self.height) / 2)
        if direction in ["north", "northwest", "northeast"]:
            y = 0
        elif direction in ["south", "southwest", "southeast"]:
            y = h - self.height
        if direction in ["west", "northwest", "southwest"]:
            x = 0
        elif direction in ["east", "northeast", "southeast"]:
            x = w - self.width
        image = BuildImage.new(self.mode, size, bg_color)
        image.paste(self.image, (x, y))
        return image

    def resize_width(self, width: int, **kwargs) -> "BuildImage":
        """调整图片宽度，不改变长宽比"""
        return self.resize((width, int(self.height * width / self.width)), **kwargs)

    def resize_height(self, height: int, **kwargs) -> "BuildImage":
        """调整图片高度，不改变长宽比"""
        return self.resize((int(self.width * height / self.height), height), **kwargs)

    def rotate(
            self,
            angle: float,
            resample: ResampleType = Image.BICUBIC,
            expand: bool = False,
            **kwargs
    ) -> "BuildImage":
        """旋转图片"""
        image = BuildImage(
            self.image.rotate(angle, resample=resample, expand=expand, **kwargs)
        )
        return image

    def square(self) -> "BuildImage":
        """将图片裁剪为方形"""
        length = min(self.width, self.height)
        return self.resize_canvas((length, length))

    def circle(self) -> "BuildImage":
        """将图片裁剪为圆形"""
        image = self.square().image.convert("RGBA")
        mask = Image.new("L", (image.width * 10, image.height * 10), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, mask.width, mask.height), 255)
        mask = mask.resize(image.size, Image.ANTIALIAS)
        bg = Image.new("RGBA", image.size)
        return BuildImage(Image.composite(image, bg, mask))

    def circle_corner(self, r: float) -> "BuildImage":
        """将图片裁剪为圆角矩形"""
        image = self.image.convert("RGBA")
        mask = Image.new("L", (image.width * 10, image.height * 10), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, mask.width, mask.height), r * 10, fill=255)
        mask = mask.resize(image.size, Image.ANTIALIAS)
        bg = Image.new("RGBA", image.size)
        return BuildImage(Image.composite(image, bg, mask))

    def crop(self, box: BoxType) -> "BuildImage":
        """裁剪图片"""
        return BuildImage(self.image.crop(box))

    def convert(self, mode: ModeType, **kwargs) -> "BuildImage":
        return BuildImage(self.image.convert(mode, **kwargs))

    def paste(
            self,
            img: Union[IMG, "BuildImage"],
            pos: PosTypeInt = (0, 0),
            alpha: bool = False,
            below: bool = False,
    ) -> "BuildImage":
        """
        粘贴图片

        :参数:
          * ``img``: 待粘贴的图片
          * ``pos``: 粘贴位置
          * ``alpha``: 图片背景是否为透明
          * ``below``: 是否粘贴到底层
        """
        if isinstance(img, BuildImage):
            img = img.image
        new_img = Image.new(self.mode, self.size) if below else self.image.copy()
        if alpha:
            img = img.convert("RGBA")
            new_img.paste(img, pos, mask=img)
        else:
            new_img.paste(img, pos)
        if below:
            new_img.paste(self.image, mask=self.image if self.mode == "RGBA" else None)
        self.image = new_img
        return self

    def alpha_composite(
            self,
            img: Union[IMG, "BuildImage"],
            dest: PosTypeInt = (0, 0),
            source: Union[PosTypeInt, BoxType] = (0, 0),
    ) -> "BuildImage":
        if isinstance(img, BuildImage):
            img = img.image
        return BuildImage(self.image.alpha_composite(img, dest=dest, source=source))  # type: ignore

    def filter(self, filter: Union[Filter, Type[Filter]]) -> "BuildImage":  # noqa
        """滤波"""
        return BuildImage(self.image.filter(filter))

    def transpose(self, method: TransposeType) -> "BuildImage":
        """变换"""
        return BuildImage(self.image.transpose(method))

    def perspective(self, points: PointsTYpe) -> "BuildImage":
        """
        透视变换

        :参数:
          * ``points``: 变换后点的位置，顺序依次为：左上->右上->右下->左下
        """

        def find_coeffs(pa: PointsTYpe, pb: PointsTYpe):
            matrix = []
            for p1, p2 in zip(pa, pb):
                matrix.append(
                    [p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]]
                )
                matrix.append(
                    [0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]]
                )
            A = np.matrix(matrix, dtype=np.float32)
            B = np.array(pb).reshape(8)
            res = np.dot(np.linalg.inv(A.T * A) * A.T, B)
            return np.array(res).reshape(8)

        img_w, img_h = self.size
        points_w = [p[0] for p in points]
        points_h = [p[1] for p in points]
        new_w = int(max(points_w) - min(points_w))
        new_h = int(max(points_h) - min(points_h))
        p = ((0, 0), (img_w, 0), (img_w, img_h), (0, img_h))
        coeffs = find_coeffs(points, p)
        return BuildImage(
            self.image.transform(
                (new_w, new_h), Image.PERSPECTIVE, coeffs, Image.BICUBIC
            )
        )

    def gradient_color(self, gradient: Gradient) -> "BuildImage":
        """
        渐变色

        :参数:
          * ``gradient``: 渐变对象
        """
        return BuildImage(gradient.create_image(self.size))

    def motion_blur(self, angle: float = 0, degree: int = 0) -> "BuildImage":
        """
        运动模糊

        :参数:
          * ``angle``: 运动方向
          * ``degree``: 模糊程度
        """
        if degree == 0:
            return self.copy()
        matrix = cv2.getRotationMatrix2D((degree / 2, degree / 2), angle + 45, 1)
        kernel = np.diag(np.ones(degree))
        kernel = cv2.warpAffine(kernel, matrix, (degree, degree)) / degree
        blurred = cv2.filter2D(np.asarray(self.image), -1, kernel)  # noqa
        cv2.normalize(blurred, blurred, 0, 255, cv2.NORM_MINMAX)
        return BuildImage(Image.fromarray(np.array(blurred, dtype=np.uint8)))

    def distort(self, coefficients: DistortType) -> "BuildImage":
        """
        畸变

        :参数:
          * ``coefficients``: 畸变参数
        """
        res = cv2.undistort(
            np.asarray(self.image),  # noqa
            np.array([[100, 0, self.width / 2], [0, 100, self.height / 2], [0, 0, 1]]),
            np.asarray(coefficients),
        )
        return BuildImage(Image.fromarray(np.array(res, dtype=np.uint8)))

    def color_mask(self, color: ColorType) -> "BuildImage":
        """
        颜色滤镜，改变图片色调

        :参数:
          * ``color``: 目标颜色
        """
        img = self.image.convert("RGB")
        w, h = img.size
        img_array = np.asarray(img)  # noqa
        img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        img_hsl = cv2.cvtColor(img_array, cv2.COLOR_RGB2HLS)
        img_new = np.zeros((h, w, 3), np.uint8)

        if isinstance(color, str):
            color = getrgb(color)
        r = color[0]
        g = color[1]
        b = color[2]
        rgb_sum = sum(color)
        for i in range(h):
            for j in range(w):
                value = img_gray[i, j]
                new_color = (
                    [
                        int(value * r / rgb_sum),
                        int(value * g / rgb_sum),
                        int(value * b / rgb_sum),
                    ]
                    if rgb_sum
                    else [0, 0, 0]
                )
                img_new[i, j] = new_color
        img_new_hsl = cv2.cvtColor(img_new, cv2.COLOR_RGB2HLS)
        result = np.dstack(
            (img_new_hsl[:, :, 0], img_hsl[:, :, 1], img_new_hsl[:, :, 2])
        )
        result = cv2.cvtColor(result, cv2.COLOR_HLS2RGB)
        return BuildImage(Image.fromarray(result))

    def draw_point(
            self, pos: PosTypeFloat, fill: Optional[ColorType] = None
    ) -> "BuildImage":
        """在图片上画点"""
        self.draw.point(pos, fill=fill)
        return self

    def draw_line(
            self,
            xy: XYType,
            fill: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画直线"""
        self.draw.line(xy, fill=fill, width=width)
        return self

    def draw_rectangle(
            self,
            xy: XYType,
            fill: Optional[ColorType] = None,
            outline: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画矩形"""
        self.draw.rectangle(xy, fill, outline, width)
        return self

    def draw_rounded_rectangle(
            self,
            xy: XYType,
            radius: int = 0,
            fill: Optional[ColorType] = None,
            outline: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画圆角矩形"""
        self.draw.rounded_rectangle(xy, radius, fill, outline, width)
        return self

    def draw_polygon(
            self,
            xy: List[PosTypeFloat],
            fill: Optional[ColorType] = None,
            outline: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画多边形"""
        self.draw.polygon(xy, fill, outline, width)
        return self

    def draw_arc(
            self,
            xy: XYType,
            start: float,
            end: float,
            fill: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画圆弧"""
        self.draw.arc(xy, start, end, fill, width)
        return self

    def draw_ellipse(
            self,
            xy: XYType,
            fill: Optional[ColorType] = None,
            outline: Optional[ColorType] = None,
            width: float = 1,
    ) -> "BuildImage":
        """在图片上画圆"""
        self.draw.ellipse(xy, fill, outline, width)
        return self

    def draw_text(
            self,
            xy: XYType,
            text: str,
            max_fontsize: int = 30,
            min_fontsize: int = 12,
            allow_wrap: bool = False,
            style: FontStyle = "normal",
            weight: FontWeight = "normal",
            fill: ColorType = "black",
            spacing: int = 4,
            halign: HAlignType = "center",
            valign: VAlignType = "center",
            lines_align: HAlignType = "left",
            stroke_ratio: float = 0,
            stroke_fill: Optional[ColorType] = None,
            font_fallback: bool = True,
            fontname: str = "",
            fallback_fonts: List[str] = [],  # noqa
    ) -> "BuildImage":
        """
        在图片上指定区域画文字

        :参数:
          * ``xy``: 文字区域，顺序依次为 左，上，右，下
          * ``text``: 文字，支持多行
          * ``max_fontsize``: 允许的最大字体大小
          * ``min_fontsize``: 允许的最小字体大小
          * ``allow_wrap``: 是否允许折行
          * ``style``: 字体样式，默认为 "normal"
          * ``weight``: 字体粗细，默认为 "normal"
          * ``fill``: 文字颜色
          * ``spacing``: 多行文字间距
          * ``halign``: 横向对齐方式，默认为居中
          * ``valign``: 纵向对齐方式，默认为居中
          * ``lines_align``: 多行文字对齐方式，默认为靠左
          * ``stroke_ratio``: 文字描边的比例，即 描边宽度 / 字体大小
          * ``stroke_fill``: 描边颜色
          * ``font_fallback``: 是否使用后备字体，默认为 `True`
          * ``fontname``: 指定首选字体
          * ``fallback_fonts``: 指定备选字体
        """

        left = xy[0]
        top = xy[1]
        width = xy[2] - xy[0]
        height = xy[3] - xy[1]
        fontsize = max_fontsize
        while True:
            text2img = Text2Image.from_text(
                text,
                fontsize,
                style,
                weight,
                fill,
                spacing,
                lines_align,
                int(fontsize * stroke_ratio),
                stroke_fill,
                font_fallback,
                fontname,
                fallback_fonts,
            )
            text_w = text2img.width
            text_h = text2img.height
            if text_w > width and allow_wrap:
                text2img.wrap(width)
                text_w = text2img.width
                text_h = text2img.height
            if text_w > width or text_h > height:
                fontsize -= 1
                if fontsize < min_fontsize:
                    raise ValueError("在指定的区域和字体大小范围内画不下这段文字")
            else:
                x = left  # "left"
                if halign == "center":
                    x += (width - text_w) / 2
                elif halign == "right":
                    x += width - text_w

                y = top  # "top"
                if valign == "center":
                    y += (height - text_h) / 2
                elif valign == "bottom":
                    y += height - text_h

                text2img.draw_on_image(self.image, (int(x), int(y)))
                return self

    def draw_bbcode_text(
            self,
            xy: XYType,
            text: str,
            max_fontsize: int = 30,
            min_fontsize: int = 12,
            allow_wrap: bool = False,
            fill: ColorType = "black",
            spacing: int = 4,
            halign: HAlignType = "center",
            valign: VAlignType = "center",
            lines_align: HAlignType = "left",
            stroke_ratio: float = 0,
            stroke_fill: Optional[ColorType] = None,
            font_fallback: bool = True,
            fontname: str = "",
            fallback_fonts: List[str] = [],  # noqa
    ) -> "BuildImage":
        """
        在图片上指定区域画文字

        :参数:
          * ``xy``: 文字区域，顺序依次为 左，上，右，下
          * ``text``: 文字，支持多行
          * ``max_fontsize``: 允许的最大字体大小
          * ``min_fontsize``: 允许的最小字体大小
          * ``allow_wrap``: 是否允许折行
          * ``fill``: 文字颜色
          * ``spacing``: 多行文字间距
          * ``halign``: 横向对齐方式，默认为居中
          * ``valign``: 纵向对齐方式，默认为居中
          * ``lines_align``: 多行文字对齐方式，默认为靠左
          * ``stroke_ratio``: 文字描边的比例，即 描边宽度 / 字体大小
          * ``stroke_fill``: 描边颜色
          * ``font_fallback``: 是否使用后备字体，默认为 `True`
          * ``fontname``: 指定首选字体
          * ``fallback_fonts``: 指定备选字体
        """

        left = xy[0]
        top = xy[1]
        width = xy[2] - xy[0]
        height = xy[3] - xy[1]
        fontsize = max_fontsize
        while True:
            text2img = Text2Image.from_bbcode_text(
                text,
                fontsize,
                fill,
                spacing,
                lines_align,
                stroke_ratio,
                stroke_fill,
                font_fallback,
                fontname,
                fallback_fonts,
            )
            text_w = text2img.width
            text_h = text2img.height
            if text_w > width and allow_wrap:
                text2img.wrap(width)
                text_w = text2img.width
                text_h = text2img.height
            if text_w > width or text_h > height:
                fontsize -= 1
                if fontsize < min_fontsize:
                    raise ValueError("在指定的区域和字体大小范围内画不下这段文字")
            else:
                x = left  # "left"
                if halign == "center":
                    x += (width - text_w) / 2
                elif halign == "right":
                    x += width - text_w

                y = top  # "top"
                if valign == "center":
                    y += (height - text_h) / 2
                elif valign == "bottom":
                    y += height - text_h

                self.paste(text2img.to_image(), (int(x), int(y)), alpha=True)
                return self

    def save(self, format: str, **params) -> BytesIO:  # noqa
        output = BytesIO()
        self.image.save(output, format, **params)
        return output

    def save_jpg(self, bg_color: ColorType = "white") -> BytesIO:
        """
        保存图片为 jpg 格式

        :参数:
          * ``bg_color``: 由 png 转为 jpg 时的背景颜色，默认为白色
        """
        if self.mode == "RGBA":
            img = self.new("RGBA", self.size, bg_color)
            img.paste(self.image, alpha=True)
        else:
            img = self
        return img.convert("RGB").save("jpeg")

    def save_png(self) -> BytesIO:
        """保存图片为 png 格式"""
        return self.convert("RGBA").save("png")
