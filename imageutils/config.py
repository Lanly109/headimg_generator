from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    custom_font_path: Optional[Path] = None
    default_fallback_fonts: List[str] = [
        "SourceHanSansSC-Bold",
        "SourceHanSansSC-Regular",
        "NotoColorEmoji",
        "Arial",
        "consola",
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
        "Segoe UI Emoji",
        "Segoe UI Symbol",
    ]
