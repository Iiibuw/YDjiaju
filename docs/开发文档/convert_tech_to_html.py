"""将开发技术文档 Markdown 转换为带样式的可浏览 HTML。

特性：
- 左侧暗色侧边栏目录（自动提取 h2/h3）
- 滚动高亮当前位置
- 代码块深色主题 + 一键复制
- 表格美化
- SVG 图片自适应
- 响应式（移动端可折叠侧边栏）
"""

from pathlib import Path
import re
import markdown
from markdown.extensions.toc import TocExtension

ROOT = Path(__file__).parent
MD_FILE = ROOT / "开发技术文档.md"
OUT_FILE = ROOT / "开发技术文档.html"


def md_to_html():
    md_text = MD_FILE.read_text(encoding="utf-8")

    # 自定义：调整图片语法，让相对路径 figures/*.svg 正确加载
    md_text = md_text.replace("figures/", "figures/")  # 已是相对路径

    md_engine = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "codehilite",
            TocExtension(toc_depth="2-3", anchorlink=False),
            "sane_lists",
            "nl2br",
        ],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": False},
        },
    )
    body = md_engine.convert(md_text)

    # 提取所有 heading 用于 JS 侧边栏渲染
    headings = re.findall(
        r'<h([23]) id="([^"]+)">(.+?)</h\1>',
        body,
        re.DOTALL,
    )

    # 简化侧边栏
    sidebar_items = [(int(lvl), hid, re.sub(r"<[^>]+>", "", txt)) for lvl, hid, txt in headings]

    html = HTML_TEMPLATE.replace("{{BODY}}", body).replace("{{SIDEBAR_ITEMS}}", json_dumps_items(sidebar_items))

    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"[OK] {OUT_FILE.name}  size={len(html):,} bytes")


