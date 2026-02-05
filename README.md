# 基于 Mkdocs-material/MaterialX 的导航站

基于 MkDocs Material (MaterialX) 架构的静态导航站点。在此处查看 [演示站点](https://nav.sufine.top) 。

推荐使用 [MaterialX](https://github.com/jaywhj/mkdocs-materialx) ，以拥抱现代化的界面设计。

> Zensical 框架同样适用此项目，但是截止目前（2026.02），Zensical 不支持插件与 hooks 自动化脚本，无法将 `build.py` 构建MD文档的工作流并入 `Zensical build` 中，您需要手动执行。

## 功能

- **自动化构建**: 从 `nav_data.yml` 自动生成导航页面
- **响应式设计**: 适配桌面端和移动端
- **桌面端侧边栏**: 支持点击左下角按钮折叠/展开侧边栏
- **状态记忆**: 自动记住用户上次的侧边栏折叠状态
- **高度可配置**: 支持自定义分类、图标、默认侧边栏状态等
- **智能图标管理**: 内置多级图标自动获取与容错机制
- **智能元数据获取**: 只需填写 URL，自动抓取网站标题、描述和图标

## 项目结构

```text
.
├── nav_data.yml      # [核心] 导航数据与功能配置文件
├── mkdocs.yml        # MkDocs 站点配置文件
├── build.py          # 构建脚本：处理数据并生成 index.md
├── hooks.py          # MkDocs 钩子：在构建前触发 build.py
├── docs/             # 文档源目录
│   ├── index.md      # [程序自动生成] 导航主页
│   ├── images/       # 图片资源
│   └── stylesheets/  # 自定义样式
├── site/             # [程序自动生成] 静态站点输出目录
└── README.md         # 项目说明文档
```

## 快速开始

### 1. 安装依赖

确保已安装 MkDocs-MaterialX （或者选择安装 Mkdocs-material）及相关项目依赖：

```bash
pip install mkdocs-materialx
# 或 pip install mkdocs-material

# 安装项目运行所需的依赖
pip install beautifulsoup4 requests PyYAML
```

### 2. 配置文件 (`nav_data.yml`)

项目的所有配置和导航数据都在 `nav_data.yml` 中管理。

#### 基础配置

```yaml
config:
  filename: index.md         # 生成的目标文件名
  sidebar_collapsed: false   # (可选) 是否默认收起侧边栏。true: 默认收起; false: 默认展开
  meta:
    title: 导航目录          # 页面标题
    description: 站点描述    # 页面描述
```

#### 添加导航链接

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

> 如果网站元数据抓取失败，程序会自动提取 URL 的域名 `hostname` 作为标题，`description` 会保持为空，站点图标将会执行Fallback策略（当时从谷歌图标服务、Yandex 图标接口获取站点图标）。

### 3. 系统配置 (`mkdocs.yml`)

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
  - pymdownx.emoji: # 用于渲染图标
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg

# 4. 建议启用的 Markdown 拓展
markdown_extensions:
  - toc:
      permalink: true # 启用标题锚点链接
```

### 4. 运行项目

**本地预览**:
```bash
mkdocs serve
```

**构建站点**:
```bash
mkdocs build
```

## 侧边栏功能说明

- **折叠/展开**: 桌面端左下角提供切换按钮。
    - 展开状态图标: `material/menu-open`
    - 收起状态图标: `material/menu-close`
- **默认状态**: 可在 `nav_data.yml` 中通过 `config.sidebar_collapsed` 设置初始状态。

## 图标获取机制

项目采用了一套 **3+3 多重保障** 的图标获取与显示策略，最大程度确保图标的正确显示与访问隐私。

### 1. 手动配置与校验 (Manual Configuration & Validation)
当您在 `nav_data.yml` 中显式配置 `icon` 字段时，构建脚本会自动执行有效性检查：

*   **在线 SVG/图片**: 支持直接使用 Iconify 等在线 SVG 源（例如 `https://api.iconify.design/logos:google-icon.svg`）。脚本会发起请求验证链接连通性与内容类型。
    *   若验证失败（如 404 或非图片），构建日志将输出警告（`Warning: Remote icon validation failed...`），但**不会**自动替换为您配置的链接，以便您排查问题。
*   **本地路径**: 检查 `docs/` 目录下是否存在对应文件。若文件缺失，将输出警告。

### 2. 构建时自动发现 (Build-time Discovery)
当 `nav_data.yml` 中的导航项未手动指定 `icon` 时，构建脚本 (`build.py`) 会按以下优先级自动寻找图标，并执行**全链路严格校验**：

1.  **HTML 智能抓取**: 访问目标网站解析 `<link rel="icon">` 等标签。
    *   **严格验证**: 对抓取到的图标进行 GET 实测，拦截 403 Forbidden、空内容或**非图片类型**（如重定向到 HTML 页面导致的 CORB 问题）。
    *   **稳健策略**: 请求超时时间延长至 5 秒。若验证过程超时，脚本将**跳过**该图标并尝试回退方案，以避免引入不稳定或错误的链接。
2.  **原生路径探测**: 若抓取失败，尝试探测默认路径 `{url}/favicon.ico`（同样执行上述严格验证与稳健策略）。
3.  **智能兜底服务 (Smart Fallback Service)**:
    *   **Google 优先验证**: 尝试从 **Google Favicon 服务** 获取图标，并自动校验 MD5 指纹。若返回默认的无效图标（如"灰色地球"），则自动弃用。
    *   **Yandex 备选**: 若 Google 验证不通过，自动切换尝试 **Yandex Favicon 服务**，同样包含针对默认空图标的指纹校验。
    *   **最终回退**: 若两者均无效，则直接使用 SVG 占位符，避免显示误导性图标。

> **隐私保护**: 所有远程图标在生成 HTML 时均会自动添加 `referrerpolicy="no-referrer"` 属性，防止用户访问记录被第三方追踪，同时绕过部分网站的防盗链限制。

### 3. 运行时智能容错 (Runtime Intelligent Fallback)
生成的网页包含智能的错误处理脚本 (`ICON_JS`)，当浏览器无法加载图标时，会自动按以下 "三级火箭" 策略降级：

1.  **Level 1 (Google)**: 原始图标加载失败时，自动尝试从 Google Favicon 服务 (`google.com/s2/favicons`) 加载。
2.  **Level 2 (Yandex)**: 若 Google 服务也被拦截或失败，自动切换至 **Yandex Favicon 服务** (`favicon.yandex.net`)。这为中国大陆等特定网络环境提供了强有力的备选保障。
3.  **Level 3 (Placeholder)**: 若所有服务均不可用，最终显示默认的灰色云朵占位图。

这一机制确保了即使原站开启了反爬虫或浏览器拦截了跨域图片，用户仍能看到有效的图标。

### 4. 本地图标支持 (Local Icons)

如果您希望使用本地图片作为项目图标，请遵循以下步骤：

1.  **存放文件**: 将您的图标文件放入 `docs/images/` 目录（或 `docs/` 下的任意子目录）。
    - 例如：`docs/images/custom-icon.png`
2.  **配置引用**: 在 `nav_data.yml` 中，将 `icon` 字段设置为相对于 `docs` 目录的路径。
    - 例如：`icon: images/custom-icon.png`

> **注意**: 请确保图标文件确实位于 `docs` 目录下，否则 MkDocs 构建时无法将其包含在最终站点中。

## 自动化构建原理

项目使用 `hooks.py` 在构建前自动读取 configuration file (`nav_data.yml`) 并通过 `build.py` 生成 `docs/index.md`。无需手动运行生成脚本，每次构建或预览时会自动更新。

构建脚本支持**彩色终端输出**，清晰展示构建过程中的元数据抓取、图标检查和回退逻辑：
- `[FETCH]`: 正在抓取网页元数据
- `[AUTO]`: 成功自动获取到标题、描述或图标
- `[CHECK]`: 正在检查手动配置的图标有效性
- `[OK]`: 配置有效
- `[SKIP]`: 抓取到的网页图标链接返回不符合图片格式
- `[FALLBACK]`: 进入图标获取失败时的三级自动回退流程
- `[FOUND]`: 在回退流程中成功找到可用图标
- `[WARN/ERROR]`: 异常情况或抓取失败提示
- `[DEFAULT]`: 所有尝试均失败，使用默认 SVG 图标

## 开发规划

- [ ] 支持 Github 站点搜索功能
- [ ] 增加多线程并发处理机制，以加快构建速度

## 许可证

本项目采用 MIT 许可证。

## 致谢

本项目基于以下优秀的开源项目构建，特此感谢：

- [MkDocs Material](https://github.com/squidfunk/mkdocs-material) - 强大的文档构建主题
- [MkDocs MaterialX](https://github.com/jaywhj/mkdocs-materialx) - Material 主题的扩展与增强
- [MkDocs](https://github.com/mkdocs/mkdocs) - 静态站点生成器