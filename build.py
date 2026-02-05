import yaml
import os
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# CSS styles
CUSTOM_CSS = """
<style>
/* Adjust the sidebar width and content gap if needed */
@media screen and (min-width: 76.25em) {
    :root {
        --md-sidebar-primary-width: 10.5rem; /* default 12.1rem */
    }
}

/* Balance the visual center of gravity (Desktop, Expanded Sidebar Only) */
@media screen and (min-width: 76.25em) {
    body:not(.sidebar-collapsed) .md-content {
        padding-right: 8px;
    }
}

/* Custom grid layout for navigation */
.md-typeset .grid.cards {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important;
    gap: 0.6rem;
    display: grid;
}

.md-typeset .grid.cards > ul {
    display: contents;
    list-style: none;
    margin: 0;
    padding: 0;
}

/* Make the whole card clickable */
.md-typeset .grid.cards > ul > li {
    position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 0.5rem;
    padding: 0.8rem;
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 0 !important;
    background-color: var(--md-default-bg-color);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    height: 100%;
}

.md-typeset .grid.cards > ul > li:hover {
    transform: translateY(-2px);
    box-shadow: var(--md-shadow-depth-2);
    border-color: var(--md-accent-fg-color);
    z-index: 1;
}

/* Icon styling */
.nav-icon {
    flex-shrink: 0;
    margin-right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-icon img {
    width: 48px;
    height: 48px;
    border-radius: 4px;
    object-fit: contain;
}

/* Content styling (Title + Description) */
.nav-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex-grow: 1;
    overflow: hidden;
}

.nav-title {
    font-weight: bold;
    font-size: 0.95rem; /* Slightly reduced from 1rem */
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

.nav-desc {
    font-size: 0.75rem;
    margin-top: 0.05rem;
    color: var(--md-default-fg-color--light);
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.md-typeset .grid.cards > ul > li a {
    text-decoration: none;
    color: inherit;
}

.nav-link-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    border-radius: 0.5rem;
}

/* Sidebar navigation adjustments */
html .md-sidebar .md-nav__link {
    font-size: .9rem !important;
    line-height: 1.8 !important;
    padding: 4px 8px !important;
    margin: 0 !important;
    border-radius: 4px !important;
    transition: background-color 0.2s ease;
}

html .md-sidebar .md-nav__link:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
    text-decoration: none !important;
}

[data-md-color-scheme="slate"] html .md-sidebar .md-nav__link:hover {
    background-color: rgba(255, 255, 255, 0.08) !important;
}

html .md-sidebar .md-nav__link--active {
    padding-left: 10px !important;
}

/* Remove background from active sidebar link*/
html body .md-sidebar .md-nav__link--active:not([href^="#"]) {
    background: transparent !important;
    color: inherit !important;
    font-weight: 500 !important;
    padding-left: 25px !important;
    letter-spacing: 4px !important; /* Added spacing */
    font-size: 1.2em !important;
}

/* Utility to hide the H1 title */
.hidden-h1 {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Custom styling for Category Headers (H2) */
.md-typeset h2.nav-category-title {
    font-size: 1.0rem !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.8rem !important;
    font-weight: 700 !important;
    color: var(--md-default-fg-color);
}

/* Sidebar Icon Styles */
.md-nav__link .nav-icon-wrapper {
    display: inline-flex;
    align-items: center;
    margin-right: 0.2em;
    vertical-align: middle;
    position: relative;
    top: 3px; /* Fine-tune vertical alignment */
}

.md-nav__link .nav-icon-wrapper svg {
    width: 1.1em;
    height: 1.1em;
    fill: currentColor;
}

/* Search Box Styles */
.nav-search-container {
    display: flex;
    justify-content: center;
    margin: 0.25rem 0 1.5rem 0;
    width: 100%;
}

.nav-search-wrapper {
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 600px;
    background: var(--md-default-bg-color);
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 24px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s, border-color 0.2s;
    overflow: hidden;
}

.nav-search-wrapper:focus-within {
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    border-color: var(--md-accent-fg-color);
}

.search-engine-select {
    border: none;
    background: transparent;
    padding: 0 1rem;
    height: 48px;
    font-size: 0.9rem;
    color: var(--md-default-fg-color);
    cursor: pointer;
    border-right: 1px solid var(--md-default-fg-color--lightest);
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    /* Custom arrow */
    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23999%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
    background-repeat: no-repeat;
    background-position: right 0.7rem top 50%;
    background-size: 0.65rem auto;
    padding-right: 2rem;
}

.search-engine-select option {
    background-color: var(--md-default-bg-color);
    color: var(--md-default-fg-color);
}

.nav-search-input {
    flex-grow: 1;
    border: none;
    height: 48px;
    padding: 0 1rem;
    font-size: 0.95rem;
    background: transparent;
    color: var(--md-default-fg-color);
    outline: none;
}

.nav-search-btn {
    border: none;
    background: transparent;
    width: 48px;
    height: 48px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    fill: var(--md-default-fg-color--light);
    transition: fill 0.2s;
}

.nav-search-btn:hover {
    fill: var(--md-accent-fg-color);
}

.nav-search-btn svg {
    width: 24px;
    height: 24px;
}

/* Mobile Sidebar Customization */
@media screen and (max-width: 76.1875em) {
    /* Title Font and Spacing */
    html .md-sidebar .md-nav__link {
        font-size: 0.85rem !important; /* Reduced from .9rem (Desktop) */
        line-height: 1.6 !important;    /* Reduced from 1.8 (Desktop) */
    }

    /* Icon Size Representation */
    .md-nav__link .nav-icon-wrapper svg {
        width: 1.1em !important; /* Match desktop relative size */
        height: 1.1em !important;
    }

    /* Increase spacing between icon and text */
    .md-nav__link .nav-icon-wrapper {
        margin-right: 0.4em !important; /* Increased from 0.2em (Desktop) */
    }
}
</style>
"""

