from pathlib import Path
from typing import List
import os

custom_font_path: Path = Path() / os.path.dirname(__file__) / '..' / 'resources' / 'fonts'
default_fallback_fonts: List[str] = [
    "Arial",
    "Tahoma",
    "Helvetica Neue",
    "Segoe UI",
    "PingFang SC",
    "Hiragino Sans GB",
    "Microsoft YaHei",
    "Source Han Sans SC",
    "Noto Sans SC",
    "Noto Sans CJK JP",
    "WenQuanYi Micro Hei",
    "Apple Color Emoji",
    "Noto Color Emoji",
    "Segoe UI Emoji",
    "Segoe UI Symbol",
]