def json_dumps_items(items):
    import json
    return json.dumps(items, ensure_ascii=False)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YD家居平台 · 开发技术文档</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #ffffff;
    --bg-secondary: #f7f8fa;
    --bg-sidebar: #1e293b;
    --bg-sidebar-hover: #334155;
    --bg-code: #1f2937;
    --text: #1f2937;
    --text-sub: #6b7280;
    --text-sidebar: #cbd5e1;
    --text-sidebar-active: #ffffff;
    --border: #e5e7eb;
    --primary: #1677ff;
    --primary-hover: #4096ff;
    --code-text: #e6edf3;
  }
  html, body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; font-size: 14px; }
  .layout { display: flex; min-height: 100vh; }
  .sidebar {
    width: 280px;
    background: var(--bg-sidebar);
    color: var(--text-sidebar);
    position: fixed;
    top: 0; left: 0; bottom: 0;
    overflow-y: auto;
    padding: 24px 0;
    z-index: 100;
  }
  .sidebar-title {
    padding: 0 24px 16px;
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 16px;
  }
  .sidebar-subtitle {
    padding: 0 24px 16px;
    font-size: 11px;
    color: var(--text-sidebar);
    opacity: 0.7;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 16px;
  }
  .sidebar ul { list-style: none; }
  .sidebar a {
    display: block;
    padding: 6px 24px 6px 32px;
    color: var(--text-sidebar);
    text-decoration: none;
    font-size: 13px;
    border-left: 2px solid transparent;
    transition: all 0.2s;
  }
  .sidebar a.toc-l2 { padding-left: 32px; font-weight: 500; }
  .sidebar a.toc-l3 { padding-left: 48px; font-size: 12px; opacity: 0.85; }
  .sidebar a:hover {
    background: var(--bg-sidebar-hover);
    color: var(--text-sidebar-active);
  }
  .sidebar a.active {
    background: rgba(22, 119, 255, 0.15);
    color: var(--text-sidebar-active);
    border-left-color: var(--primary);
  }
  .content {
    margin-left: 280px;
    padding: 32px 64px 64px;
    max-width: 1080px;
    min-width: 0;
  }
  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #1f2937;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 32px;
  }
  h2 {
    font-size: 22px;
    font-weight: 600;
    color: #1f2937;
    margin: 40px 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    scroll-margin-top: 24px;
  }
  h3 {
    font-size: 17px;
    font-weight: 600;
    color: #374151;
    margin: 28px 0 12px;
    scroll-margin-top: 24px;
  }
  h4 {
    font-size: 15px;
    font-weight: 600;
    color: #4b5563;
    margin: 20px 0 8px;
  }
  p { margin: 12px 0; }
  a { color: var(--primary); text-decoration: none; }
  a:hover { text-decoration: underline; }
  ul, ol { padding-left: 24px; margin: 12px 0; }
  li { margin: 4px 0; }
  hr { border: none; border-top: 1px dashed var(--border); margin: 32px 0; }
  strong { font-weight: 600; color: #1f2937; }
  blockquote {
    border-left: 3px solid var(--primary);
    padding: 8px 16px;
    margin: 16px 0;
    background: var(--bg-secondary);
    color: var(--text-sub);
    border-radius: 0 4px 4px 0;
  }
  code {
    background: rgba(22, 119, 255, 0.08);
    color: #c026d3;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: "JetBrains Mono", Consolas, Monaco, monospace;
    font-size: 0.92em;
  }
  pre {
    background: var(--bg-code);
    color: var(--code-text);
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 16px 0;
    font-family: "JetBrains Mono", Consolas, Monaco, monospace;
    font-size: 13px;
    line-height: 1.6;
    position: relative;
  }
  pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border-radius: 0;
  }
  .codehilite { background: transparent; }
  .codehilite .c { color: #8b949e; font-style: italic; }
  .codehilite .k { color: #ff7b72; }
  .codehilite .s { color: #a5d6ff; }
  .codehilite .s2 { color: #a5d6ff; }
  .codehilite .n { color: #e6edf3; }
  .codehilite .nb { color: #79c0ff; }
  .codehilite .nf { color: #d2a8ff; }
  .codehilite .mi { color: #79c0ff; }
  .codehilite .kc { color: #79c0ff; }
  .codehilite .kt { color: #ffa657; }
  .codehilite .kn { color: #ff7b72; }
  .codehilite .o { color: #ff7b72; }
  .codehilite .kn { color: #ff7b72; }
  pre .copy-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(255, 255, 255, 0.08);
    color: #e6edf3;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 11px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s;
  }
  pre:hover .copy-btn { opacity: 1; }
  pre .copy-btn:hover { background: rgba(255, 255, 255, 0.15); }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 13px;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
  }
  th {
    background: #1f2937;
    color: #ffffff;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
  }
  td {
    padding: 10px 14px;
    border-top: 1px solid var(--border);
    vertical-align: top;
  }
  tbody tr:hover { background: var(--bg-secondary); }
  tbody tr:nth-child(even) { background: #fafbfc; }
  tbody tr:nth-child(even):hover { background: var(--bg-secondary); }
  img { max-width: 100%; height: auto; border-radius: 6px; margin: 16px 0; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
  /* Mermaid 块 */
  pre code.language-mermaid {
    background: #f9fafb;
    color: #1f2937;
    display: block;
  }
  .menu-toggle {
    display: none;
    position: fixed;
    top: 16px; left: 16px;
    z-index: 200;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    cursor: pointer;
  }
  @media (max-width: 1024px) {
    .sidebar { transform: translateX(-100%); transition: transform 0.2s; }
    .sidebar.open { transform: translateX(0); }
    .content { margin-left: 0; padding: 24px 24px 64px; }
    .menu-toggle { display: block; }
  }
  @media print {
    .sidebar, .menu-toggle { display: none; }
    .content { margin-left: 0; padding: 0; max-width: 100%; }
  }
</style>
</head>
<body>
<button class="menu-toggle" onclick="toggleSidebar()">☰ 目录</button>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-title">YD家居平台</div>
    <div class="sidebar-subtitle">开发技术文档 · v1.0</div>
    <ul id="sidebar-list"></ul>
  </aside>
  <main class="content">
    {{BODY}}
  </main>
</div>
<script>
const SIDEBAR_ITEMS = {{SIDEBAR_ITEMS}};

// 渲染侧边栏
const list = document.getElementById('sidebar-list');
SIDEBAR_ITEMS.forEach(([lvl, id, text]) => {
  const li = document.createElement('li');
  const a = document.createElement('a');
  a.href = '#' + id;
  a.className = 'toc-l' + lvl;
  a.dataset.target = id;
  a.textContent = text;
  li.appendChild(a);
  list.appendChild(li);
});

// 滚动高亮
const headings = SIDEBAR_ITEMS.map(([, id]) => id);
const tocLinks = document.querySelectorAll('#sidebar-list a');
const headingMap = new Map();
tocLinks.forEach(link => {
  const anchor = link.getAttribute('href').slice(1);
  headingMap.set(anchor, link);
});

let activeId = null;
function updateActive() {
  let currentId = null;
  for (const hid of headings) {
    const el = document.getElementById(hid);
    if (!el) continue;
    const rect = el.getBoundingClientRect();
    if (rect.top <= 120) currentId = hid;
  }
  if (currentId && currentId !== activeId) {
    activeId = currentId;
    tocLinks.forEach(l => l.classList.remove('active'));
    const link = headingMap.get(currentId);
    if (link) link.classList.add('active');
  }
}
window.addEventListener('scroll', updateActive, { passive: true });
updateActive();

// 移动端切换
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// 点击锚点后关闭（移动端）
tocLinks.forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth <= 1024) {
      document.getElementById('sidebar').classList.remove('open');
    }
  });
});

// 代码块复制
document.querySelectorAll('pre').forEach(pre => {
  if (pre.querySelector('code.language-mermaid')) return;  // 跳过 mermaid
  const btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.textContent = '复制';
  btn.onclick = () => {
    const code = pre.querySelector('code');
    if (!code) return;
    navigator.clipboard.writeText(code.innerText).then(() => {
      btn.textContent = '已复制';
      setTimeout(() => btn.textContent = '复制', 1500);
    });
  };
  pre.appendChild(btn);
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    md_to_html()