TOGGLE_CSS = """
<style>
/* Sidebar Toggle Button */
#sidebar-toggle {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 100;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--md-default-bg-color);
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    border: 1px solid var(--md-default-fg-color--lightest);
    color: var(--md-default-fg-color);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    opacity: 0.6;
}

#sidebar-toggle:hover {
    opacity: 1;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    transform: scale(1.05);
}

/* Toggle Icon Visibility */
#sidebar-toggle .toggle-icon-collapsed { display: none; }
#sidebar-toggle .toggle-icon-expanded { display: flex; }

body.sidebar-collapsed #sidebar-toggle .toggle-icon-collapsed { display: flex; }
body.sidebar-collapsed #sidebar-toggle .toggle-icon-expanded { display: none; }

#sidebar-toggle span {
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

/* Hide on mobile (use native drawer) */
@media screen and (max-width: 76.1875em) {
    #sidebar-toggle {
        display: none;
    }
}

/* Collapsed State (Desktop Only) */
@media screen and (min-width: 76.25em) {
    body.sidebar-collapsed .md-sidebar--primary {
        display: none;
    }
    
    body.sidebar-collapsed .md-content {
        max-width: 1400px;
        margin: 0 auto;
    }
}
</style>
"""

SEARCH_HTML = """
<div id="nav-search-container" class="nav-search-container">
    <div class="nav-search-wrapper">
        <select id="search-engine-select" class="search-engine-select">
            <option value="local">站内</option>
            <option value="google">Google</option>
            <option value="bing">Bing</option>
            <option value="github">Github</option>
            <option value="baidu">百度</option>
            <option value="bilibili">Bilibili</option>
            <option value="zhihu">知乎</option>
        </select>
        <input type="text" id="nav-search-input" class="nav-search-input" placeholder="搜索资源..." autocomplete="off">
        <button id="nav-search-btn" class="nav-search-btn">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" /></svg>
        </button>
    </div>
</div>
"""

TOGGLE_HTML = """
<button id="sidebar-toggle" title="Toggle Sidebar" markdown="1">
<span class="toggle-icon-expanded">:material-menu-open:</span>
<span class="toggle-icon-collapsed">:material-menu-close:</span>
</button>
"""

