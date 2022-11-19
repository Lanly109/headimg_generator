import numpy as np
from PIL import Image
from PIL.ImageColor import getrgb
from PIL.Image import Image as IMG  # noqa
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ColorType, SizeType, XYType


class ColorStop:
    def __init__(self, stop: float, color: "ColorType"):
        self.stop = stop
        """介于 0.0 与 1.0 之间的值，表示渐变中开始与结束之间的位置"""
        if isinstance(color, str):
            color = getrgb(color)
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)
        self.color = color
        """在 stop 位置显示的颜色值"""

    def __lt__(self, other: "ColorStop"):
        return self.stop < other.stop


class Gradient:
    def __init__(self, color_stops: List[ColorStop] = []):  # noqa
        self.color_stops = color_stops
        self.color_stops.sort()

    def add_color_stop(self, stop: float, color: "ColorType"):
        self.color_stops.append(ColorStop(stop, color))
        self.color_stops.sort()

    def create_image(self, size: "SizeType") -> IMG:
        raise NotImplementedError


class LinearGradient(Gradient):
    def __init__(self, xy: "XYType", color_stops: List[ColorStop] = []):  # noqa
        self.xy = xy
        self.x0 = xy[0]
        """渐变开始点的 x 坐标"""
        self.y0 = xy[1]
        """渐变开始点的 y 坐标"""
        self.x1 = xy[2]
        """渐变结束点的 x 坐标"""
        self.y1 = xy[3]
        """渐变结束点的 y 坐标"""
        super().__init__(color_stops)

    def create_image(self, size: "SizeType") -> IMG:
        w = size[0]
        h = size[1]
        x0 = self.x0
        y0 = self.y0
        x1 = self.x1
        y1 = self.y1
        x01 = x1 - x0
        y01 = y1 - y0
        d = x01 ** 2 + y01 ** 2
        arr = np.zeros([h, w, 4], np.uint8)
        if len(self.color_stops) == 1:
            arr[:, :, :] = self.color_stops[0].color
        elif self.color_stops:
            for x in range(w):
                for y in range(h):
                    x0p = x - x0
                    y0p = y - y0
                    ratio = (x0p * x01 + y0p * y01) / d
                    color = (0, 0, 0, 0)
                    if ratio < 0:
                        color = self.color_stops[0].color
                    if ratio >= 1:
                        color = self.color_stops[-1].color
                    for i in range(len(self.color_stops) - 1):
                        color_stop0 = self.color_stops[i]
                        color_stop1 = self.color_stops[i + 1]
                        stop0 = color_stop0.stop
                        stop1 = color_stop1.stop
                        color0 = color_stop0.color
                        color1 = color_stop1.color
                        if stop0 <= ratio < stop1:
                            e = (ratio - stop0) / (stop1 - stop0)
                            color = [
                                round((1 - e) * color0[j] + e * color1[j])
                                for j in range(4)
                            ]
                    arr[y, x, :] = color
        return Image.fromarray(arr)


if __name__ == "__main__":
    img = LinearGradient(
        (0, 0, 255, 255),
        [
            ColorStop(0, "red"),
            ColorStop(0.1, "orange"),
            ColorStop(0.25, "yellow"),
            ColorStop(0.4, "green"),
            ColorStop(0.6, "blue"),
            ColorStop(0.8, "cyan"),
            ColorStop(1, "purple"),
        ],
    ).create_image((255, 255))
    img.save("test.png")
