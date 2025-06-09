from pathlib import Path
from typing import List
from meme_generator.config import meme_config

meme_command_start: str = ""  # 命令前缀
memes_prompt_params_error: bool = (
    True  # 是否在图片/文字数量不符或参数解析错误时提示（若没有设置命令前缀不建议开启，否则极易误触发）
)
memes_check_resources_on_startup: bool = True  # 是否在启动时检查 `meme-generator` 资源
memes_use_sender_when_no_image: bool = (
    True  # 在表情需要至少1张图且没有输入图片时，是否使用发送者的头像（谨慎使用，容易误触发）
)
memes_use_default_when_no_text: bool = (
memes_normal_error: bool = (
    False  # 是否输出表情的相关错误提示，如获取图片失败、表情不存在等（谨慎使用，容易误触发）
)
meme_disabled_list: List[str] = []  # 禁用的表情包列表，填写表情的 `key`

baidu_trans_appid: str = ""
baidu_trans_apikey: str = ""

meme_config.translate.baidu_trans_appid = baidu_trans_appid
meme_config.translate.baidu_trans_apikey = baidu_trans_apikey
meme_config.meme.meme_dirs = [
    str(Path(__file__).parent / "meme_optional"),  # 本地额外表情包目录
    # str(Path(__file__).parent / "meme-generator-contrib" / "memes"),
]  # 第三方表情包目录
meme_config.dump()
