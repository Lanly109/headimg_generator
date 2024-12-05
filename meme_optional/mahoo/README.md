# mahoo
HoshinoBot娱乐插件，在群内生成游戏王卡图

# 安装
安装依赖`pip install opencc-python-reimplemented`
到`/hoshino/modules`目录下`git clone https://github.com/N-zi/mahoo`   
并在 `/hoshino/config/__bot__.py`的`MODULES_ON`处添加`mahoo`开启模块

# 指令

| 指令 | 说明 | 备注 |
| - | - | - |
| 召唤怪兽卡 + 图片 + 卡名（空格）描述 | 生成对应描述怪兽卡 | 如果选择图片时@sb，将会用对应用户的头像、昵称生成 |
| 发动魔法卡 + 图片 + 卡名（空格）描述 | 生成对应描述魔法卡 | 同上 |
| 发动陷阱卡 + 图片 + 卡名（空格）描述 | 生成对应描述陷阱卡 | 同上 |

# tips：

图片支持gif，gif太大或帧数太多酌情考虑服务器配置 

生成的图片会存在`/hoshino/modules/mahoo/out` 目录下 

<del>文字部分使用繁体，简体部分不显示</del>现已支持简体

