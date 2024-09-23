# headimg_generator

基于[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的制作头像相关的表情包插件。

移植自[nonebot-plugin-memes](https://github.com/noneplugin/nonebot-plugin-memes)，
后端由[meme-generator](https://github.com/MeetWq/meme-generator)驱动，
感谢[@MeetWq](https://github.com/MeetWq)以及参与该项目的所有成员！

## 更新日志
**2024.09.22**
- 移植nonebot2的pydantic v1 & v2 兼容层
**2024.09.22**
- 重构代码以修复源仓库在0.1版本后的破坏性更新。
  - ~~不再支持正则搜索表情包（因为源仓库已经删除了正则表达式）~~
  - 修复正则匹配表情包（调用源仓库接口）
  - 修复参数异常
  - 部分异常现在由源仓库接管
  - 兼容`pydantic 1.x`
- 以上感谢[@kcn3388](https://github.com/kcn3388)

<details>

<summary>更新历史</summary>

**2023.04.19**
- 重构代码，以匹配重构后的源仓库。具体配置看后文
- 注意：安装插件前请先卸载opencv：`pip uninstall opencv-python`
- 针对已经安装了本模块的用户：
  - 如果在`git clone`时没有抓取子模块：
    - 初始化本地子模块配置文件
      - `git submodule init`
    - 更新项目，抓取子模块内容。
      - `git submodule update`
- 如果想在`git clone`时抓取子模块：
  - `git clone --recursive https://GIT_REPO_URL`
- 以上感谢[@kcn3388](https://github.com/kcn3388)

**2023.01.09**
- 新增`恍惚`，`恐龙`，`挠头`，`鼓掌`，`追列车`，`万花筒`，`加班`，`头像公式`，`一直套娃`
- 修改`催刀`触发方式
- 以上感谢[@kcn3388](https://github.com/kcn3388)

**2022.12.09**
- 重构`催刀`，解决历史遗留问题，现在全部表情均支持emoji
- 重构生成帮助的函数，现在生成的帮助图片可以包含emoji
  - 同时被禁用的函数会变为灰色
- 以上感谢[@kcn3388](https://github.com/kcn3388)
**2022.12.08**
- 新增`咖波蹭`、`可莉吃`、`胡桃啃`、`踢球`、`砸`、`波奇手稿`、`坐得住`、`偷学`
- 同步源仓库bug修复
- 以上感谢[@kcn3388](https://github.com/kcn3388)

**2022.12.02**
- 实施[#23](https://github.com/Lanly109/headimg_generator/issues/23)，采用`Trie`树优化触发。优化`禁用表情、启用表情、随机表情`逻辑

**2022.11.15**
- 切换handle为`on_message`，彻底解决`一直`与`一直一直`冲突的问题。感谢[@kcn3388](https://github.com/kcn3388)
  - 同时修改`Handler`的固有变量为`command`数组，避免注册多个`trigger`带来的性能损失

**2022.11.14**
- 新增随机表情
  - 同步源repo
- 新增启用/禁用表情
  - 同步源repo
  - 支持同时启用/禁用多个表情
  - 参数附带`全局`会在全部群禁用
- 重构代码，现在image实现层与源repo一致，简化移植难度
    - 旧function已全部同步为源仓库，现在所有function都使用buildimage
        - **注意：不要使用pip安装`nonebot_plugin_imageutils`，该module依赖nonebot2**
    - 重命名相关库为正常名字，方便后续调整
    - 部分设置项移至`config.py`
        - 命令前缀、百度翻译apiID与Key、gif大小限制
    - 暂时取消移除用户名的emoji，有报错再加回去
    - ~~由于`on_keyword`限制，`一直一直`修改为`一一直`~~
    - 增加风控提醒
- 同步至最新表情
    - 新增`波纹`、`诈尸`、`卡比重锤`
- 以上感谢[@kcn3388](https://github.com/kcn3388)

**2022.10.23**
- 完善回复触发，适应回复多图情况
- 新增`怒撕、一直直、胡桃放大`指令

**2022.10.17**
- 新增`一起`指令
- 现在支持回复触发，逻辑如下：
    - 当回复对象是图片时，优先选择图片
    - 否则第一用户对象为回复的人
- 修复当使用emoji时的报错
- 新增触发词前缀设置(于`__init__.py`的`cmd_prefix`变量，默认触发词前加`#`）避免参数触发情况
- 以上感谢[@kcn3388](https://github.com/kcn3388)

**2022.10.12**
- 新增`打穿屏幕`、`击剑`、`抱大腿`、`唐可可举牌`、`无响应`、`抱紧`、`看扁`、`看图标`、`舰长`、`急急国王`、`不文明`
  指令，感谢[@kcn3388](https://github.com/kcn3388)

**2022.09.18**
- 新增`这是我的老婆`、`胡桃平板`、`敲黑板`、`上瘾`、`手枪`、`高血压`、`看书`、`遇到困难请拨打`、`迷惑`指令
- 由于懒得适配旧版的图片处理函数，直接搬了`nonebot-plugin-imageutils`[插件](https://github.com/noneplugin/nonebot-plugin-imageutils)，但字体选择方面还有点问题（新增的指令绘制的都是粗体，且大小似乎无法控制，容易因内容过长而无法绘制）
- 由于搬了`imageutils`插件，`requirements`有所更新，记得安装缺失的插件

**2022.08.07**
- 新增`远离`、`结婚申请`、`小画家`、`复读`、`防诱拐`、`字符画`、`催刀`、`共进晚餐`
  指令，感谢[@othinus001](https://github.com/othinus001)
- 资源见`resources`分支，可从`release`中下载，亦可同步`resources`分支，便于增量更新，亦可交由插件自行下载
- 插件缺少资源时会自行核对`resources`文件夹的完整性，对于损坏和缺失的文件会重新下载，但鉴于字体文件较大（`10MB+`
  ），由插件下载网速较慢，建议自行下载。
- 向`resources`分支增加图片时会自动更新`resource_list.json`和`release`，欢迎贡献资源于该分支

</details>

## 安装

在```HoshinoBot/hoshino/modules```目录下使用以下命令拉取本项目

```
git clone https://github.com/Lanly109/headimg_generator.git
```

如果需要安装额外的表情仓库则使用以下命令：

```
git clone --recursive https://github.com/Lanly109/headimg_generator.git
```

进入该目录后使用如下命令安装依赖

```
cd headimg_generator
pip install -r requirements.txt
```

然后在```HoshinoBot\hoshino\config\__bot__.py```文件的```MODULES_ON```加入```headimg_generator```

## 使用方法

发送`头像表情包`显示下图的列表：

<div align="left">
  <img src="./memes_cache_dir/default.jpg" width="400"  alt=""/>
</div>

> 以下内容摘自原插件README并对本插件作修改

### 配置项

> 以下配置项可在 `config.py` 文件中设置

#### `memes_command_start`
 - 类型：`str`
 - 默认：``
 - 说明：命令前缀

#### `memes_disabled_list`
 - 类型：`List[str]`
 - 默认：`[]`
 - 说明：禁用的表情包列表，需填写表情的`key`，可在 [meme-generator 表情列表](https://github.com/MeetWq/meme-generator/blob/main/docs/memes.md) 中查看。若只是临时关闭，可以用下文中的`表情包开关`

#### `memes_check_resources_on_startup`
 - 类型：`bool`
 - 默认：`True`
 - 说明：是否在启动时检查 `meme-generator` 资源

#### `memes_prompt_params_error`
 - 类型：`bool`
 - 默认：`False`
 - 说明：是否在图片/文字数量不符或参数解析错误时提示（若没有设置命令前缀不建议开启，否则极易误触发）

#### `memes_use_sender_when_no_image`
 - 类型：`bool`
 - 默认：`False`
 - 说明：在表情需要至少1张图且没有输入图片时，是否使用发送者的头像（谨慎使用，容易误触发）

#### `memes_use_default_when_no_text`
 - 类型：`bool`
 - 默认：`False`
 - 说明：在表情需要至少1段文字且没有输入文字时，是否使用默认文字（谨慎使用，容易误触发）

#### `load_builtin_memes`
 - 类型：`bool`
 - 默认：`True`
 - 说明：是否加载内置表情包

#### `meme_dirs` = []
 - 类型：`List[Path]`
 - 默认：`[]`
 - 说明：加载其他位置的表情包，填写文件夹路径

#### `resource_url`
 - 类型：`str`
 - 默认：`https://ghproxy.com/https://raw.githubusercontent.com/MeetWq/meme-generator`
 - 说明：下载内置表情包图片时的资源链接

#### `gif_max_size`
 - 类型：`float`
 - 默认：`10.0`
 - 说明：限制生成的 gif 文件大小，单位为 Mb

#### `gif_max_frames`
 - 类型：`int`
 - 默认：`100`
 - 说明：限制生成的 gif 文件帧数

#### `baidu_trans_appid`
 - 类型：`str`
 - 默认：``
 - 说明：百度翻译api相关，表情包 `dianzhongdian` 需要使用

#### `baidu_trans_apikey`
 - 类型：`str`
 - 默认：``
 - 说明：可在 百度翻译开放平台 (http://api.fanyi.baidu.com) 申请

#### `host`
 - 类型：`str`
 - 默认：`127.0.0.1`
 - 说明：web server 监听地址

#### `port`
 - 类型：`int`
 - 默认：`2233`
 - 说明：web server 端口

### 中文字体 和 emoji字体 安装

根据系统的不同，推荐安装的字体如下：

- Windows:

大部分 Windows 系统自带 [微软雅黑](https://learn.microsoft.com/zh-cn/typography/font-list/microsoft-yahei) 中文字体 和 [Segoe UI Emoji](https://learn.microsoft.com/zh-cn/typography/font-list/segoe-ui-emoji) emoji 字体，一般情况下无需额外安装

- Linux:

部分系统可能自带 [文泉驿微米黑](http://wenq.org/wqy2/index.cgi?MicroHei) 中文字体；

对于 Ubuntu 系统，推荐安装 Noto Sans CJK 和 Noto Color Emoji：

```bash
sudo apt install fonts-noto-cjk fonts-noto-color-emoji
```

为避免 Noto Sans CJK 中部分中文显示为异体（日文）字形，可以将简体中文设置为默认语言（详见 [ArchWiki](https://wiki.archlinux.org/title/Localization/Simplified_Chinese?rdfrom=https%3A%2F%2Fwiki.archlinux.org%2Findex.php%3Ftitle%3DLocalization_%28%25E7%25AE%2580%25E4%25BD%2593%25E4%25B8%25AD%25E6%2596%2587%29%2FSimplified_Chinese_%28%25E7%25AE%2580%25E4%25BD%2593%25E4%25B8%25AD%25E6%2596%2587%29%26redirect%3Dno#%E4%BF%AE%E6%AD%A3%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87%E6%98%BE%E7%A4%BA%E4%B8%BA%E5%BC%82%E4%BD%93%EF%BC%88%E6%97%A5%E6%96%87%EF%BC%89%E5%AD%97%E5%BD%A2)）：

```bash
sudo locale-gen zh_CN zh_CN.UTF-8
sudo update-locale LC_ALL=zh_CN.UTF-8 LANG=zh_CN.UTF-8
fc-cache -fv
```

其他 Linux 系统可以自行下载字体文件安装：

思源黑体：https://github.com/adobe-fonts/source-han-sans

NotoSansSC：https://fonts.google.com/noto/specimen/Noto+Sans+SC

Noto Color Emoji：https://github.com/googlefonts/noto-emoji


- Mac:

苹果系统一般自带 "PingFang SC" 中文字体 与 "Apple Color Emoji" emoji 字体

### 其他字体安装

某些表情包需要用到一些额外字体，存放于仓库中 [resources/fonts](https://github.com/MeetWq/meme-generator/tree/main/resources/fonts)，需要自行下载安装

具体字体及对应的表情如下：

| 字体名                                                                          | 字体文件名                                                                                                                 | 用到该字体的表情                       | 备注        |
|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|--------------------------------|-----------|
| [Consolas](https://learn.microsoft.com/zh-cn/typography/font-list/consolas)  | [consola.ttf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/consola.ttf)                         | `charpic`                      |           |
| [FZKaTong-M19S](https://www.foundertype.com/index.php/FontInfo/index/id/136) | [FZKATJW.ttf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/FZKATJW.ttf)                         | `capoo_say`                    | 方正卡通      |
| [FZXS14](https://www.foundertype.com/index.php/FontInfo/index/id/208)        | [FZXS14.ttf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/FZXS14.ttf)                           | `nokia`                        | 方正像素14    |
| [FZSJ-QINGCRJ](https://www.foundertype.com/index.php/FontInfo/index/id/5178) | [FZSJ-QINGCRJ.ttf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/FZSJ-QINGCRJ.ttf)               | `psyduck`                      | 方正手迹-青春日记 |
| [FZShaoEr-M11S](https://www.foundertype.com/index.php/FontInfo/index/id/149) | [FZSEJW.ttf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/FZSEJW.ttf)                           | `raise_sign`、`nekoha_holdsign` | 方正少儿      |
| [NotoSansSC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)            | [NotoSansSC-Regular.otf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/NotoSansSC-Regular.otf)   | `5000choyen`                   |           |
| [NotoSerifSC](https://fonts.google.com/noto/specimen/Noto+Serif+SC)          | [NotoSerifSC-Regular.otf](https://github.com/MeetWq/meme-generator/blob/main/resources/fonts/NotoSerifSC-Regular.otf) | `5000choyen`                   |           |

### 字体安装方式

不同系统的字体安装方式：

- Windows:
    - 双击通过字体查看器安装
    - 复制到字体文件夹：`C:\Windows\Fonts`

- Linux:

在 `/usr/share/fonts` 目录下新建文件夹，如 `myfonts`，将字体文件复制到该路径下；

运行如下命令建立字体缓存：

```bash
fc-cache -fv
```

- Mac:

使用字体册打开字体文件安装

### 使用

#### 表情列表

发送 `表情包制作` 查看表情列表

> **Note**
>
> 插件会缓存生成的表情列表图片以避免重复生成
>
> 若因为字体没安装好等原因导致生成的图片不正常，需要删除缓存的图片
>
> 缓存路径：
> - `./memes_cache_dir`

发送 `更新表情包制作` 更新表情资源

#### 表情帮助

- 发送 `表情详情 + 表情名/关键词` 查看 表情详细信息 和 表情预览

示例：

<div align="left">
  <img src="https://s2.loli.net/2023/03/10/1glyUrwELCHMfkT.png" width="250"  alt=""/>
</div>

#### 表情包开关

群主 / 管理员 / 超级用户 可以启用或禁用某些表情包

发送 `启用表情/禁用表情 [表情名/表情关键词]`，如：`禁用表情 摸`

超级用户 可以设置某个表情包的管控模式（黑名单/白名单）

发送 `全局启用表情 [表情名/表情关键词]` 可将表情设为黑名单模式；

发送 `全局禁用表情 [表情名/表情关键词]` 可将表情设为白名单模式；

#### 表情使用

发送 `关键词 + 图片/文字` 制作表情

可使用 `自己`、`@某人` 获取指定用户的头像作为图片

可使用 `@ + 用户id` 指定任意用户获取头像，如 `摸 @114514`

可回复包含图片的消息作为图片输入

示例：

<div align="left">
  <img src="https://s2.loli.net/2023/03/10/UDTOuPnwk3emxv4.png" width="250"  alt=""/>
</div>

#### 随机表情

发送 `随机表情 + 图片/文字` 可随机制作表情

随机范围为 图片/文字 数量符合要求的表情


**注意事项**

- 为避免误触发，当输入的 图片/文字 数量不符时，不会进行提示，可事先通过 `表情详情` 查看所需的图文数

### 支持的指令

请访问[源仓库](https://github.com/MeetWq/meme-generator/blob/main/docs/memes.md)查看
