# 基于 MkDocs Material / MaterialX 的导航站

用一份 `nav_data.yml` 描述站点，构建期自动抓取标题、描述与图标，最终产出纯静态的导航页面。

> 演示站点：`https://nav.sufine.top`（部署后替换为实际地址）

推荐使用 [MaterialX](https://github.com/jaywhj/mkdocs-materialx) 主题，以拥抱现代化的界面设计。

> Zensical 框架同样适用此项目，但截止目前（2026.02），Zensical 不支持插件与 hooks 自动化脚本，无法将 `build.py` 构建 MD 文档的工作流并入 `Zensical build` 中，需要您手动执行。

> **关于示例中的域名**：本文档所有示例域名均为占位地址（如 `example.com`、`www.example.org`），请替换为您自己的真实地址后再使用。切勿把示例地址直接提交到仓库。

## 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [导航数据配置（`nav_data.yml`）](#导航数据配置nav_datayml)
- [站点配置（`mkdocs.yml`）](#站点配置mkdocsyml)
- [图标机制](#图标机制)
- [ASK AI 问答助手部署](#ask-ai-问答助手部署)
- [音乐播放器部署](#音乐播放器部署)
- [构建健康检查报告](#构建健康检查报告)
- [并发校验加速](#并发校验加速)
- [自动化构建原理](#自动化构建原理)
- [开发规划](#开发规划)
- [许可证](#许可证)
- [致谢](#致谢)

## 功能特性

- **自动化构建**：从 `nav_data.yml` 自动生成导航页面
- **智能元数据获取**：只需填写 URL，自动抓取网站标题、描述和图标
- **智能图标管理**：多级图标自动获取与容错机制，构建期逐条目核对图标来源
- **并发校验加速**：构建期对站点元数据/图标校验并发执行，显著降低大量站点时的构建耗时
- **失效站点检测**：构建期自动检测域名已不存在的导航站点，在终端输出末尾汇总提醒
- **响应式设计**：适配桌面端和移动端
- **桌面端侧边栏**：支持点击左下角按钮折叠/展开侧边栏
- **状态记忆**：自动记住用户上次的侧边栏折叠状态
- **可选扩展**：内置 ASK AI 问答助手与悬浮音乐播放器，均为独立模块，可单独启用

## 项目结构

```text
.
├── nav_data.yml      # [核心] 导航数据与功能配置文件
├── mkdocs.yml        # MkDocs 站点配置文件
├── build.py          # 构建脚本：处理数据并生成 index.md
├── hooks.py          # MkDocs 钩子：在构建前触发 build.py
├── ai-worker.js      # [可选] ASK AI 后端（Cloudflare Worker）
├── docs/             # 文档源目录
│   ├── index.md      # [程序自动生成] 导航主页
│   ├── images/       # 图片资源
│   ├── javascripts/  # 交互脚本（ASK AI、音乐播放器、侧边栏等）
│   └── stylesheets/  # 自定义样式
├── site/             # [程序自动生成] 静态站点输出目录
└── README.md         # 项目说明文档
```

## 快速开始

### 1. 环境要求

- Python `>= 3.11`
- MkDocs MaterialX（或 MkDocs Material）

### 2. 安装依赖

使用 `uv`（推荐，仓库已提供 `uv.lock`）：

```bash
uv sync
```

或使用 `pip`：

```bash
pip install mkdocs-materialx
# 或 pip install mkdocs-material

# 安装项目运行所需的依赖
pip install beautifulsoup4 requests PyYAML
```

### 3. 运行项目

**本地预览**：

```bash
mkdocs serve
```

**构建站点**：

```bash
mkdocs build
```

构建产物输出到 `site/` 目录。

## 导航数据配置（`nav_data.yml`）

项目的所有配置和导航数据都在 `nav_data.yml` 中管理。

### 1. 全局配置

```yaml
config:
  filename: index.md         # 生成的目标文件名
  sidebar_collapsed: false   # (可选) 是否默认收起侧边栏。true: 默认收起; false: 默认展开
  validation_workers: 12     # (可选) 并发校验线程数。设置为 1 可禁用并发（回退为串行）
  dead_link_check: true      # (可选) 是否启用构建健康检查，默认 true
  report_fallback_icons: true # (可选) 是否在报告中输出「依赖第三方图标服务」一类，默认 true
  meta:
    title: 导航目录          # 页面标题
    description: 站点描述    # 页面描述
```

| 字段 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `filename` | string | `index.md` | 生成的 Markdown 文件名，写入 `docs/` 目录 |
| `sidebar_collapsed` | bool | `false` | 桌面端侧边栏初始状态，`true` 为收起 |
| `validation_workers` | int | 自动（4~24） | 构建期并发线程数，`1` 表示串行 |
| `dead_link_check` | bool | `true` | 是否启用全部构建健康检查 |
| `report_fallback_icons` | bool | `true` | 是否输出「依赖第三方图标服务」提示 |
| `report_icon_sources` | bool | `true` | 同上，兼容别名，任一为 `false` 即关闭 |
| `meta.title` | string | — | 页面标题，写入 Front Matter |
| `meta.description` | string | — | 页面描述，写入 Front Matter |

### 2. 添加导航链接

```yaml
nav:
  - category: 分类名称
    icon: material/tools     # (可选) 分类图标，格式为 material/icon-name
    items:
      - name: (可选) 网站名称。若留空，程序会自动抓取网页 Title
        url: https://example.com
        description: (可选) 网站描述。若留空，程序会自动抓取网页 Meta Description
        icon: (可选) 图标链接，支持 favicon、在线 SVG 或本地图片。若留空，程序会自动抓取
```

| 字段 | 必填 | 留空时的行为 |
| :--- | :--- | :--- |
| `category` | 是 | — |
| `category.icon` | 否 | 分类标题不显示图标，取值为 Material 图标名（如 `material/tools`） |
| `items[].url` | 是 | — |
| `items[].name` | 否 | 自动抓取网页 `<title>` |
| `items[].description` | 否 | 自动抓取网页 Meta Description |
| `items[].icon` | 否 | 按 [图标机制](#图标机制) 的优先级自动获取 |

> 如果网站元数据抓取失败，程序会自动提取 URL 的域名 `hostname` 作为标题，`description` 保持为空，站点图标则进入 Fallback 策略（依次尝试站点自身 favicon、Google 图标服务、Yandex 图标接口）。

## 站点配置（`mkdocs.yml`）

为了使本项目正常运行，您的 `mkdocs.yml` 必须包含以下关键配置：

```yaml
# 1. 挂载构建脚本 (核心)
hooks:
  - hooks.py

# 2. 主题配置
theme:
  name: materialx # 或 material
  features:
    - navigation.top # 推荐开启返回顶部按钮
    - toc.integrate  # 集成目录功能必须开启！

# 3. 必须启用的 Markdown 扩展
markdown_extensions:
  - attr_list
  - md_in_html      # 允许 HTML 中嵌入 Markdown (用于侧边栏按钮)
  - toc:
      permalink: true # 启用标题锚点链接
  - pymdownx.emoji: # 用于渲染图标
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
```

> `markdown_extensions` 在 YAML 中是一个列表，所有扩展必须写在同一个键下；重复声明同名键会导致先前的配置被覆盖。

### 侧边栏功能

- **折叠/展开**：桌面端左下角提供切换按钮。
    - 展开状态图标：`material/menu-open`
    - 收起状态图标：`material/menu-close`
- **默认状态**：可在 `nav_data.yml` 中通过 `config.sidebar_collapsed` 设置初始状态。
- **智能避让**：`extra.js` 脚本实现了悬浮按钮（侧边栏切换、ASK AI、音乐播放器）在滚动到底部时自动避让页脚的功能，防止内容被遮挡。

## 图标机制

### 1. 图标解析顺序

每个条目的图标按以下顺序解析，`build.py` 会记录最终结果来自哪一层：

| 顺序 | 来源 | 说明 |
| :--- | :--- | :--- |
| 1 | `configured` / `local` | `nav_data.yml` 中显式配置的远程链接或本地文件 |
| 2 | `page` | 抓取站点 HTML 中 `<link rel="icon">` 声明的图标 |
| 3 | `favicon` | 探测默认路径 `/favicon.ico` |
| 4 | `google` | Google favicon 服务兜底 |
| 5 | `yandex` | Yandex favicon 服务兜底 |
| 6 | 无 | 全部失败，页面显示灰色云朵占位图 |

抓取与探测阶段均执行**严格校验**：对候选图标发起实测请求，拦截 `403`、空内容或非图片类型（如重定向到 HTML 页面导致的 CORB 问题），请求超时设置为 5 秒，超时即跳过并进入下一层。

### 2. 图标源选择建议

`icon` 字段支持远程 URL 与本地相对路径。**图标源的选择直接决定图标能否长期正常显示**，建议按以下优先级选用。

**优先级 1：本地图标（最稳）**

需要绝对稳定，或远程源未收录某个图标时，把 SVG 放进 `docs/images/icons/`，用相对路径引用：

```yaml
# 文件放在 docs/images/icons/your-icon.svg
icon: images/icons/your-icon.svg
```

本地图标**零外部依赖、离线可用**，且构建期只做文件存在性校验。获取方式：从 [Iconify 图标集](https://github.com/iconify/icon-sets) 或任意来源下载 SVG，放入该目录即可。

**优先级 2：`cdn.simpleicons.org`（推荐远程源）**

```yaml
icon: https://cdn.simpleicons.org/github
```

返回标准 `image/svg+xml`，响应稳定，是当前首选远程图标源。可通过追加颜色段自定义颜色：`https://cdn.simpleicons.org/github/ffffff`。

图标 slug 可在 [simpleicons.org](https://simpleicons.org) 查询。注意部分品牌（如 `openai`、`codepen`）因商标原因未收录，会返回 `404`。

**已知不可用：`api.iconify.design`**

> **⚠️ 自 2026 年起，`api.iconify.design` 及其官方镜像 `api.simplesvg.com`、`api.unisvg.com` 对自动化请求统一返回 `403` + Cloudflare 拦截页**（`Content-Type: text/html`），无论是否经过代理均如此。浏览器加载同样被拦截，图标会静默降级为 favicon 或灰色占位图。
>
> **请勿再使用该源。** 若需 Iconify 的图标，请下载 SVG 后走本地路径。

判定方法：构建时若出现 `[SKIP] Non-image Content-Type` 或图标源的 `Content-Type` 为 `text/html`，即说明该图标源正在返回拦截页而非图片。

### 3. 兜底服务的占位图必须拦截

**Google 与 Yandex 在「不认识某个域名」时会返回一张通用占位图，而不是报错**：

| 服务 | 状态码 | 占位图 |
| :--- | :--- | :--- |
| Google | `404` | 通用地球图标（无论请求多大尺寸，都返回 16x16） |
| Yandex | `200` | 1x1 空白透明图 |

因此**只看状态码会把占位图当成有效图标写进页面**——用户看到的就是一个毫无意义的地球。项目用两个可靠信号拦截：

1. **状态码**
    - `404` → 该服务没有此站点的图标，弃用
    - 其它非 `200` → 弃用
2. **图片指纹 MD5** → 命中已知占位图则弃用（覆盖 Google 也可能以 `200` 返回地球的情况）

任一命中即视为该兜底来源不可用，继续降级到下一层；全部失败则 `icon` 留空，页面上由占位 SVG 兜底。

> **⚠️ 不要用响应体积做判据。** 实测数据证明尺寸无法区分有效图标与占位图：
>
> | 响应 | 体积 | 性质 |
> | :--- | ---: | :--- |
> | 某站点真实图标（A） | **467 B** | 有效 |
> | 某站点真实图标（B） | **281 B** | 有效 |
> | Google 地球占位图 | 726 B | 占位图 |
>
> **真实图标（281 B）比占位图（726 B）更小**，任何尺寸阈值都会误杀有效图标。代码中仅保留一个 `100` 字节的下限用于过滤 1x1 空图与截断响应，这在实测中与真实图标（最小 281 B）有充足余量。

### 4. 运行时兜底（客户端）

构建期拦截只影响**构建产物里写哪个 URL**，不改变浏览器端的兜底链。生成的每个图标 `<img>` 仍带 `onerror="handleImageError(this)"`，一旦加载失败，浏览器会按「三级火箭」策略降级：

1. **Level 1（Google）**：原始图标加载失败时，尝试 Google favicon 服务。
2. **Level 2（Yandex）**：Google 服务也被拦截或失败时，切换至 Yandex favicon 服务。这为中国大陆等特定网络环境提供了强有力的备选保障。
3. **Level 3（Placeholder）**：全部不可用，显示默认的灰色云朵占位图。

构建期判定与客户端兜底是**互补**而非替代关系：构建期尽量选出一个可用的真实图标来源，客户端负责兜住运行时失败。

> **隐私保护**：所有远程图标在生成 HTML 时均会自动添加 `referrerpolicy="no-referrer"` 属性，防止用户访问记录被第三方追踪，同时绕过部分网站的防盗链限制。

### 5. 手动配置与校验

当您在 `nav_data.yml` 中显式配置 `icon` 字段时，构建脚本会自动执行有效性检查：

- **在线 SVG/图片**：脚本会发起请求验证链接连通性与内容类型。
    - 若验证失败（如 `404` 或非图片），构建日志将输出警告（`Warning: Remote icon validation failed...`），但**不会**自动替换为您配置的链接，以便您排查问题。
- **本地路径**：检查 `docs/` 目录下是否存在对应文件。若文件缺失，将输出警告。

> **注意**：请确保本地图标文件确实位于 `docs` 目录下，否则 MkDocs 构建时无法将其包含在最终站点中。

## ASK AI 问答助手部署

本项目可选的 AI 问答助手基于 Cloudflare Workers 和 SiliconFlow（硅基流动）实现。后端 Worker 负责转发请求，隐藏 API Key 并处理跨域问题。

### 1. 部署后端（Cloudflare Worker）

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 进入 **Workers & Pages** → **Create Application** → **Create Worker**。
3. 命名您的 Worker（例如 `nav-hub-ai`）并点击 **Deploy**。
4. 点击 **Edit code**，将项目根目录下的 `ai-worker.js` 内容完整复制并覆盖默认代码。
5. 保存并部署。
6. 返回 Worker 详情页，进入 **Settings** → **Variables and Secrets**。
7. 添加变量：
    - **Variable name**：`SILICONFLOW_API_KEY`
    - **Value**：您的 SiliconFlow API Key（以 `sk-` 开头）
    - 点击 **Encrypt** 加密存储。
8. 记录下您的 Worker URL（形如 `https://<worker-name>.<account>.workers.dev`）。

> 建议在生产环境中修改 `ai-worker.js` 里的 `ALLOWED_ORIGINS`，把 `"*"` 收紧为您的站点域名，避免接口被任意站点调用。

### 2. 引入资源（`mkdocs.yml`）

```yaml
extra_css:
  - stylesheets/ask_ai.css # ASK AI 样式
  # - stylesheets/extra.css # (可选) 其他样式

extra_javascript:
  - https://cdn.jsdelivr.net/npm/marked/marked.min.js # 用于 Markdown 渲染
  - javascripts/ask_ai.js # ASK AI 核心逻辑
  - javascripts/extra.js # 界面交互优化（如按钮避让页脚）
```

### 3. 配置前端（`ask_ai.js`）

1. 打开 `docs/javascripts/ask_ai.js` 文件。
2. 找到文件顶部的配置项：

    ```javascript
    // Cloudflare Worker URL
    const WORKER_URL = "https://<worker-name>.<account>.workers.dev";
    ```

3. 将 `WORKER_URL` 的值替换为您在第一步中获取的 Worker URL。
4. 保存文件。

### 4. 验证

重新运行 `mkdocs serve` 或 `mkdocs build`，在站点右下角应出现 ASK AI 的悬浮按钮，点击即可开始对话。

> **注意**：默认模型配置为 `deepseek-ai/DeepSeek-V3`，您可以在 `ai-worker.js` 中修改 `MODEL_NAME` 变量来切换其他模型。

## 音乐播放器部署

本项目可选集成一个轻量级的悬浮音乐播放器，基于 [APlayer](https://github.com/DIYgod/APlayer) 和 [MetingJS](https://github.com/metowolf/MetingJS) 实现，支持网易云音乐、QQ 音乐等多种平台的歌单播放。

### 1. 功能特点

- **多平台支持**：支持网易云、QQ 音乐、酷狗等多家音乐平台。
- **极简设计**：默认显示为悬浮按钮，点击即可展开/折叠播放器，不占用页面空间。
- **自动吸附**：播放器界面自动吸附在页面左下角（可通过 CSS 调整）。

### 2. 引入资源（`mkdocs.yml`）

```yaml
extra_css:
  - https://cdnjs.cloudflare.com/ajax/libs/aplayer/1.10.1/APlayer.min.css
  - stylesheets/music_player.css # 自定义播放器样式

extra_javascript:
  - https://cdnjs.cloudflare.com/ajax/libs/aplayer/1.10.1/APlayer.min.js
  - https://cdn.jsdelivr.net/npm/meting@2/dist/Meting.min.js
  - javascripts/music_player.js # 播放器初始化脚本
  - javascripts/extra.js # 界面交互优化（如音乐播放器可见性与位置逻辑）
```

> **注意：本地精简版 APlayer**
>
> `docs/javascripts/APlayer.min.js` 是 APlayer 1.10.1 官方发行版的**本地精简副本**，已删除三部分内容：
>    - 内置 smoothscroll 对页内锚点点击的接管（它忽略 `scroll-margin-top`，会让标题永久链接的滚动落点偏移、末尾跳变）；
>    - 控制台输出版本横幅；
>    - 仅被内置 Promise polyfill 使用的 Promise / setImmediate / timers / process 垫片（改用浏览器原生 `Promise`），整体体积由 59 326 字节降到 51 854 字节。
>
>    因此**不要**用 CDN 原版直接覆盖该文件，否则锚点滚动问题会复现。

### 3. 配置歌单与数据源（`music_player.js`）

打开 `docs/javascripts/music_player.js`，文件顶部就是配置区：

```javascript
// 歌单：server 音乐平台 / type 资源类型 / id 资源 ID
const MUSIC_SOURCE = {
    server: "netease",   // netease 网易云, tencent QQ音乐, kugou, xiami, baidu
    type: "playlist",    // song 单曲, playlist 歌单, album 专辑, search 搜索, artist 歌手
    id: "17741904561",   // 资源 ID（如网易云歌单 ID）
};

// Meting 接口：按顺序探测，第一个可用的会被真正使用
// :server / :type / :id / :r 是 MetingJS 的占位符，不可删
const METING_APIS = [
    "https://api.injahow.cn/meting/?server=:server&type=:type&id=:id&r=:r",
    "https://api.qijieya.cn/meting/?server=:server&type=:type&id=:id&r=:r",
];
```

播放器外观相关的属性在同一个文件的 `mountMetingPlayer()` 中设置：

```javascript
    metingElement.setAttribute("fixed", "false");    // ！吸底模式必须为 false，否则自定义样式失效
    metingElement.setAttribute("mini", "false");     // ！迷你模式必须为 false，否则自定义样式失效
    metingElement.setAttribute("autoplay", "false"); // 是否自动播放
    metingElement.setAttribute("theme", "#2980b9");  // 主题颜色
    metingElement.setAttribute("volume", "0.7");
```

**接口探测与降级行为**（`mountPlayer()` / `probeApi()`）：

1. 页面加载后按 `METING_APIS` 顺序请求歌单接口，要求 **HTTP 200 且返回非空数组** 才算可用（单实例超时 `API_PROBE_TIMEOUT`，默认 3 秒）；
2. 第一个可用实例会被写入 `<meting-js api="…">`，之后歌单、音频流、歌词都由该实例中转；
3. 全部实例都不可用时**不显示音乐按钮**（避免"点了没反应"），控制台输出 `[music-player]` 警告；
4. 即使探测通过，若数据源中途失效导致播放器 12 秒内仍未出现（MetingJS 内部不处理 `fetch` 异常），也会自动移除按钮。

> **⚠️ 公共实例没有可用性保证**：这些接口由个人维护，随时可能限流、下线或更换域名（`api.i-meto.com` 就长期返回 524/超时）。若要长期稳定，建议自建 [Meting-API](https://github.com/dreamerhe114514/Meting-API) 或 [Vercel 版](https://github.com/YL2209/vercel-meting)，把自建地址放在 `METING_APIS` 第一位；也可以在 `mkdocs build` 阶段把歌单抓成静态 JSON，彻底去掉运行时第三方依赖。

**常用配置项说明**：

| 属性 | 描述 | 示例值 |
| :--- | :--- | :--- |
| **server** | 音乐平台 | `netease`（网易云）、`tencent`（QQ 音乐） |
| **type** | 资源类型 | `playlist`（歌单）、`song`（单曲） |
| **id** | 资源 ID | 对应平台链接中的数字 ID |
| **theme** | 主题颜色 | `#2980b9` |

> **提示**：导航站默认为单页面站点，如果您配置了多页面，希望切换页面时音乐不中断，需要在 `mkdocs.yml` 中开启 `navigation.instant` 特性。

## 构建健康检查报告

两个检查（站点域名解析、站点图标）合并为**一个**报告块，在构建输出的最末端一次性输出：

```text
==============================================================================
  构建健康检查报告
==============================================================================
[1] 站点域名解析（DNS）—— 116 个域名
  1 个域名无法解析（站点已失效）：

  ✗ www.example-dead.org
      分类：实用站点导航
      站点：（站点名称）
      URL ：https://www.example-dead.org/music/
      原因：getaddrinfo failed

  建议：以上站点域名已不存在，核实后从 nav_data.yml 中移除。
  注：DNS 解析失败是唯一失效判据；403 / 超时 / 证书错误多为反爬或临时故障，不计入。

[2] 站点图标 —— 117 个站点
  ✓ 所有站点图标均已正常获取。
==============================================================================
```

两项检查都不会改动生成页面，也不会中断构建。

### 1. 站点失效判定标准

只有域名无法解析（`getaddrinfo failed` 等）才会被判定为失效。以下情况**均不计入失效**：

| 现象 | 为什么不判为失效 |
| :--- | :--- |
| `403` / `429` | 多为 Cloudflare 等反爬拦截页，站点实际存活 |
| 请求超时 / 连接被拒 | 网络或代理的临时问题，与站点存活无关 |
| 证书过期 | 站点仍可访问，属独立问题，需单独处理 |
| `5xx` | 服务端临时故障 |
| 跳转到登录页 | 站点存活，仅需登录 |

这样取舍是因为 DNS 解析失败是**唯一零误报**的判据。若把 `403` 或超时也当作失效，会把大量存活站点误报为失效站点，反而淹没真正的问题。

**实现要点**：

- **按域名去重**：多个条目共用同一域名时只查询一次
- **并发查询**：复用 `config.validation_workers` 配置的并发数
- **IDN 支持**：中文等国际化域名会先做 punycode 编码再解析，避免误报
- **跳过非站点条目**：`#` 锚点，以及无法解析出域名的条目不参与检测
- **绝不抛异常**：任何未预期错误都会降级为「跳过该项」，检测本身不会导致构建失败

**后续可扩展方向**：当前输出层只报告 DNS 失效，判定逻辑已按分级结构组织，后续如需收紧可按优先级扩展：证书过期 → `404/410` → 登录跳转。`403` 与超时**不建议**纳入站点检查，实测证明其噪音极大。

### 2. 站点图标报告的四类问题

终端报告的 `[2] 站点图标` 段按严重程度分四类输出。

| 分类 | 含义 | 建议处理 |
| :--- | :--- | :--- |
| **无可用图标** | 站点 favicon 与两个兜底服务都没有有效图标，页面显示灰色占位图 | 手动为该条目指定 `icon` |
| **配置图标已失效** | 你配置的 `icon` 校验失败，页面静默降级用了别的来源 | 替换失效链接，或删除该字段交由自动获取 |
| **兜底图标域名已失效** | 兜底图标 URL 指向的站点域名已停止解析，图标必然加载失败 | 先处理失效站点本身 |
| **依赖第三方图标服务** | 图标能用，但取自 Google / Yandex 而非站点自身 | 介意网络依赖时可手动指定 |

第三、四类是**信息提示**而非错误：前者说明图标一定加载不出来，后者只说明来源不理想。若觉得第四类噪音过多，可关闭：

```yaml
config:
  report_fallback_icons: false   # 默认 true，仅影响第四类是否输出
```

### 3. 关闭健康检查

`nav_data.yml` 中可按需关闭：

```yaml
config:
  dead_link_check: false         # 关闭全部健康检查（默认 true）
  report_fallback_icons: false   # 只关闭「依赖第三方图标服务」一类（默认 true）
```

也可在构建时通过环境变量临时跳过（便于在 CI 中排查问题）：

```bash
NAV_SKIP_DEAD_LINK_CHECK=1 mkdocs build
```

## 并发校验加速

当 `nav_data.yml` 中的站点较多，且存在「自动抓取元数据 / 自动发现图标 / 兜底图标服务」等网络请求时，构建期会成为瓶颈。项目已将「单个站点条目」的校验与抓取任务改为并发执行。

### 1. 并发粒度与顺序稳定性

- 并发粒度为单个导航项（`items` 中的每个站点）
- 并发仅影响构建期的网络请求执行方式，不会改变最终页面的渲染顺序
- 构建日志会按原始 `items` 顺序输出，避免并发日志交错导致难以排查

### 2. 配置方式

优先级从高到低：

1. 环境变量
    - `NAV_VALIDATION_WORKERS`
    - `NAV_VALIDATE_WORKERS`（兼容字段）
2. `nav_data.yml` 配置

```yaml
config:
  validation_workers: 12
```

### 3. 默认并发数

未配置时，会根据 CPU 核心数自动给出一个偏 I/O 并发的默认值（范围 4~24），用于加速网络请求密集的构建流程。

### 4. 注意事项

- 如果遇到 `403` / `429` 或图标源带有反爬/挑战页（例如部分 CDN 会返回 Cloudflare challenge 页面），建议适当降低 `validation_workers`，或对相关站点/图标改用本地图标
- 并发请求会对目标站点造成更高瞬时访问压力，建议在 CI 环境中使用更保守的并发数

## 自动化构建原理

项目使用 `hooks.py` 在构建前自动读取配置文件（`nav_data.yml`），并通过 `build.py` 生成 `docs/index.md`。无需手动运行生成脚本，每次构建或预览时会自动更新。

构建脚本支持**彩色终端输出**，清晰展示构建过程中的元数据抓取、图标检查和回退逻辑：

| 标记 | 含义 |
| :--- | :--- |
| `[FETCH]` | 正在抓取网页元数据 |
| `[AUTO]` | 成功自动获取到标题、描述或图标 |
| `[CHECK]` | 正在检查手动配置的图标有效性 |
| `[OK]` | 配置有效 |
| `[SKIP]` | 抓取到的网页图标链接返回不符合图片格式 |
| `[FALLBACK]` | 进入图标获取失败时的三级自动回退流程 |
| `[FOUND]` | 在回退流程中成功找到可用图标 |
| `[WARN/ERROR]` | 异常情况或抓取失败提示 |
| `[DEFAULT]` | 所有尝试均失败，使用默认 SVG 图标 |

## 开发规划

- [x] 支持 GitHub 站点搜索功能
- [x] 增加多线程并发处理机制，以加快构建速度
- [x] 构建期检测失效站点（DNS 解析失败），并在终端输出末尾汇总提醒
- [x] 构建期将 `api.iconify.design` 相关图标迁移至 `cdn.simpleicons.org` 与本地图标
- [x] 构建期逐条目核对站点图标，输出无图标 / 配置图标失效 / 兜底域名失效的站点清单

## 许可证

本项目采用 MIT 许可证。

## 致谢

本项目基于以下优秀的开源项目构建，特此感谢：

- [MkDocs Material](https://github.com/squidfunk/mkdocs-material) - 强大的文档构建主题
- [MkDocs MaterialX](https://github.com/jaywhj/mkdocs-materialx) - Material 主题的扩展与增强
- [MkDocs](https://github.com/mkdocs/mkdocs) - 静态站点生成器
