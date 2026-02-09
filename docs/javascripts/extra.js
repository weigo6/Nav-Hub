/* ASK AI按钮和音乐控制按钮与播放器自动避让页脚 */
document.addEventListener("DOMContentLoaded", function () {
    
    // 1. 按钮避让页脚逻辑 (Footer Avoidance Logic)
    function updateFooterAvoidance() {
        if (window.innerWidth <= 720) {
            // 如果屏幕变窄，清除 JS 设置的 bottom 样式，恢复 CSS 默认值
            const elements = [
                document.getElementById("ask-ai-toggle"),
                document.getElementById("sidebar-toggle"),
                document.getElementById("music-player-toggle"),
                document.getElementById("music-player-container")
            ];
            
            elements.forEach(el => {
                if (el) el.style.bottom = "";
            });
            return;
        }

        const footer = document.querySelector(".md-footer") || document.querySelector("footer");
        if (!footer) return;

        const footerRect = footer.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const distanceToFooter = viewportHeight - footerRect.top;

        // 基础底部距离 (Base bottom offset)
        const baseBottom = 20;
        let offset = 0;

        if (distanceToFooter > 0) {
            offset = distanceToFooter;
        }

        // 更新 Ask AI 按钮位置
        const askAiToggle = document.getElementById("ask-ai-toggle");
        if (askAiToggle) {
            askAiToggle.style.bottom = `${baseBottom + offset}px`;
        }

        // 更新 侧边栏切换按钮位置
        const sidebarToggle = document.getElementById("sidebar-toggle");
        if (sidebarToggle) {
            sidebarToggle.style.bottom = `${baseBottom + offset}px`;
        }
        
        // 更新音乐播放器按钮位置 (位于 Ask AI 上方 52px)
        const musicToggle = document.getElementById("music-player-toggle");
        if (musicToggle) {
            musicToggle.style.bottom = `${baseBottom + 52 + offset}px`;
        }
        
        // 更新音乐播放器容器位置
        const musicContainer = document.getElementById("music-player-container");
        if (musicContainer) {
            musicContainer.style.bottom = `${baseBottom + offset}px`;
        }
    }

    // 2. 音乐播放器可见性与位置逻辑 (Player Visibility & Position Logic)
    function updatePlayerVisibility() {
        const musicToggle = document.getElementById("music-player-toggle");
        const musicContainer = document.getElementById("music-player-container");
        if (!musicToggle) return;

        // Check if sidebar toggle is visible (it's hidden on mobile via CSS)
        // If sidebarToggle is visible (Desktop), move music player to the left
        // If sidebarToggle is hidden (Mobile), keep music player on the right
        const sidebarToggle = document.getElementById("sidebar-toggle");
        const isSidebarVisible = sidebarToggle && window.getComputedStyle(sidebarToggle).display !== 'none';
        
        // Check Chat State for Window Avoidance
        const chatWindow = document.getElementById("ask-ai-window");
        const isChatOpen = chatWindow && chatWindow.classList.contains("open");

        if (isSidebarVisible) {
            // 桌面端逻辑：音乐播放器在左侧
            musicToggle.style.left = "20px";
            musicToggle.style.right = "auto";
            
            // Ensure music button is visible on the left, even if chat is open
            musicToggle.style.display = '';

            if (musicContainer) {
                musicContainer.classList.add("music-player-left");
                // Ensure display is reset in case it was hidden on the right side
                musicContainer.style.display = '';
            }
        } else {
            // 移动端逻辑：音乐播放器在右侧 (Right Side Logic)
            if (isChatOpen) {
                // Chat is Open: Hide Button & Close Player
                musicToggle.style.display = 'none';
                musicToggle.classList.remove("active");
                
                // Move hidden button to right (state consistency)
                musicToggle.style.right = "20px";
                musicToggle.style.left = "auto";

                if (musicContainer) {
                    // FORCE HIDE to prevent any visual flash of the player jumping to the right
                    musicContainer.style.display = 'none';
                    musicContainer.classList.remove("show");
                    musicContainer.classList.remove("music-player-left");
                }
            } else {
                // Chat is Closed: Normal Mobile Behavior
                musicToggle.style.display = '';
                musicToggle.style.right = "20px";
                musicToggle.style.left = "auto";
                
                if (musicContainer) {
                    musicContainer.classList.remove("music-player-left");
                    // Restore display in case it was hidden
                    musicContainer.style.display = '';
                }
            }
        }
    }

    // 事件监听
    window.addEventListener("scroll", updateFooterAvoidance);
    
    // Resize 需要同时更新两者（因为既可能改变页脚相对位置，也可能触发桌面/移动端布局切换）
    window.addEventListener("resize", () => {
        updateFooterAvoidance();
        updatePlayerVisibility();
    });
    
    // 初始化检查 (延时一小段时间以确保动态元素已加载)
    setTimeout(() => {
        updateFooterAvoidance();
        updatePlayerVisibility();

        // 监听 Ask AI 窗口的 class 变化，只触发可见性更新
        const chatWindow = document.getElementById("ask-ai-window");
        if (chatWindow) {
            const observer = new MutationObserver(() => {
                updatePlayerVisibility();
            });
            observer.observe(chatWindow, { attributes: true, attributeFilter: ['class'] });
        }
    }, 100);
});
