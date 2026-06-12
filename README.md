# EvenBetterNeteaseResolver

用于解析网易云音乐的歌曲、歌手、专辑等信息的 API/SDK.

灵感来源: [Netease_url](https://github.com/Suxiaoqinx/Netease_url)

示例 API: `https://ebnr.xiyang6666.top`

> [!IMPORTANT]
> **示例 API 不支持 VIP 歌曲的解析.**
>
> 如需解析 VIP 歌曲, 请按照下文教程自行部署项目, 并使用有 VIP 的网易云音乐账号的 Cookie 配置项目.

> [!TIP]
> **如何获取网易云 Cookie？**
>
> 以 FireFox 为例
>
> 1. 在浏览器中打开 [music.163.com](https://music.163.com) 并登录账号
> 2. 按 F12 打开开发者工具 → Network(网络) 标签页
> 3. 刷新页面，找到任意一个请求，选择 Cookie 栏, 右击复制全部
> 4. 将复制的 JSON 中的外层 ` {"请求 Cookie": ...}` 去掉, 仅保留内层对象(即`{"__csrf":"xxx",...}`), 填入 `EBNR_COOKIE` 环境变量

## 部署

### 运行项目

1. 克隆项目并安装依赖.
2. 在 `data` 目录下创建 `cookie.json` 文件或运行一次项目以自动生成改文件, 使用浏览器登录网易云音乐获取 Cookie 并填入该文件. (可选)
3. 使用 `pdm run start` 或 `python -m ebnr` 或 `uvicorn ebnr:app --host 0.0.0.0` 启动项目.

### Docker 部署

使用 docker-compose 一键部署

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

### Vercel 部署

> [!NOTE]
> Vercel 的 Serverless 环境不支持持久化文件存储, **Cookie 必须通过环境变量传入**.

#### 一键部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/XiYang6666/EvenBetterNeteaseResolver&env=EBNR_BASE_URL,EBNR_COOKIE&envDescription=部署所需的环境变量配置&envLink=https://github.com/XiYang6666/EvenBetterNeteaseResolver%23配置)

#### 手动部署步骤

**1. Fork 仓库**

点击右上角 Fork，将本仓库 Fork 到你自己的 GitHub 账号下。

**2. 导入到 Vercel**

前往 [vercel.com/new](https://vercel.com/new)，选择刚才 Fork 的仓库导入。

**3. 配置环境变量**

在 Vercel 项目的 **Settings → Environment Variables** 中添加以下变量：

| 变量名               | 必填  | 说明                                                              |
| -------------------- | ----- | ----------------------------------------------------------------- |
| `EBNR_BASE_URL`      | true  | Vercel 部署域名，例如 `https://your-app.vercel.app`               |
| `EBNR_COOKIE`        | false | 网易云音乐 Cookie（JSON 字符串格式），不填则无法解析 VIP 歌曲     |
| `EBNR_CACHE_BACKEND` | false | 缓存后端, 如果项目配置了 Vercel Storage 的 Redis 应设置为 `redis` |

**4. 部署**

点击 **Deploy**，等待部署完成后即可通过 Vercel 分配的域名访问。

**5. 验证部署**

访问 `https://your-app.vercel.app/`，若返回欢迎信息则说明部署成功。
API 文档可通过 `https://your-app.vercel.app/docs` 访问。

## 配置

配置文件在项目根目录下的 `config.toml` 中, 可以使用环境变量覆盖配置.

### 基础配置

| 配置项                             | 默认值                  | 注释                                                                                    |
| ---------------------------------- | ----------------------- | --------------------------------------------------------------------------------------- |
| `EBNR_BASE_UR`                     | `http://127.0.0.1:8000` | API 根路径, 用于 meting-api 正确处理返回值                                              |
| `EBNR_COOKIE`                      | `None`                  | json 格式 网易云音乐 Cookie 字符串                                                      |
| `EBNR_COOKIE_FILE_PATH`            | `./data/cookie.json`    | json 格式 网易云音乐 Cookie 文件路径, `EBNR_COOKIE` 设置时无效                          |
| `EBNR_COOKIE_FILE_TYPE`            | `object`                | json 格式 网易云音乐 Cookie 文件类型, `EBNR_COOKIE` 设置时无效, 可选 `object` 或 `list` |
| `EBNR_API_CACHE`                   | `true`                  | 是否缓存上游网易云 API 返回值                                                           |
| `EBNR_CACHE_SIZE`                  | `1024`                  | 上游 API 数据缓存量                                                                     |
| `EBNR_CACHE_TIMEOUT`               | `86400`                 | 上游 API 数据缓存时长                                                                   |
| `EBNR_CACHE_BACKEND`               | `memory`                | 缓存后端 ， 可选 `memory` 或 `redis`                                                    |
| `EBNR_AUDIO_CACHE_TIMEOUT`         | `3600  `                | 音频链接缓存时长, 为 0 则不缓存                                                         |
| `EBNR_AUDIO_CACHE_VALIDATION_TYPE` | `background`            | 音频链接缓存策略，EBNR_AUDIO_CACHE_TIMEOUT 为 0 时无效, 可选 `sync` 或 `background`     |
| `EBNR_RESOLVE_RESPONSE_TYPE`       | `redirect`              | 音频解析返回类型, 可选 `redirect`, `proxy`或 `streaming-proxy`                          |
| `EBNR_REDIRECT_CODE`               | `307`                   | 重定向返回码, 当 EBNR_RESOLVE_TYPE 不为 redirect 时无效, 可选 `307` 或 `302`            |
| `EBNR_API_CONCURRENCY`             | `200`                   | 上游 API 请求最大并发量                                                                 |

### Redis 配置

`EBNR_CACHE_BACKEND` 不为 `redis` 或 Vercel 环境下无效. Vercel 环境下会通过 `REDIS_URL` 环境变量配置 Redis

| 配置项                       | 默认值      | 注释             |
| ---------------------------- | ----------- | ---------------- |
| `EBNR_REDIS_HOST`            | `localhost` | Redis 服务 host  |
| `EBNR_REDIS_PORT`            | `6379`      | Redis 服务端口   |
| `EBNR_REDIS_DB`              | `0`         | Redis 数据库编号 |
| `EBNR_REDIS_USERNAME`        | `None`      | Redis 用户名     |
| `EBNR_REDIS_PASSWORD`        | `None`      | Redis 密码       |
| `EBNR_REDIS_PREFIX`          | `ebnr`      | Redis 缓存键前缀 |
| `EBNR_REDIS_MAX_CONNECTIONS` | `50`        | Redis 最大连接数 |

## 请求格式

访问 https://ebnr.xiyang6666.top/docs 以获取 OpenAPI 文档.

[API 文档](docs/api-docs.md)

## 已知问题

- `/info` 接口无法获取 `jyeffect`, `sky` 以及 `jymaster` 的音频信息, 暂时未找到对应功能的参考代码.
- `/playlist` 接口无法获取歌单 1000 首之后的歌.
