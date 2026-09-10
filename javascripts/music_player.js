const MUSIC_ICON = `<svg viewBox="0 0 24 24"><path d="M12,3V12.26C11.5,12.09 11,12 10.5,12C8,12 6,14 6,16.5C6,19 8,21 10.5,21C13,21 15,19 15,16.5V6H19V3H12Z" /></svg>`;

/* ===================== 播放器数据源配置 ===================== *
 * MetingJS 会把 URL 里的 :server / :type / :id / :r 占位符替换成实际参数，
 * 所以占位符必须保留，不要删。
 *
 * 页面加载时按顺序探测这些实例，第一个「HTTP 200 且返回非空数组」的实例
 * 会被真正使用；全部不可用时不会显示音乐按钮，避免出现点了没反应的死按钮。
 *
 * 注意：这些都是个人维护的公益实例，没有可用性保证，随时可能限流或下线。
 * 想长期稳定请自建 Meting-API（PHP / Vercel / Cloudflare Worker），
 * 然后把自建地址放到数组第一位。
 * ========================================================== */
const METING_APIS = [
    // 实测较快（约 80ms），返回 Access-Control-Allow-Origin: *，音频流 200 audio/mpeg
    "https://api.injahow.cn/meting/?server=:server&type=:type&id=:id&r=:r",
    // 备用实例（实测约 400ms，同一歌单同样可用）
    "https://api.qijieya.cn/meting/?server=:server&type=:type&id=:id&r=:r",
];

// 歌单配置：server 音乐平台 / type 资源类型 / id 资源 ID
const MUSIC_SOURCE = {
    server: "netease", // netease 网易云, tencent QQ音乐, kugou, xiami, baidu
    type: "playlist", // song 单曲, playlist 歌单, album 专辑, search 搜索, artist 歌手
    id: "17741904561", // 资源 ID（如网易云歌单 ID）
};

const API_PROBE_TIMEOUT = 3000; // 单个实例的探测超时（毫秒）
const PLAYER_MOUNT_TIMEOUT = 12000; // 挂载后等待播放器出现的兜底时间（毫秒）

document.addEventListener("DOMContentLoaded", function () {
    // Only initialize if the toggle button doesn't exist yet
    if (document.getElementById("music-player-toggle")) return;

    createMusicUI();
    mountPlayer();
});

/** 探测数据源，成功后挂载 MetingJS 播放器 */
async function mountPlayer() {
    const api = await pickMetingApi();
    if (!api) {
        teardownMusicUI("所有 Meting 接口均不可用");
        return;
    }
    mountMetingPlayer(api);
    watchPlayerMount();
}

/** 依次探测实例，返回第一个可用的 api 模板（全部失败返回 null） */
async function pickMetingApi() {
    for (const template of METING_APIS) {
        if (await probeApi(probeUrl(template))) {
            console.info("[music-player] 使用接口:", template);
            return template;
        }
        console.warn("[music-player] 接口不可用，尝试下一个:", template);
    }
    return null;
}

/** 把 api 模板里的占位符换成真实参数，用于探测 */
function probeUrl(template) {
    return template
        .replace(":server", MUSIC_SOURCE.server)
        .replace(":type", MUSIC_SOURCE.type)
        .replace(":id", MUSIC_SOURCE.id)
        .replace(":r", Math.random());
}

/** 探测单个实例：必须 HTTP 200 且返回非空曲目数组才算可用 */
async function probeApi(url) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), API_PROBE_TIMEOUT);
    try {
        const res = await fetch(url, { signal: controller.signal, cache: "no-store" });
        if (!res.ok) return false;
        const data = await res.json();
        return Array.isArray(data) && data.length > 0;
    } catch (e) {
        return false;
    } finally {
        clearTimeout(timer);
    }
}

/** 挂载 MetingJS 元素（需 APlayer 已就绪） */
function mountMetingPlayer(apiTemplate) {
    const playerContainer = document.getElementById("music-player-container");
    if (!playerContainer || playerContainer.querySelector("meting-js")) return;
    if (!window.APlayer || !window.customElements) return;

    // Create MetingJS Element
    const metingElement = document.createElement("meting-js");
    metingElement.setAttribute("api", apiTemplate);
    metingElement.setAttribute("server", MUSIC_SOURCE.server);
    metingElement.setAttribute("type", MUSIC_SOURCE.type);
    metingElement.setAttribute("id", MUSIC_SOURCE.id);
    metingElement.setAttribute("fixed", "false"); // ！吸底模式必须为 false，否则自定义样式失效
    metingElement.setAttribute("mini", "false"); // ！迷你模式必须为 false，否则自定义样式失效
    metingElement.setAttribute("autoplay", "false");
    metingElement.setAttribute("list-folded", "true");
    metingElement.setAttribute("theme", "#2980b9");
    metingElement.setAttribute("volume", "0.7");
    metingElement.setAttribute("preload", "none");

    playerContainer.appendChild(metingElement);
}

/**
 * 兜底：若数据源在探测通过之后中途失效（MetingJS 内部不处理 fetch 异常），
 * 播放器不会出现，此时移除按钮，而不是留一个点了没反应的死按钮。
 */
function watchPlayerMount() {
    const playerContainer = document.getElementById("music-player-container");
    setTimeout(() => {
        if (!playerContainer || playerContainer.querySelector(".aplayer")) return;
        teardownMusicUI("播放器未能在超时前初始化，数据源可能已失效");
    }, PLAYER_MOUNT_TIMEOUT);
}

/** 数据源不可用时移除播放器 UI */
function teardownMusicUI(reason) {
    console.warn("[music-player] " + reason + "，已隐藏音乐按钮");
    const toggleBtn = document.getElementById("music-player-toggle");
    if (toggleBtn) toggleBtn.remove();
    const playerContainer = document.getElementById("music-player-container");
    if (playerContainer) playerContainer.remove();
}

function createMusicUI() {
    // Create Toggle Button
    const toggleBtn = document.createElement("button");
    toggleBtn.id = "music-player-toggle";
    toggleBtn.title = "Music Player";
    toggleBtn.innerHTML = MUSIC_ICON;
    document.body.appendChild(toggleBtn);

    // Create Player Container
    const playerContainer = document.createElement("div");
    playerContainer.id = "music-player-container";
    document.body.appendChild(playerContainer);

    // Toggle Logic
    toggleBtn.addEventListener("click", () => {
        playerContainer.classList.toggle("show");
        toggleBtn.classList.toggle("active");
    });
}
