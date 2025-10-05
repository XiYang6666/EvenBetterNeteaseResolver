# EvenBetterNeteaseResolver

用于解析网易云音乐的歌曲、歌手、专辑等信息的 API/SDK.

灵感来源: [Netease_url](https://github.com/Suxiaoqinx/Netease_url)

示例 API: `https://ebnr.xiyang6666.top`

> [!IMPORTANT]
> **示例 API 不支持 VIP 歌曲的解析.**
>
> 如需解析 VIP 歌曲, 请按照下文教程自行部署项目, 并使用有 VIP 的网易云音乐账号的 Cookie 配置项目.

## 部署

### 运行项目

1. 克隆项目并安装依赖.
2. 在 `data` 目录下创建 `cookie.json` 文件或运行一次项目以自动生成改文件, 使用浏览器登录网易云音乐获取 Cookie 并填入该文件. (可选)
3. 使用 `pdm run start` 或 `python -m ebnr` 或 `uvicorn ebnr:app --host 0.0.0.0` 启动项目.

### Docker 部署

使用 docker-compose

```yaml
services:
  ebnr:
    image: xiyang6666/ebnr:dev
    container_name: ebnr
    restart: always
    network_mode: bridge
    environment:
      - TZ=Asia/Shanghai
      - EBNR_BASE_URL=https://example.com
    volumes:
      - ./data:/app/data
    ports:
      - 8000:8000
```

一键部署

## 配置

配置文件在项目根目录下的 `config.toml` 中, 可以使用环境变量覆盖配置.

| 配置项                   | 默认值                | 注释                                                                     |
| ------------------------ | --------------------- | ------------------------------------------------------------------------ |
| EBNR_BASE_URL            | http://127.0.0.1:8000 | API 根路径, 用于 meting-api 正确处理返回值                               |
| EBNR_API_CACHE           | true                  | 是否缓存上游网易云 API 返回值                                            |
| EBNR_AUDIO_CACHE_TIMEOUT | 3600                  | 音频链接缓存时长, 为 0 则不缓存                                          |
| EBNR_AUDIO_CACHE_TYPE    | optimistic            | 音频链接缓存策略，EBNR_AUDIO_CACHE_TIMEOUT 为 0 时无效                   |
| EBNR_RESOLVE_TYPE        | redirect              | 音频解析返回类型, 可选 redirect, proxy, streaming-proxy                  |
| EBNR_REDIRECT_CODE       | 307                   | 重定向返回码, 当 EBNR_RESOLVE_TYPE 不为 redirect 时无效, 可选 307 和 302 |

## 请求格式

访问 https://ebnr.xiyang6666.top/docs 以获取 OpenAPI 文档.

支持的网易云链接格式为 `[http://|https://][y.]music.163.com[/m]/<song|album|playlist></<id>|?id=<id>>`

### GET `/`

根路径, 显示欢迎信息与 VIP 状态.

支持拼接网易云分享链接, 会自动根据链接类型重定向至正确的路径.

### GET `/meting`

meting-api 兼容接口, 详见 [meting-api](https://github.com/injahow/meting-api)

### GET/POST `/info`

获取歌曲信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例:
`https://ebnr.xiyang6666.top/info/https://music.163.com/song?id=557579321`

请求参数:

| 参数    | 必填 | GET | POST | 类型     | 注释                                                                                     |
| ------- | ---- | --- | ---- | -------- | ---------------------------------------------------------------------------------------- |
| `ids`   | ❌   | ❌  | ✅   | int[]    | 歌曲 ID 列表, 如果传入则返回 `SongInfo[]`                                                |
| `id`    | ❌   | ✅  | ✅   | int      | 歌曲 ID, GET 请求可传入多个, 传入单个时返回 `SongInfo`, 传入多个时返回 `SongInfo[]`      |
| `links` | ❌   | ❌  | ✅   | string[] | 歌曲分享链接列表，如果传入则返回 `SongInfo[]`                                            |
| `link`  | ❌   | ✅  | ✅   | string   | 歌曲分享链接, GET 请求可传入多个, 传入单个时返回 `SongInfo`, 传入多个时返回 `SongInfo[]` |

`ids`, `id`, `links`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/audio`

获取歌曲音频, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/audio/https://music.163.com/song?id=557581315`

请求参数:

| 参数      | 必填 | GET | POST | 类型     | 注释                                                                                                    |
| --------- | ---- | --- | ---- | -------- | ------------------------------------------------------------------------------------------------------- |
| `ids`     | ❌   | ❌  | ✅   | int[]    | 歌曲 ID 列表, 如果传入则返回 `AudioInfo[]`                                                              |
| `id`      | ❌   | ✅  | ✅   | int      | 歌曲 ID, GET 请求可传入多个, 传入单个时返回 `AudioInfo`, 传入多个时返回 `AudioInfo[]`                   |
| `links`   | ❌   | ❌  | ✅   | string[] | 歌曲分享链接列表，如果传入则返回 `AudioInfo[]`                                                          |
| `link`    | ❌   | ✅  | ✅   | string   | 歌曲分享链接, GET 请求可传入多个, 传入单个时返回 `AudioInfo`, 传入多个时返回 `AudioInfo[]`              |
| `quality` | ❌   | ✅  | ✅   | string   | 音频质量, 可选 `standard`(默认), `higher`, `exhigh`, `lossless`, `hires`, `jyeffect`, `sky`, `jymaster` |

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
`https://ebnr.xiyang6666.top/playlist/https://music.163.com/playlist?id=13317821430`

请求参数:

| 参数   | 必填 | GET | POST | 类型   | 注释         |
| ------ | ---- | --- | ---- | ------ | ------------ |
| `id`   | ❌   | ✅  | ✅   | int    | 歌曲 ID      |
| `link` | ❌   | ✅  | ✅   | string | 歌曲分享链接 |

- `id`(可选): 歌单 ID
- `link`(可选): 歌单分享链接

`id`, `link` 至少应传入一种, 传入多个时优先级从前往后.

### GET/POST `/album`

获取专辑信息, 同时支持 GET 与 POST, POST 请求参数为 JSON 格式.

支持拼接网易云分享链接, 相当于传入单个 id.

示例
`https://ebnr.xiyang6666.top/album/https://music.163.com/album?id=38591089`

请求参数:

| 参数   | 必填 | GET | POST | 类型   | 注释         |
| ------ | ---- | --- | ---- | ------ | ------------ |
| `id`   | ❌   | ✅  | ✅   | int    | 歌曲 ID      |
| `link` | ❌   | ✅  | ✅   | string | 歌曲分享链接 |

`id`, `link` 至少应传入一种, 传入多个时优先级从前往后.

## 已知问题

- `/info` 接口无法获取 `jyeffect`, `sky` 以及 `jymaster` 的音频信息, 暂时未找到对应功能的参考代码.
- `/playlist` 接口无法获取歌单 1000 首之后的歌.
