# headimg_generator

基于[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的制作头像相关的表情包插件。

移植自[nonebot-plugin-petpet](https://github.com/noneplugin/nonebot-plugin-petpet)
，感谢[@MeetWq](https://github.com/MeetWq)以及参与该项目的所有成员！

## 更新日志

**2022.11.14**

- 新增随机表情
  - 同步源repo
- 新增启用/禁用表情
  - 同步源repo
  - 支持同时启用/禁用多个表情
  - 参数附带`全局`会在全部群禁用
- 重构代码，现在实现层与源repo移植，简化移植难度
    - 旧function已全部同步为源仓库，现在所有function都使用buildimage
        - **注意：不要使用pip安装`nonebot_plugin_imageutils`，该module依赖nonebot2**
    - 重命名相关库为正常名字，方便后续调整
    - 部分设置项移至`config.py`
        - 命令前缀、百度翻译apiID与Key、gif大小限制
    - 暂时取消移除用户名的emoji，有报错再加回去
    - 由于`on_keyword`限制，`一直一直`修改为`一一直`
    - 增加风控提醒
- 同步至最新表情
    - 新增`波纹、诈尸、卡比重锤`

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
-

由于懒得适配旧版的图片处理函数，直接搬了`nonebot-plugin-imageutils`[插件](https://github.com/noneplugin/nonebot-plugin-imageutils)
，但字体选择方面还有点问题（新增的指令绘制的都是粗体，且大小似乎无法控制，容易因内容过长而无法绘制）

- 由于搬了`imageutils`插件，`requirements`有所更新，记得安装缺失的插件

**2022.08.07**

- 新增`远离`、`结婚申请`、`小画家`、`复读`、`防诱拐`、`字符画`、`催刀`、`共进晚餐`
  指令，感谢[@othinus001](https://github.com/othinus001)
- 资源见`resources`分支，可从`release`中下载，亦可同步`resources`分支，便于增量更新，亦可交由插件自行下载
- 插件缺少资源时会自行核对`resources`文件夹的完整性，对于损坏和缺失的文件会重新下载，但鉴于字体文件较大（`10MB+`
  ），由插件下载网速较慢，建议自行下载。
- 向`resources`分支增加图片时会自动更新`resource_list.json`和`release`，欢迎贡献资源于该分支

## 安装

在```HoshinoBot/hoshino/modules```目录下使用以下命令拉取本项目

```
git clone https://github.com/Lanly109/headimg_generator.git
```

进入该目录后使用如下命令安装依赖

```
cd headimg_generator
pip install -r requirements.txt
```

`python 3.6`以下的还需安装以下依赖（[#1](https://github.com/Lanly109/headimg_generator/issues/1)）

```bash
pip install dataclasses
``` 

下载`releases`中的`resources.zip`，解压文件至`resources/`下，放置情况如下（注意`fonts`文件夹下无`fonts`文件夹，`images`同理）

```bash
.
└── resources
    ├── fonts
    └── images
``` 

然后在```HoshinoBot\hoshino\config\__bot__.py```文件的```MODULES_ON```加入```headimg_generator```

`imageutils`的字体安装方法请参照[原插件仓库](https://github.com/noneplugin/nonebot-plugin-imageutils)的`README`

## 使用方法

发送`帮助头像表情包`显示下图的列表：

<div align="left">
  <img src="https://s2.loli.net/2022/11/09/xazi1q8JsfEmdhC.jpg" width="400" />
</div>

> 以下内容摘自原插件README

### 触发方式

- 指令 + @user，如： 爬 @小Q
- 指令 + 回复消息，如： [回复消息] 爬
- 指令 + qq号，如：爬 123456
- 指令 + 自己，如：爬 自己
- 指令 + 图片，如：爬 [图片]

前三种触发方式会使用目标qq的头像作为图片

### 随机表情

随机表情 + @user/qq号/自己/图片

如：`随机表情 自己`

会在未禁用的表情中随机选取一个制作表情包

### 表情包开关

群主 / 管理员 / 超级用户 可以启用或禁用某些表情包

发送 `启用表情/禁用表情 [表情名]`，如：`禁用表情 摸`、`启用表情 petpet 贴 爬`

超级用户 可以设置某个表情包的管控模式（黑名单/白名单）

发送 `启用表情 [全局] [表情名]` 可将表情设为黑名单模式；

发送 `禁用表情 [全局] [表情名]` 可将表情设为白名单模式；

### 支持的指令

<details>
<summary>展开/收起</summary>

| 指令                          | 效果                                                                           | 备注                                                                 |
|-----------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------|
| 万能表情<br>空白表情                | <img src="https://s2.loli.net/2022/05/29/C2VRA6iw4hzWZXO.jpg" width="200" /> | 简单的图片加文字                                                           |
| 摸<br>摸摸<br>摸头<br>摸摸头<br>rua | <img src="https://s2.loli.net/2022/02/23/oNGVO4iuCk73g8S.gif" width="200" /> | 可使用参数“圆”让头像为圆形<br>如：摸头圆 自己                                         |
| 亲<br>亲亲                     | <img src="https://s2.loli.net/2022/02/23/RuoiqP8plJBgw9K.gif" width="200" /> | 可指定一个或两个目标<br>若为一个则为 发送人 亲 目标<br>若为两个则为 目标1 亲 目标2<br>如：亲 114514 自己 |
| 贴<br>贴贴<br>蹭<br>蹭蹭          | <img src="https://s2.loli.net/2022/02/23/QDCE5YZIfroavub.gif" width="200" /> | 可指定一个或两个目标<br>类似 亲                                                 |
| 顶<br>玩                      | <img src="https://s2.loli.net/2022/08/16/WVotKxjqupdCJAS.gif" width="200" /> |                                                                    |
| 拍                           | <img src="https://s2.loli.net/2022/02/23/5mv6pFJMNtzHhcl.gif" width="200" /> |                                                                    |
| 撕                           | <img src="https://s2.loli.net/2022/05/29/FDcam9ROPkqvwxH.jpg" width="200" >  |                                                                    |
| 怒撕                          | <img src="https://s2.loli.net/2022/10/11/NepC3ETugIaWnHs.jpg" width="200" >  |                                                                    |
| 丢<br>扔                      | <img src="https://s2.loli.net/2022/02/23/LlDrSGYdpcqEINu.jpg" width="200" /> |                                                                    |
| 抛<br>掷                      | <img src="https://s2.loli.net/2022/03/10/W8X6cGZS5VMDOmh.gif" width="200" /> |                                                                    |
| 爬                           | <img src="https://s2.loli.net/2022/02/23/hfmAToDuF2actC1.jpg" width="200" /> | 默认为随机选取一张爬表情<br>可使用数字指定特定表情<br>如：爬 13 自己                           |
| 精神支柱                        | <img src="https://s2.loli.net/2022/02/23/WwjNmiz4JXbuE1B.jpg" width="200" /> |                                                                    |
| 一直                          | <img src="https://s2.loli.net/2022/02/23/dAf9Z3kMDwYcRWv.gif" width="200" /> | 支持gif                                                              |
| 一一直                         | <img src="https://s2.loli.net/2022/10/15/hn5Q4jm29pXNsrL.gif" width="200" /> | 支持gif                                                              |
| 加载中                         | <img src="https://s2.loli.net/2022/02/23/751Oudrah6gBsWe.gif" width="200" /> | 支持gif                                                              |
| 转                           | <img src="https://s2.loli.net/2022/02/23/HoZaCcDIRgs784Y.gif" width="200" /> |                                                                    |
| 小天使                         | <img src="https://s2.loli.net/2022/02/23/ZgD1WSMRxLIymCq.jpg" width="200" /> | 图中名字为目标qq昵称<br>可指定名字，如：小天使 meetwq 自己                               |
| 不要靠近                        | <img src="https://s2.loli.net/2022/02/23/BTdkAzvhRDLOa3U.jpg" width="200" /> |                                                                    |
| 一样                          | <img src="https://s2.loli.net/2022/02/23/SwAXoOgfdjP4ecE.jpg" width="200" /> |                                                                    |
| 滚                           | <img src="https://s2.loli.net/2022/02/23/atzZsSE53UDIlOe.gif" width="200" /> |                                                                    |
| 玩游戏<br>来玩游戏                 | <img src="https://s2.loli.net/2022/05/31/j9ZKB7cFOSklzMe.jpg" width="200" /> | 图中描述默认为：来玩休闲游戏啊<br>可指定描述<br>支持gif                                  |
| 膜<br>膜拜                     | <img src="https://s2.loli.net/2022/02/23/nPgBJwV5qDb1s9l.gif" width="200" /> |                                                                    |
| 吃                           | <img src="https://s2.loli.net/2022/02/23/ba8cCtIWEvX9sS1.gif" width="200" /> |                                                                    |
| 啃                           | <img src="https://s2.loli.net/2022/02/23/k82n76U4KoNwsr3.gif" width="200" /> |                                                                    |
| 出警                          | <img src="https://s2.loli.net/2022/05/31/Q7WL1q2TlHgnERr.jpg" width="200" /> |                                                                    |
| 警察                          | <img src="https://s2.loli.net/2022/03/12/xYLgKVJcd3HvqfM.jpg" width="200" >  |                                                                    |
| 问问<br>去问问                   | <img src="https://s2.loli.net/2022/02/23/GUyax1BF6q5Hvin.jpg" width="200" /> | 名字为qq昵称，可指定名字                                                      |
| 舔<br>舔屏<br>prpr             | <img src="https://s2.loli.net/2022/03/05/WMHpwygtmN5bdEV.jpg" width="200" /> | 支持gif                                                              |
| 搓                           | <img src="https://s2.loli.net/2022/03/09/slRF4ue56xSQzra.gif" width="200" /> |                                                                    |
| 墙纸                          | <img src="https://s2.loli.net/2022/10/01/wm3pFvEZeUctA4J.gif" width="200" /> |                                                                    |
| 国旗                          | <img src="https://s2.loli.net/2022/03/10/p7nwCvgsU3LxBDI.jpg" width="200" /> |                                                                    |
| 交个朋友                        | <img src="https://s2.loli.net/2022/03/10/SnmkNrjKuFeZvbA.jpg" width="200" /> | 名字为qq昵称，可指定名字                                                      |
| 继续干活<br>打工人                 | <img src="https://s2.loli.net/2022/04/20/LIak2BsJ9Dd5O7l.jpg" width="200" >  |                                                                    |
| 完美<br>完美的                   | <img src="https://s2.loli.net/2022/03/10/lUS1nmPAKIYtwih.jpg" width="200" /> |                                                                    |
| 关注                          | <img src="https://s2.loli.net/2022/03/12/FlpjRWCte72ozqs.jpg" width="200" >  | 名字为qq昵称，可指定名字                                                      |
| 我朋友说<br>我有个朋友说              | <img src="https://s2.loli.net/2022/03/12/cBk4aG3RwIoYbMF.jpg" width="200" >  | 没有图片则使用发送者的头像<br>可指定名字<br>如“我朋友张三说 来份涩图”                           |
| 这像画吗                        | <img src="https://s2.loli.net/2022/03/12/PiSAM1T6EvxXWgD.jpg" width="200" >  |                                                                    |
| 震惊                          | <img src="https://s2.loli.net/2022/03/12/4krO6y53bKzYpUg.gif" width="200" >  |                                                                    |
| 兑换券                         | <img src="https://s2.loli.net/2022/03/12/6tS7dDaprb1sUxj.jpg" width="200" >  | 默认文字为：qq昵称 + 陪睡券<br>可指定文字                                          |
| 听音乐                         | <img src="https://s2.loli.net/2022/03/15/rjgvbXeOJtIW8fF.gif" width="200" >  |                                                                    |
| 典中典                         | <img src="https://s2.loli.net/2022/03/18/ikQ1IB6hS4x3EjD.jpg" width="200" >  |                                                                    |
| 哈哈镜                         | <img src="https://s2.loli.net/2022/03/15/DwRPaErSNZWXGgp.gif" width="200" >  |                                                                    |
| 永远爱你                        | <img src="https://s2.loli.net/2022/03/15/o6mhWk7crwdepU5.gif" width="200" >  |                                                                    |
| 对称                          | <img src="https://s2.loli.net/2022/03/15/HXntCy8kc7IRZxp.jpg" width="200" >  | 可使用参数“上”、“下”、“左”、“右”指定对称方向<br>支持gif                                |
| 安全感                         | <img src="https://s2.loli.net/2022/03/15/58pPzrgxJNkUYRT.jpg" width="200" >  | 可指定描述                                                              |
| 永远喜欢<br>我永远喜欢               | <img src="https://s2.loli.net/2022/03/15/EpTiUbcoVGCXLkJ.jpg" width="200" >  | 图中名字为目标qq昵称<br>可指定名字<br>可指定多个目标叠buff                               |
| 采访                          | <img src="https://s2.loli.net/2022/03/15/AYpkWEc2BrXhKeU.jpg" width="200" >  | 可指定描述                                                              |
| 打拳                          | <img src="https://s2.loli.net/2022/03/18/heA9fCPMQWXBxTn.gif" width="200" >  |                                                                    |
| 群青                          | <img src="https://s2.loli.net/2022/03/18/drwXx3yK14IMVCf.jpg" width="200" >  |                                                                    |
| 捣                           | <img src="https://s2.loli.net/2022/03/30/M9xUehlV64OpGoY.gif" width="200" >  |                                                                    |
| 捶                           | <img src="https://s2.loli.net/2022/03/30/ElnARr7ohVXjtJx.gif" width="200" >  |                                                                    |
| 需要<br>你可能需要                 | <img src="https://s2.loli.net/2022/03/30/VBDG74QeZUYcunh.jpg" width="200" >  |                                                                    |
| 捂脸                          | <img src="https://s2.loli.net/2022/03/30/NLy4Eb6CHKP3Svo.jpg" width="200" >  |                                                                    |
| 敲                           | <img src="https://s2.loli.net/2022/04/14/uHP8z3bDMtGdOCk.gif" width="200" >  |                                                                    |
| 垃圾<br>垃圾桶                   | <img src="https://s2.loli.net/2022/04/14/i1ok2NUYaMfKezT.gif" width="200" >  |                                                                    |
| 为什么@我<br>为什么at我             | <img src="https://s2.loli.net/2022/04/14/qQYydurABV7TMbN.jpg" width="200" >  |                                                                    |
| 像样的亲亲                       | <img src="https://s2.loli.net/2022/04/14/1KvLjb2uRYQ9mCI.jpg" width="200" >  |                                                                    |
| 啾啾                          | <img src="https://s2.loli.net/2022/04/20/v3YrbLMnND8BoPK.gif" width="200" >  |                                                                    |
| 吸<br>嗦                      | <img src="https://s2.loli.net/2022/04/20/LlFNscXC1IQrkgE.gif" width="200" >  |                                                                    |
| 锤                           | <img src="https://s2.loli.net/2022/04/20/ajXFm95tHRM6CzZ.gif" width="200" >  |                                                                    |
| 紧贴<br>紧紧贴着                  | <img src="https://s2.loli.net/2022/04/20/FiBwc3ZxvVLObGP.gif" width="200" >  |                                                                    |
| 注意力涣散                       | <img src="https://s2.loli.net/2022/05/11/mEtyxoZ3DfwBCn5.jpg" width="200" >  |                                                                    |
| 阿尼亚喜欢                       | <img src="https://s2.loli.net/2022/08/16/PNCZxzqvV9uDFEf.jpg" width="200" >  | 支持gif                                                              |
| 想什么                         | <img src="https://s2.loli.net/2022/05/18/ck1jNO2K8Qd6Lo3.jpg" width="200" >  | 支持gif                                                              |
| 远离                          | <img src="https://s2.loli.net/2022/05/31/lqyOu25WPTsGBcb.jpg" width="200" >  | 可指定多个目标                                                            |
| 结婚申请<br>结婚登记                | <img src="https://s2.loli.net/2022/05/31/tZR3ls7cBrdGHTL.jpg" width="200" >  |                                                                    |
| 小画家                         | <img src="https://s2.loli.net/2022/06/23/KCD73EbgqzWFxr4.jpg" width="200" >  |                                                                    |
| 复读                          | <img src="https://s2.loli.net/2022/08/16/E6vgRCt3MSLfAWU.gif" width="200" >  | 复读内容默认为“救命啊”<br>可指定多个目标                                            |
| 防诱拐                         | <img src="https://s2.loli.net/2022/07/21/ve6lcYaiV4wfhHg.jpg" width="200" >  |                                                                    |
| 字符画                         | <img src="https://s2.loli.net/2022/07/21/R58eG7mVZWPp1Cy.jpg" width="200" >  | 支持gif                                                              |                                                          |
| 催刀                          | <img src="https://s2.loli.net/2022/08/07/9UZeilHQWXIf2mF.jpg" width="200" >  |                                                                    |
| 共进晚餐                        | <img src="https://s2.loli.net/2022/08/07/QSyceaFHwEKVRPX.jpg" width="200" >  |                                                                    |
| 我老婆                         | <img src="https://s2.loli.net/2022/08/16/7wPht5rp6sk1ZCq.jpg" width="200" >  |                                                                    |
| 胡桃平板                        | <img src="https://s2.loli.net/2022/08/16/Mc5HvfB6ywqLQiV.jpg" width="200" >  | 支持gif                                                              |
| 胡桃放大                        | <img src="https://s2.loli.net/2022/10/01/ISotJVp1xOfgvlq.gif" width="200" >  | 支持gif                                                              |
| 讲课<br>敲黑板                   | <img src="https://s2.loli.net/2022/08/16/VpdIHsteKocgRzP.jpg" width="200" >  | 支持gif                                                              |
| 上瘾<br>毒瘾发作                  | <img src="https://s2.loli.net/2022/08/26/WAVDFfJB7tH5z3y.jpg" width="200" >  | 支持gif                                                              |
| 手枪                          | <img src="https://s2.loli.net/2022/08/26/MRO3mqvfbaxkB1t.jpg" width="200" >  |                                                                    |
| 高血压                         | <img src="https://s2.loli.net/2022/08/26/9qbyN2h38MAkRZE.jpg" width="200" >  | 支持gif                                                              |
| 看书                          | <img src="https://s2.loli.net/2022/08/26/SeAC86RgDlUvLNY.jpg" width="200" >  |                                                                    |
| 遇到困难请拨打                     | <img src="https://s2.loli.net/2022/08/26/KWGSf6qErB14uwp.jpg" width="200" >  | 可指定一个或两个目标                                                         |
| 迷惑                          | <img src="https://s2.loli.net/2022/10/01/WqfAXNpD8JkVnUH.gif" width="200" >  | 支持gif                                                              |
| 打穿<br>打穿屏幕                  | <img src="https://s2.loli.net/2022/10/01/ndxBbC1TKeRYv9X.gif" width="200" >  | 支持gif                                                              |
| 击剑<br>🤺                    | <img src="https://s2.loli.net/2022/10/01/97uZYdFs16CkJhQ.gif" width="200" >  |                                                                    |
| 抱大腿                         | <img src="https://s2.loli.net/2022/10/01/mivPkLle6qwZQsg.gif" width="200" >  |                                                                    |
| 唐可可举牌                       | <img src="https://s2.loli.net/2022/10/01/LdGk9MmzYaebFt5.gif" width="200" >  |                                                                    |
| 无响应                         | <img src="https://s2.loli.net/2022/10/01/vjXnOgcSVLGfdCQ.jpg" width="200" >  |                                                                    |
| 抱紧                          | <img src="https://s2.loli.net/2022/10/01/vYgl3nRmXuGwqDd.jpg" width="200" >  |                                                                    |
| 看扁                          | <img src="https://s2.loli.net/2022/10/08/kAHs6GYnmRh28WB.jpg" width="200" >  | 支持gif<br>可指定描述<br>可指定缩放倍率，默认为2<br>如：看扁 3 自己                        |
| 看图标                         | <img src="https://s2.loli.net/2022/10/08/Ek8Vu6eFyQKJnos.jpg" width="200" >  | 支持gif<br>可指定描述                                                     |
| 舰长                          | <img src="https://s2.loli.net/2022/10/11/8kPgVo6yzWMhfqU.jpg" width="200" >  | 可指定1~5个目标                                                          |
| 急急国王                        | <img src="https://s2.loli.net/2022/10/11/RqFP8Gtr2CQmSTU.jpg" width="200" >  | 可指定方块中的字和描述<br>可用多个图片替代方块                                          |
| 不文明                         | <img src="https://s2.loli.net/2022/10/15/XBqrksgCcAx1YaH.jpg" width="200" >  |                                                                    |
| 一起                          | <img src="https://s2.loli.net/2022/10/15/Ujt7avy9d5TfOlW.jpg" width="200" >  |                                                                    |
| 波纹                          | <img src="https://s2.loli.net/2022/11/09/hTnrF1e5gaYbxsX.gif" width="200" >  | 支持gif                                                              |
| 诈尸<br>秽土转生                  | <img src="https://s2.loli.net/2022/11/09/z2alEPjdsrNSyMU.gif" width="200" >  |                                                                    |
| 卡比锤<br>卡比重锤                 | <img src="https://s2.loli.net/2022/11/09/ouF5MxzQaqjC64d.gif" width="200" >  | 支持gif<br>可使用参数“圆”让头像为圆形                                            |

</details>