SEARCH_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('nav-search-input');
    const select = document.getElementById('search-engine-select');
    const btn = document.getElementById('nav-search-btn');
    const items = document.querySelectorAll('.grid.cards > ul > li');
    
    // Store original placeholders
    const placeholders = {
        'local': '搜索资源...',
        'google': 'Google 搜索...',
        'bing': 'Bing 搜索...',
        'github': 'Github 搜索...',
        'baidu': '百度搜索...',
        'bilibili': 'Bilibili 搜索...',
        'zhihu': '知乎搜索...'
    };

    function performSearch() {
        const query = input.value.trim();
        const engine = select.value;

        if (engine === 'local') {
            const lowerQuery = query.toLowerCase();
            
            // Iterate over each category grid
            const grids = document.querySelectorAll('.grid.cards');
            grids.forEach(grid => {
                const listItems = grid.querySelectorAll('ul > li');
                let hasVisibleItems = false;
                
                listItems.forEach(item => {
                    const title = item.querySelector('.nav-title').textContent.toLowerCase();
                    const desc = item.querySelector('.nav-desc').textContent.toLowerCase();
                    
                    if (title.includes(lowerQuery) || desc.includes(lowerQuery)) {
                        item.style.display = '';
                        hasVisibleItems = true;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                // Find the associated category header (H2)
                let sibling = grid.previousElementSibling;
                while (sibling && sibling.tagName !== 'H2') {
                    sibling = sibling.previousElementSibling;
                }
                
                // Toggle visibility of the grid and the header
                if (hasVisibleItems) {
                    grid.style.display = '';
                    if (sibling && sibling.classList.contains('nav-category-title')) {
                        sibling.style.display = '';
                    }
                } else {
                    grid.style.display = 'none';
                    if (sibling && sibling.classList.contains('nav-category-title')) {
                        sibling.style.display = 'none';
                    }
                }
            });
        } else {
            if (!query) return;
            let url = '';
            if (engine === 'google') url = 'https://www.google.com/search?q=' + encodeURIComponent(query);
            if (engine === 'bing') url = 'https://www.bing.com/search?q=' + encodeURIComponent(query);
            if (engine === 'github') url = 'https://github.com/search?q=' + encodeURIComponent(query);
            if (engine === 'baidu') url = 'https://www.baidu.com/s?wd=' + encodeURIComponent(query);
            if (engine === 'bilibili') url = 'https://search.bilibili.com/all?keyword=' + encodeURIComponent(query);
            if (engine === 'zhihu') url = 'https://www.zhihu.com/search?type=content&q=' + encodeURIComponent(query);
            if (url) window.open(url, '_blank');
        }
    }

    input.addEventListener('input', function() {
        if (select.value === 'local') performSearch();
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') performSearch();
    });

    select.addEventListener('change', function() {
        input.focus();
        input.placeholder = placeholders[this.value] || '搜索...';
        
        if (this.value === 'local') {
            performSearch();
        } else {
            // Restore visibility when switching to external search
            items.forEach(item => item.style.display = '');
        }
    });
    
    btn.addEventListener('click', performSearch);
});
</script>
"""

ICON_JS = """
<script>
function handleImageError(img) {
    const cloudSvg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="#9e9e9e"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/></svg>';
    
    // Get current fallback level (default 0)
    let level = parseInt(img.getAttribute('data-fallback-level') || '0');
    
    // Attempt to extract domain from the sibling link
    let hostname = null;
    try {
        const item = img.closest('li');
        const link = item ? item.querySelector('a.nav-link-overlay') : null;
        if (link && link.href) {
            hostname = new URL(link.href).hostname;
        }
    } catch (e) {
        // parsing failed
    }

    // If we can't find a hostname, give up immediately
    if (!hostname) {
        img.onerror = null;
        if (img.parentNode) img.parentNode.innerHTML = cloudSvg;
        return;
    }

    // Check if current src is already Google (handle build-time fallback)
    if (level === 0 && img.src.includes('google.com/s2/favicons')) {
        level = 1;
    }

    if (level === 0) {
        // Level 0 -> 1: Try Google
        img.setAttribute('data-fallback-level', '1');
        img.src = 'https://www.google.com/s2/favicons?domain=' + hostname + '&sz=64';
    } else if (level === 1) {
        // Level 1 -> 2: Try Yandex (Backup for China/Network issues)
        img.setAttribute('data-fallback-level', '2');
        img.src = 'https://favicon.yandex.net/favicon/' + hostname + '?size=32';
    } else {
        // Level 2+ -> Give up, show SVG
        img.onerror = null;
        if (img.parentNode) {
            img.parentNode.innerHTML = cloudSvg;
        }
    }
}
</script>
"""

SIDEBAR_ICON_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Find all category headers
    const headers = document.querySelectorAll('.nav-category-title');
    
    headers.forEach(header => {
        const categoryId = header.id;
        // MkDocs Material wraps icons in .twemoji span
        const iconElement = header.querySelector('.twemoji') || header.querySelector('svg');
        
        if (categoryId && iconElement) {
            // Find the sidebar link with the corresponding href
            const sidebarLink = document.querySelector(`.md-sidebar .md-nav__link[href="#${categoryId}"]`);
            
            // Only add if found and doesn't already have our wrapper
            if (sidebarLink && !sidebarLink.querySelector('.nav-icon-wrapper')) {
                // Prepend icon
                const iconSpan = document.createElement('span');
                iconSpan.className = 'nav-icon-wrapper';
                // Clone the icon from the header
                iconSpan.appendChild(iconElement.cloneNode(true));
                
                // Insert before the text node
                if (sidebarLink.firstChild) {
                    sidebarLink.insertBefore(iconSpan, sidebarLink.firstChild);
                } else {
                    sidebarLink.appendChild(iconSpan);
                }
            }
        }
    });
});
</script>
"""

TOGGLE_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const body = document.body;
    const STATE_KEY = 'sidebar-collapsed';
    const defaultCollapsed = {DEFAULT_COLLAPSED};
    
    // Load state
    const savedState = localStorage.getItem(STATE_KEY);
    
    if (savedState === 'true' || (savedState === null && defaultCollapsed)) {
        body.classList.add('sidebar-collapsed');
    }
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            body.classList.toggle('sidebar-collapsed');
            localStorage.setItem(STATE_KEY, body.classList.contains('sidebar-collapsed'));
            
            // Trigger resize event to help layout adjust if needed
            window.dispatchEvent(new Event('resize'));
        });
    }
});
</script>
"""

def validate_icon(url, headers):
    """
    Validate an icon URL by performing a GET request.
    Checks for status 200, valid image content-type, and permissible CORP headers.
    Returns the URL if valid, None otherwise.
    """
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '').lower()
            corp = response.headers.get('Cross-Origin-Resource-Policy', '').lower()

            # 1. CORB Check: Must be an image type
            if any(t in content_type for t in ['text/html', 'application/json', 'application/xml']):
                print(f"  {Colors.WARNING}[SKIP]{Colors.ENDC} Non-image Content-Type: {url} ({content_type})")
                return None

            if not content_type.startswith('image/'):
                is_ico = url.endswith('.ico') or response.url.endswith('.ico')
                if not (is_ico and len(response.content) > 0):
                    print(f"  {Colors.WARNING}[SKIP]{Colors.ENDC} Invalid Content-Type: {url} ({content_type})")
                    return None

            # 2. CORP Check
            if corp in ['same-origin', 'same-site']:
                print(f"  {Colors.WARNING}[SKIP]{Colors.ENDC} CORP Block: {url} (Policy: {corp})")
                return None
            
            if len(response.content) > 0:
                return url
    except:
        pass
    return None

def extract_icon_from_soup(soup, url, headers):
    # Search for icon links (icon, shortcut icon, apple-touch-icon)
    icon_rel = ['icon', 'shortcut icon', 'apple-touch-icon']
    icon_links = soup.find_all('link', rel=lambda x: x and x.lower() in icon_rel)
    
    for link in icon_links:
        href = link.get('href')
        if href:
            if href.startswith('data:'):
                if 'image' not in href or len(href) < 20:
                    continue
            
            full_icon_url = urljoin(url, href)
            if validate_icon(full_icon_url, headers):
                return full_icon_url
    return None

def fetch_site_metadata(url):
    if not url or url.startswith('#'):
        return None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {}
        
        # Title
        if soup.title and soup.title.string:
            result['title'] = soup.title.string.strip()
            
        # Description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                    soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            content = meta_desc.get('content', '')
            if content:
                result['description'] = content.strip()
                
        # Icon
        icon_url = extract_icon_from_soup(soup, url, headers)
        if icon_url:
            result['icon'] = icon_url
            
        return result

    except Exception as e:
        print(f"  {Colors.FAIL}[ERROR]{Colors.ENDC} Could not fetch metadata for {url}: {e}")
        return None

def get_fallback_icon(url):
    if not url or url.startswith('#'):
        return None
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    parsed_url = urlparse(url)
    if not (parsed_url.scheme and parsed_url.netloc):
        return None

    # 1. Favicon.ico
    favicon_url = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"
    if validate_icon(favicon_url, headers):
        return favicon_url
    
    # 2. Google
    google_url = f"https://www.google.com/s2/favicons?domain={parsed_url.netloc}&sz=64"
    try:
        g_resp = requests.get(google_url, timeout=5)
        if g_resp.status_code == 200:
            md5 = hashlib.md5(g_resp.content).hexdigest()
            if md5 != "b8a0bf372c762e966cc99ede8682bc71":
                return google_url
            else:
                print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Google returned default globe icon.")
        else:
            print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Google returned status {g_resp.status_code}.")
    except Exception as e:
        print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Google check failed: {e}")

    # 3. Yandex
    yandex_url = f"https://favicon.yandex.net/favicon/{parsed_url.netloc}?size=32"
    try:
        y_resp = requests.get(yandex_url, timeout=5)
        if y_resp.status_code == 200:
            md5 = hashlib.md5(y_resp.content).hexdigest()
            if md5 != "5047fd356fc4802e4fe471ae09f9efe5":
                return yandex_url
            else:
                print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Yandex returned default empty icon.")
        else:
            print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Yandex returned status {y_resp.status_code}.")
    except Exception as e:
        print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Yandex check failed: {e}")
            
    print(f"  {Colors.HEADER}[DEFAULT]{Colors.ENDC} Using default SVG icon.")
    return None

def generate_nav():
    with open('nav_data.yml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Default configuration
    output_filename = 'index.md'
    meta = {}
    nav_items = []

    # Parse config and nav data
    if isinstance(data, dict):
        config = data.get('config', {})
        if 'filename' in config:
            output_filename = config['filename']
        if 'meta' in config:
            meta.update(config['meta'])
        nav_items = data.get('nav', [])
    elif isinstance(data, list):
        nav_items = data
    else:
        print(f"{Colors.FAIL}Error: Invalid nav_data.yml format.{Colors.ENDC}")
        return

    content = []
    
    # Generate Front Matter
    content.append("---")
    if meta:
        content.append(yaml.dump(meta, default_flow_style=False, allow_unicode=True).strip())
    content.append("---")
    content.append("")
    
    # Inject CSS
    content.append(CUSTOM_CSS)
    content.append(TOGGLE_CSS)
    content.append("")
    
    # Inject Search UI
    content.append(SEARCH_HTML)
    content.append(TOGGLE_HTML)
    content.append("")
    content.append(SEARCH_JS)
    
    # Process TOGGLE_JS with config
    sidebar_collapsed = config.get('sidebar_collapsed', False)
    js_content = TOGGLE_JS.replace('{DEFAULT_COLLAPSED}', 'true' if sidebar_collapsed else 'false')
    content.append(js_content)
    
    content.append("")
    content.append(ICON_JS)
    content.append("")
    content.append(SIDEBAR_ICON_JS)
    content.append("")
    
    # Add a hidden H1 to prevent MkDocs from auto-generating one
    title = meta.get('title', '导航站')
    content.append(f"# {title} {{ .hidden-h1 }}")
    content.append("")
    
    for i, category in enumerate(nav_items):
        cat_id = f"category-{i+1}"
        cat_name = category['category']
        cat_icon = category.get('icon', '')
        
        # Build header text with icon if present
        header_text = cat_name
        if cat_icon:
            # Convert material/name to :material-name:
            markdown_icon = f":{cat_icon.replace('/', '-')}:"
            header_text = f"{markdown_icon} {cat_name}"
        
        # Added .nav-category-title class to H2 and explicit ID
        content.append(f"## {header_text} {{ #{cat_id} .nav-category-title }}")
        content.append("")
        content.append('<div class="grid cards">')
        content.append('<ul>')
        
        for item in category['items']:
            name = item.get('name', '')
            url = item.get('url', '#')
            desc = item.get('description', '')
            icon = item.get('icon', '')

            # Validate manually configured icon
            if icon:
                if icon.startswith('http://') or icon.startswith('https://'):
                    print(f"{Colors.OKCYAN}[CHECK]{Colors.ENDC} Checking icon for {name}...")
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    if validate_icon(icon, headers):
                        print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} {icon}")
                    else:
                        print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Remote icon validation failed for {name} ({icon})")
                else:
                    # Local path check (relative to docs/)
                    print(f"{Colors.OKCYAN}[CHECK]{Colors.ENDC} Checking local icon for {name}...")
                    local_path = os.path.join('docs', icon.lstrip('/\\'))
                    if os.path.exists(local_path):
                        print(f"  {Colors.OKGREEN}[OK]{Colors.ENDC} {local_path}")
                    else:
                        print(f"  {Colors.WARNING}[WARN]{Colors.ENDC} Local icon file not found for {name}: {local_path}")
            
            # Auto-fetch metadata if needed
            if (not name or not desc or not icon) and url and not url.startswith('#'):
                print(f"{Colors.OKCYAN}[FETCH]{Colors.ENDC} Fetching metadata for {url}...")
                metadata = fetch_site_metadata(url)
                if metadata:
                    if not name and metadata.get('title'):
                        name = metadata['title']
                        print(f"  {Colors.WARNING}[AUTO]{Colors.ENDC} + Title: {name}")
                    if not desc and metadata.get('description'):
                        desc = metadata['description']
                        print(f"  {Colors.WARNING}[AUTO]{Colors.ENDC} + Desc: {desc}")
                    if not icon and metadata.get('icon'):
                        icon = metadata['icon']
                        print(f"  {Colors.WARNING}[AUTO]{Colors.ENDC} + Icon: {icon}")

            # Fallback for name if still missing (use hostname)
            if not name and url:
                parsed = urlparse(url)
                if parsed.netloc:
                    name = parsed.netloc
                    print(f"  {Colors.WARNING}[AUTO]{Colors.ENDC} + Title (Fallback): {name}")

            # Fallback for icon if still missing
            if not icon and url and not url.startswith('#'):
                print(f"{Colors.OKCYAN}[FALLBACK]{Colors.ENDC} Fetching fallback icon for {name or url}...")
                fallback_icon = get_fallback_icon(url)
                if fallback_icon:
                    icon = fallback_icon
                    print(f"  {Colors.OKGREEN}[FOUND]{Colors.ENDC} {icon}")
            
            icon_html = ""
            if icon:
                # Add no-referrer if it's a remote URL to prevent tracking/hotlinking blocking
                referrer_policy = ' referrerpolicy="no-referrer"' if icon.startswith('http') else ''
                img_attrs = f'src="{icon}" alt="{name}" onerror="handleImageError(this)"{referrer_policy}'
                icon_html = f'<img {img_attrs}>'
            else:
                 icon_html = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="#9e9e9e"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/></svg>'
            
            content.append('<li>')
            content.append(f'<div class="nav-icon">{icon_html}</div>')
            content.append('<div class="nav-content">')
            content.append(f'<div class="nav-title">{name}</div>')
            content.append(f'<div class="nav-desc">{desc}</div>')
            content.append('</div>')
            content.append(f'<a href="{url}" class="nav-link-overlay" title="{name}"></a>')
            content.append('</li>')
            
        content.append('</ul>')
        content.append('</div>')
        content.append("")

    output_path = os.path.join('docs', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"{Colors.OKGREEN}Navigation page generated successfully in {output_path}{Colors.ENDC}")

if __name__ == '__main__':
    generate_nav()
