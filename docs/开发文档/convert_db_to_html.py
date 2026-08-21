"""数据库设计文档 Markdown → HTML 转换器

特性：
- 侧边栏 TOC 自动生成 + 滚动高亮
- SQL 代码块一键复制按钮
- SVG 居中显示 + 暗色主题
- 代码高亮（pymdown 扩展）
- 响应式布局
"""

import re
from pathlib import Path
import markdown
from markdown.extensions.toc import TocExtension

DOC = Path(__file__).parent / "数据库设计文档.md"
OUT = Path(__file__).parent / "数据库设计文档.html"

md_text = DOC.read_text(encoding="utf-8")

# 提取标题生成 TOC
def extract_toc(md):
    """从 Markdown 提取 h1/h2/h3 标题生成 TOC 树"""
    lines = md.split("\n")
    toc = []
    for line in lines:
        m = re.match(r'^(#{1,3})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            # 移除 emoji 和特殊字符保留锚点
            slug = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', title).strip('-').lower()
            toc.append((level, title, slug))
    return toc

toc = extract_toc(md_text)
print(f"[OK] 提取到 {len(toc)} 个标题")

# 配置 markdown
md_engine = markdown.Markdown(
    extensions=[
        'extra',
        'tables',
        'fenced_code',
        'codehilite',
        TocExtension(toc_depth="1-3", anchorlink=False),
        'pymdownx.superfences',
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
        'admonition',
    ],
    extension_configs={
        'codehilite': {'css_class': 'highlight', 'guess_lang': False},
    }
)

body = md_engine.convert(md_text)

# 提取 TOC（从 markdown 引擎）
toc_tokens = md_engine.toc_tokens

def build_toc_html(tokens):
    """递归构建 TOC HTML（tokens 是 markdown TocExtension 的嵌套字典）"""
    html = []
    for t in tokens:
        if 'children' in t and t['children']:
            html.append(f'<li class="toc-l{t["level"]}"><a href="#{t["id"]}">{t["name"]}</a>')
            html.append('<ul>')
            html.append(build_toc_html(t['children']))
            html.append('</ul></li>')
        else:
            html.append(f'<li class="toc-l{t["level"]}"><a href="#{t["id"]}">{t["name"]}</a></li>')
    return "".join(html)

toc_html = build_toc_html(toc_tokens) if toc_tokens else ""


# 模板
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YD家居 · 数据库设计文档</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/core.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/sql.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/python.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/languages/bash.min.js"></script>
<style>
:root {{
  --bg: #ffffff;
  --bg-secondary: #fafafa;
  --bg-code: #1f2937;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --border: #e5e7eb;
  --border-strong: #d1d5db;
  --primary: #0d9488;
  --primary-light: #ccfbf1;
  --accent: #f59e0b;
  --sidebar-bg: #1e293b;
  --sidebar-text: #cbd5e1;
  --sidebar-active: #5eead4;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
  background: var(--bg);
}}
/* Layout */
.layout {{ display: flex; min-height: 100vh; }}
.sidebar {{
  width: 280px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow-y: auto;
  padding: 24px 16px;
  z-index: 100;
}}
.sidebar h1 {{
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  padding: 0 4px;
}}
.sidebar .subtitle {{
  font-size: 11px;
  color: #94a3b8;
  margin: 0 0 24px 0;
  padding: 0 4px;
}}
.sidebar ul {{ list-style: none; padding: 0; margin: 0; }}
.sidebar li {{ margin: 2px 0; }}
.sidebar a {{
  display: block;
  color: var(--sidebar-text);
  text-decoration: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}}
.sidebar a:hover {{ background: #334155; color: #fff; }}
.sidebar a.active {{
  background: #334155;
  color: var(--sidebar-active);
  border-left-color: var(--sidebar-active);
}}
.toc-l1 {{ font-weight: 600; }}
.toc-l2 {{ padding-left: 16px !; }}
.toc-l3 {{ padding-left: 28px !; font-size: 12px; }}
/* Main */
.main {{
  margin-left: 280px;
  flex: 1;
  padding: 40px 60px;
  max-width: calc(100% - 280px);
}}
@media (max-width: 1024px) {{
  .sidebar {{ transform: translateX(-100%); transition: transform 0.3s; }}
  .sidebar.open {{ transform: translateX(0); }}
  .main {{ margin-left: 0; max-width: 100%; padding: 24px; }}
}}
.menu-toggle {{
  display: none;
  position: fixed;
  top: 16px; left: 16px;
  z-index: 200;
  background: var(--sidebar-bg);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
}}
@media (max-width: 1024px) {{ .menu-toggle {{ display: block; }} }}
/* Typography */
h1 {{ font-size: 28px; font-weight: 700; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); }}
h2 {{ font-size: 22px; font-weight: 700; margin: 28px 0 12px; padding-bottom: 6px; border-bottom: 1px solid var(--border-strong); }}
h3 {{ font-size: 18px; font-weight: 600; margin: 24px 0 10px; }}
h4 {{ font-size: 16px; font-weight: 600; margin: 20px 0 8px; }}
p {{ margin: 12px 0; }}
/* Tables */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 13px;
}}
th {{
  background: #1f2937;
  color: #fff;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
}}
td {{
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
tr:hover td {{ background: var(--bg-secondary); }}
/* Code */
pre {{
  background: var(--bg-code);
  color: #e5e7eb;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  font-size: 12px;
  line-height: 1.5;
  position: relative;
}}
code {{
  font-family: "Fira Code", "Cascadia Code", Consolas, Monaco, monospace;
  font-size: 0.9em;
}}
:not(pre) > code {{
  background: #f3f4f6;
  color: #db2777;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
}}
pre code {{ padding: 0; background: none; color: inherit; }}
/* Copy button */
.copy-btn {{
  position: absolute;
  top: 8px; right: 8px;
  background: #374151;
  color: #e5e7eb;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 11px;
  opacity: 0;
  transition: opacity 0.2s;
}}
pre:hover .copy-btn {{ opacity: 1; }}
.copy-btn:hover {{ background: #4b5563; }}
/* Images (SVGs) */
img {{
  max-width: 100%;
  height: auto;
  display: block;
  margin: 16px auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
}}
/* Blockquote */
blockquote {{
  border-left: 4px solid var(--primary);
  background: var(--primary-light);
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 8px 8px 0;
  color: #134e4a;
}}
blockquote p {{ margin: 4px 0; }}
/* Strong / em */
strong {{ font-weight: 700; color: #0f172a; }}
em {{ font-style: italic; color: var(--text-secondary); }}
/* Lists */
ul, ol {{ margin: 8px 0; padding-left: 28px; }}
li {{ margin: 4px 0; }}
/* Links */
a {{ color: var(--primary); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
/* Header anchor offset for sticky if needed */
:target {{ scroll-margin-top: 20px; }}
/* Footer note */
.doc-footer {{
  margin-top: 60px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-tertiary);
}}
</style>
</head>
<body>
<button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰ 目录</button>
<div class="layout">
  <aside class="sidebar">
    <h1>YD家居 · 数据库设计</h1>
    <p class="subtitle">v1.0 · 33 张表 + 2 视图 + 触发器</p>
    <ul>{toc_html}</ul>
  </aside>
  <main class="main">
{body}
    <div class="doc-footer">
      <p>📐 本文档配套：<code>figures/*.svg</code>（ER 图）· <code>数据库设计文档_install_all.sql</code>（一键脚本）· <code>迁移脚本/alembic/versions/001_initial.py</code></p>
      <p>版本 v1.0 · 2026-08-18 · 基于 PRD v1.1 + 开发技术文档 + 用户最新字段约定</p>
    </div>
  </main>
</div>
<script>
// 代码块添加复制按钮
document.querySelectorAll('pre code').forEach(function(block) {{
  const btn = document.createElement('button');
  btn.className = 'copy-btn';
  btn.textContent = '复制';
  btn.addEventListener('click', function() {{
    navigator.clipboard.writeText(block.textContent).then(function() {{
      btn.textContent = '已复制 ✓';
      setTimeout(function() {{ btn.textContent = '复制'; }}, 1500);
    }});
  }});
  block.parentElement.appendChild(btn);
}});

// 代码高亮
if (typeof hljs !== 'undefined') {{
  hljs.highlightAll();
}}

// 滚动高亮侧边栏
const tocLinks = document.querySelectorAll('.sidebar a');
const headingMap = new Map();
tocLinks.forEach(function(link) {{
  const anchor = link.getAttribute('href').slice(1);
  const target = document.getElementById(anchor);
  if (target) headingMap.set(target, link);
}});

function updateActiveHeading() {
  const scrollTop = window.scrollY + 100;
  let activeHeading = null;
  headingMap.forEach(function(link, heading) {{
    if (heading.offsetTop <= scrollTop) {{
      activeHeading = link;
    }}
  }});
  tocLinks.forEach(function(l) {{ l.classList.remove('active'); }});
  if (activeHeading) activeHeading.classList.add('active');
}}

window.addEventListener('scroll', updateActiveHeading);
updateActiveHeading();
</script>
</body>
</html>
"""

final_html = HTML_TEMPLATE
final_html = final_html.replace("{toc_html}", toc_html)
final_html = final_html.replace("{body}", body)

OUT.write_text(final_html, encoding="utf-8")
print(f"[OK] {OUT.name} ({len(final_html)} bytes)")