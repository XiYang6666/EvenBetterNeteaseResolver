## API 文档

### GET `/`

根路径, 显示欢迎信息与状态.

支持拼接网易云分享链接, 会自动根据链接类型重定向至正确的路径.

支持的网易云链接格式为 `[http://|https://][y.]music.163.com[/m]/<song|album|playlist></<id>|?id=<id>>`

### GET `/meting`

meting-api 兼容接口, 详见 [meting-api](https://github.com/injahow/meting-api)

### GET/POST `/info`

获取歌曲信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例:
`https://ebnr.xiyang6666.top/info/https://music.163.com/song?id=557579321`

请求参数:

| 参数    | 必填  | GET   | POST | 类型     | 注释                                                                                     |
| ------- | ----- | ----- | ---- | -------- | ---------------------------------------------------------------------------------------- |
| `ids`   | false | false | true | number[] | 歌曲 ID 列表, 如果传入则返回 `SongInfo[]`                                                |
| `id`    | false | true  | true | number   | 歌曲 ID, GET 请求可传入多个, 传入单个时返回 `SongInfo`, 传入多个时返回 `SongInfo[]`      |
| `links` | false | false | true | string[] | 歌曲分享链接列表，如果传入则返回 `SongInfo[]`                                            |
| `link`  | false | true  | true | string   | 歌曲分享链接, GET 请求可传入多个, 传入单个时返回 `SongInfo`, 传入多个时返回 `SongInfo[]` |

`ids`, `id`, `links`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/audio`

获取歌曲音频, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/audio/https://music.163.com/song?id=557581315`

请求参数:

| 参数      | 必填  | GET   | POST | 类型     | 注释                                                                                                    |
| --------- | ----- | ----- | ---- | -------- | ------------------------------------------------------------------------------------------------------- |
| `ids`     | false | false | true | number[] | 歌曲 ID 列表, 如果传入则返回 `AudioInfo[]`                                                              |
| `id`      | false | true  | true | number   | 歌曲 ID, GET 请求可传入多个, 传入单个时返回 `AudioInfo`, 传入多个时返回 `AudioInfo[]`                   |
| `links`   | false | false | true | string[] | 歌曲分享链接列表，如果传入则返回 `AudioInfo[]`                                                          |
| `link`    | false | true  | true | string   | 歌曲分享链接, GET 请求可传入多个, 传入单个时返回 `AudioInfo`, 传入多个时返回 `AudioInfo[]`              |
| `quality` | false | true  | true | string   | 音频质量, 可选 `standard`(默认), `higher`, `exhigh`, `lossless`, `hires`, `jyeffect`, `sky`, `jymaster` |

`ids`, `id`, `links`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/resolve`

解析歌曲音频, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

与 `/audio` 不同, 该接口会直接重定向至歌曲的音频地址.

仅支持拼接网易云分享链接.

示例
`https://ebnr.xiyang6666.top/resolve/https://music.163.com/song?id=1357953770`

### GET/POST `/playlist`

获取歌单信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/playlist/https://music.163.com/playlist?id=14316757648`

请求参数:

| 参数   | 必填  | GET  | POST | 类型   | 注释         |
| ------ | ----- | ---- | ---- | ------ | ------------ |
| `id`   | false | true | true | number | 歌曲 ID      |
| `link` | false | true | true | string | 歌曲分享链接 |

- `id`(可选): 歌单 ID
- `link`(可选): 歌单分享链接

`id`, `link` 至少应传入一种, 传入多个时优先级从前往后.

> [!TIP]
> `/playlist` API 返回的 `Playlisy` 的 tracks 属性仅包含前 1000 首歌的信息, 要获取全部歌曲请调用 `/tracks`.

### GET/POST `/tracks`

获取歌单内的歌曲信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/tracks/https://music.163.com/playlist?id=14316757648`

请求参数:

| 参数    | 必填               | GET  | POST | 类型   | 注释         |
| ------- | ------------------ | ---- | ---- | ------ | ------------ |
| `id`    | false              | true | true | number | 歌曲 ID      |
| `link`  | false              | true | true | string | 歌曲分享链接 |
| `limit` | false(默认 100000) | true | true | number | 单页歌曲数   |
| `page`  | false(默认 0)      | true | true | number | 页序号       |

- `id`(可选): 歌单 ID
- `link`(可选): 歌单分享链接

`id`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/album`

获取专辑信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/album/https://music.163.com/album?id=38591089`

请求参数:

| 参数   | 必填  | GET  | POST | 类型   | 注释         |
| ------ | ----- | ---- | ---- | ------ | ------------ |
| `id`   | false | true | true | number | 歌曲 ID      |
| `link` | false | true | true | string | 歌曲分享链接 |

`id`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/search`

搜索歌曲, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

请求参数:

| 参数      | 必填          | GET  | POST | 类型   | 注释     |
| --------- | ------------- | ---- | ---- | ------ | -------- |
| `keyword` | true          | true | true | string | 关键词   |
| `limit`   | false(默认10) | true | true | number | 搜索条数 |
