from pathlib import Path
from typing import List

from pydantic import BaseModel

meme_command_start: str = ""  # 命令前缀
memes_prompt_params_error: bool = False  # 是否在图片/文字数量不符或参数解析错误时提示（若没有设置命令前缀不建议开启，否则极易误触发）
memes_check_resources_on_startup: bool = True  # 是否在启动时检查 `meme-generator` 资源
memes_check_cfg_on_startup: bool = True  # 是否在启动时生成/修改配置文件，建议仅当第一次使用插件时或修改配置后开启
memes_use_sender_when_no_image: bool = False  # 在表情需要至少1张图且没有输入图片时，是否使用发送者的头像（谨慎使用，容易误触发）
memes_use_default_when_no_text: bool = False  # 在表情需要至少1段文字且没有输入文字时，是否使用默认文字（谨慎使用，容易误触发）
meme_disabled_list: List[str] = []  # 禁用的表情包列表，填写表情的 `key`


class MemeConfig(BaseModel):
    load_builtin_memes: bool = True  # 是否加载内置表情包
    meme_dirs: List[Path] = []  # 加载其他位置的表情包，填写文件夹路径
    meme_disabled_list = meme_disabled_list  # 禁用的表情包列表，填写表情的 `key`


class ResourceConfig(BaseModel):
    resource_url: str = (
        "https://ghproxy.com/https://raw.githubusercontent.com/MeetWq/meme-generator"
    )  # 下载内置表情包图片时的资源链接


class GifConfig(BaseModel):
    gif_max_size: float = 10  # 限制生成的 gif 文件大小，单位为 Mb
    gif_max_frames: int = 100  # 限制生成的 gif 文件帧数


class TranslatorConfig(BaseModel):
    baidu_trans_appid: str = ""  # 百度翻译api相关，表情包 `dianzhongdian` 需要使用
    baidu_trans_apikey: str = ""  # 可在 百度翻译开放平台 (http://api.fanyi.baidu.com) 申请


class ServerConfig(BaseModel):
    host: str = "127.0.0.1"  # web server 监听地址
    port: int = 2233  # web server 端口
