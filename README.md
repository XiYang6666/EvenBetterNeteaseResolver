# EvenBetterNeteaseResolver

用于解析网易云音乐的歌曲、歌手、专辑等信息的 API/SDK.

灵感来源: [Netease_url](https://github.com/Suxiaoqinx/Netease_url)

## 请求格式

### GET `/`

根路径, 显示欢迎信息与 VIP 状态.

### GET `/meting/`

meting-api 兼容接口, 详见 [meting-api](https://github.com/injahow/meting-api)

### GET/POST `/info/`

获取歌曲信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持直接拼接链接, 相当于传入单个 id.
比如直接 GET `https://ebnr.xiyang6666.top/info/https://music.163.com/song?id=557579321&uct2=U2FsdGVkX1+v0LwYC5yMXDApv1BAzl9NOd/DBy+guWw=`

请求参数:

- `ids`(可选): 歌曲 ID 列表, 对于 GET 请求, 多个 ID 用逗号分隔, 如 `ids=114514,1919810`, 对于 POST 请求, 多个 ID 放入数组中(id 为 number 类型), 如果传入则返回歌曲信息列表
- `id`(可选): 歌曲 ID
- `link`(可选): 歌曲链接, 如 `https://music.163.com/song?id=557579321&uct2=U2FsdGVkX1+v0LwYC5yMXDApv1BAzl9NOd/DBy+guWw=`

`ids`, `id`, `link` 至少应传入一个, 优先级从上至下.

### GET/POST `/audio/`

获取歌曲音频, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持直接拼接链接, 相当于传入单个 id.
比如直接 GET `https://ebnr.xiyang6666.top/audio/https://music.163.com/song?id=557581315&uct2=U2FsdGVkX1/ZwULy0tlfChgEBu54YoJUjlNweDy+2Gc=`

请求参数:

- `ids`(可选): 歌曲 ID 列表, 对于 GET 请求, 多个 ID 用逗号分隔, 如 `ids=114514,1919810`, 对于 POST 请求, 多个 ID 放入数组中(id 为 number 类型), 如果传入则返回歌曲信息列表
- `id`(可选): 歌曲 ID
- `link`(可选): 歌曲链接, 如 `https://music.163.com/song?id=557581315&uct2=U2FsdGVkX1/ZwULy0tlfChgEBu54YoJUjlNweDy+2Gc=`
- `quality`(可选): 音频质量, 可选 `standard`(默认), `exhigh`, `lossless`, `higres`,`sky`, `jyeffect`,`jymaster`

`ids`, `id`,`link` 至少应传入一个, 优先级从上至下.

### GET/POST `/resolve/`

解析歌曲音频, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

与 `/audio/` 不同, 该接口会直接重定向至歌曲的音频地址.

支持直接拼接链接, 相当于传入单个 id.
比如直接 GET `https://ebnr.xiyang6666.top/resolve/https://music.163.com/song?id=1357953770&uct2=U2FsdGVkX18pgJvJv2sRyWD1CJDM5cKd5bYP2Gb7+gI=`

请求参数:

- `ids`(可选): 歌曲 ID 列表, 对于 GET 请求, 多个 ID 用逗号分隔, 如 `ids=114514,1919810`, 对于 POST 请求, 多个 ID 放入数组中(id 为 number 类型), 如果传入则返回歌曲信息列表
- `id`(可选): 歌曲 ID
- `link`(可选): 歌曲链接, 如 `https://music.163.com/song?id=1357953770&uct2=U2FsdGVkX18pgJvJv2sRyWD1CJDM5cKd5bYP2Gb7+gI=`
- `quality`(可选): 音频质量, 可选 `standard`(默认), `exhigh`, `lossless`, `higres`,`sky`, `jyeffect`,`jymaster`

`ids`, `id`,`link` 至少应传入一个, 优先级从上至下.

### GET/POST `/playlist/`
获取歌单信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持直接拼接链接, 相当于传入单个 id.
比如直接 GET `https://ebnr.xiyang6666.top/playlist/https://music.163.com/playlist?id=13317821430&uct2=U2FsdGVkX19omPbnImKeAowmOi+2zWYqABR21qn4teg=`

请求参数:

- `id`(可选): 歌单 ID
- `link`(可选): 歌单链接, 如 `https://music.163.com/playlist?id=13317821430&uct2=U2FsdGVkX19omPbnImKeAowmOi+2zWYqABR21qn4teg=`

`id`, `link` 至少应传入一个, 优先级从上至下.

### GET/POST `/album/`

获取专辑信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持直接拼接链接, 相当于传入单个 id.
比如直接 GET `https://ebnr.xiyang6666.top/album/https://music.163.com/album?id=38591089&uct2=U2FsdGVkX18hr8ASwm86DmWvFzwiYfy+jdupBbpOfUQ=`

请求参数:

- `id`(可选): 专辑 ID
- `link`(可选): 专辑链接, 如 `https://music.163.com/album?id=38591089&uct2=U2FsdGVkX18hr8ASwm86DmWvFzwiYfy+jdupBbpOfUQ=`

`id`, `link` 至少应传入一个, 优先级从上至下.

