#!/usr/bin/env python3
"""Convert UI/UX Markdown spec to styled HTML with sidebar navigation."""

import markdown
import re
from pathlib import Path

MD_PATH = Path(r"D:\WorkBuddy_1\2026-08-13-09-43-40\YD家居\UI文档\UI-UX设计规格文档.md")
HTML_PATH = Path(r"D:\WorkBuddy_1\2026-08-13-09-43-40\YD家居\UI文档\UI-UX设计规格文档.html")

md_text = MD_PATH.read_text(encoding="utf-8")

# Convert markdown to HTML
md = markdown.Markdown(extensions=[
    "tables",
    "fenced_code",
    "attr_list",
    "pymdownx.highlight",
    "pymdownx.superfences",
    "pymdownx.tilde",
    "sane_lists",
], extension_configs={
    "pymdownx.highlight": {"use_pygments": False},
})
body_html = md.convert(md_text)

# Build sidebar TOC from headings
toc_items = []
for line in md_text.split("\n"):
    m = re.match(r'^(#{1,3})\s+(.+)', line)
    if m:
        level = len(m.group(1))
        title = m.group(2).strip()
        # Remove markdown formatting
        title_clean = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
        title_clean = re.sub(r'`(.+?)`', r'\1', title_clean)
        # Generate anchor
        anchor = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title_clean)
        anchor = re.sub(r'\s+', '-', anchor.strip().lower())
        if level <= 2:
            indent = "" if level == 1 else "  " if level == 2 else "    "
            toc_items.append(f'{indent}<a href="#{anchor}" class="toc-l{level}">{title_clean}</a>')

toc_html = "\n".join(toc_items)

# Add IDs to headings in body_html
def add_heading_ids(html):
    def replacer(match):
        tag = match.group(1)
        content = match.group(2)
        text = re.sub(r'<[^>]+>', '', content)
        anchor = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', text)
        anchor = re.sub(r'\s+', '-', anchor.strip().lower())
        return f'<{tag} id="{anchor}">{content}</{tag}>'
    return re.sub(r'<(h[1-3])>(.*?)</\1>', replacer, html, flags=re.DOTALL)

body_html = add_heading_ids(body_html)

# Full HTML template
html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>YD家居 UI/UX 设计规格文档</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Sans+3:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
  --c-bg: #FAFAF9;
  --c-surface: #FFFFFF;
  --c-ink: #1C1917;
  --c-text: #44403C;
  --c-muted: #78716C;
  --c-border: #E7E5E4;
  --c-gold: #CA8A04;
  --c-gold-light: #FEF3C7;
  --c-primary: #1677ff;
  --c-code-bg: #1C1917;
  --c-code-text: #F5F5F4;
  --sidebar-w: 280px;
}}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Source Sans 3', 'Inter', sans-serif;
  background: var(--c-bg);
  color: var(--c-text);
  line-height: 1.7;
  font-size: 15px;
}}

/* ===== Sidebar ===== */
#sidebar {{
  position: fixed;
  left: 0; top: 0; bottom: 0;
  width: var(--sidebar-w);
  background: var(--c-ink);
  color: #D6D3D1;
  overflow-y: auto;
  padding: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}}
#sidebar .logo {{
  padding: 20px 24px;
  border-bottom: 1px solid #44403C;
  display: flex;
  align-items: center;
  gap: 10px;
}}
#sidebar .logo .badge {{
  width: 36px; height: 36px;
  border-radius: 8px;
  background: var(--c-gold);
  color: var(--c-ink);
  font-weight: 700;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}}
#sidebar .logo .title {{
  font-size: 15px;
  font-weight: 600;
  color: #FAFAF9;
}}
#sidebar .logo .subtitle {{
  font-size: 11px;
  color: #A8A29E;
}}
#sidebar nav {{ padding: 12px 0; }}
#sidebar nav a {{
  display: block;
  padding: 6px 24px;
  font-size: 13px;
  color: #A8A29E;
  text-decoration: none;
  transition: all 0.15s;
  border-left: 3px solid transparent;
}}
#sidebar nav a.toc-l1 {{
  font-weight: 600;
  color: #FAFAF9;
  font-size: 13px;
  margin-top: 12px;
  padding-top: 10px;
  border-bottom: 1px solid #292524;
}}
#sidebar nav a.toc-l1:first-child {{ margin-top: 0; }}
#sidebar nav a.toc-l2 {{
  padding-left: 36px;
  font-size: 12.5px;
}}
#sidebar nav a:hover {{
  color: var(--c-gold);
  background: #292524;
  border-left-color: var(--c-gold);
}}
#sidebar nav a.active {{
  color: var(--c-gold);
  border-left-color: var(--c-gold);
}}

/* ===== Main Content ===== */
#main {{
  margin-left: var(--sidebar-w);
  padding: 40px 48px 80px;
  max-width: 1100px;
}}
#main h1 {{
  font-family: 'Inter', sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: var(--c-ink);
  margin: 48px 0 20px;
  padding-bottom: 12px;
  border-bottom: 3px solid var(--c-gold);
  line-height: 1.3;
}}
#main h1:first-child {{ margin-top: 0; }}
#main h2 {{
  font-family: 'Inter', sans-serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--c-ink);
  margin: 36px 0 16px;
  padding-left: 12px;
  border-left: 4px solid var(--c-gold);
}}
#main h3 {{
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--c-ink);
  margin: 28px 0 12px;
}}
#main h4 {{
  font-size: 16px;
  font-weight: 600;
  color: var(--c-text);
  margin: 20px 0 8px;
}}
#main p {{ margin: 10px 0; }}
#main ul, #main ol {{ margin: 10px 0 10px 24px; }}
#main li {{ margin: 4px 0; }}

/* Tables */
#main table {{
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 13.5px;
  background: var(--c-surface);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
#main th {{
  background: #1C1917;
  color: #FAFAF9;
  font-weight: 600;
  text-align: left;
  padding: 10px 14px;
  font-size: 13px;
}}
#main td {{
  padding: 9px 14px;
  border-bottom: 1px solid var(--c-border);
  vertical-align: top;
}}
#main tr:last-child td {{ border-bottom: none; }}
#main tr:hover td {{ background: #FAFAF9; }}

/* Code */
#main code {{
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  background: #F5F5F4;
  color: #B45309;
  padding: 2px 6px;
  border-radius: 4px;
}}
#main pre {{
  background: var(--c-code-bg);
  color: var(--c-code-text);
  padding: 18px 20px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 16px 0;
  font-size: 13px;
  line-height: 1.6;
}}
#main pre code {{
  background: none;
  color: var(--c-code-text);
  padding: 0;
  font-size: 13px;
}}

/* Blockquotes */
#main blockquote {{
  border-left: 4px solid var(--c-gold);
  background: var(--c-gold-light);
  padding: 12px 18px;
  margin: 16px 0;
  border-radius: 0 8px 8px 0;
  color: var(--c-ink);
}}
#main blockquote p {{ margin: 4px 0; }}

/* HR */
#main hr {{
  border: none;
  border-top: 2px solid var(--c-border);
  margin: 40px 0;
}}

/* Links */
#main a {{
  color: var(--c-gold);
  text-decoration: none;
  font-weight: 500;
}}
#main a:hover {{ text-decoration: underline; }}

/* ASCII art / pre without code */
#main pre:not(:has(code)) {{
  background: #F5F5F4;
  color: var(--c-text);
  border: 1px solid var(--c-border);
}}

/* Mobile toggle */
#sidebarToggle {{
  display: none;
  position: fixed;
  top: 16px; left: 16px;
  z-index: 200;
  width: 40px; height: 40px;
  border-radius: 8px;
  background: var(--c-ink);
  color: var(--c-gold);
  border: none;
  cursor: pointer;
  font-size: 20px;
  align-items: center;
  justify-content: center;
}}

/* Responsive */
@media (max-width: 1024px) {{
  #sidebar {{ transform: translateX(-100%); }}
  #sidebar.open {{ transform: translateX(0); }}
  #main {{ margin-left: 0; padding: 60px 24px 60px; }}
  #sidebarToggle {{ display: flex; }}
}}

/* Print */
@media print {{
  #sidebar {{ display: none; }}
  #main {{ margin-left: 0; padding: 0; }}
  #sidebarToggle {{ display: none; }}
}}

/* Scrollbar */
#sidebar::-webkit-scrollbar {{ width: 6px; }}
#sidebar::-webkit-scrollbar-track {{ background: #1C1917; }}
#sidebar::-webkit-scrollbar-thumb {{ background: #44403C; border-radius: 3px; }}
#main pre::-webkit-scrollbar {{ height: 6px; }}
#main pre::-webkit-scrollbar-thumb {{ background: #44403C; border-radius: 3px; }}
</style>
</head>
<body>

<button id="sidebarToggle" aria-label="切换目录">☰</button>

<aside id="sidebar">
  <div class="logo">
    <span class="badge">YD</span>
    <div>
      <div class="title">UI/UX 设计规格</div>
      <div class="subtitle">v1.0 · 2026-08-18</div>
    </div>
  </div>
  <nav id="tocNav">
{toc_html}
  </nav>
</aside>

<main id="main">
{body_html}
</main>

<script>
// Mobile sidebar toggle
const toggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
toggle.addEventListener('click', () => sidebar.classList.toggle('open'));

// Active TOC highlight on scroll
const headings = document.querySelectorAll('#main h1, #main h2');
const tocLinks = document.querySelectorAll('#tocNav a');
const headingMap = new Map();
tocLinks.forEach(link => {{
  const anchor = link.getAttribute('href').slice(1);
  headingMap.set(anchor, link);
}});

function updateActiveToc() {{
  let current = '';
  for (const h of headings) {{
    if (h.getBoundingClientRect().top < 120) {{
      current = h.id;
    }}
  }}
  tocLinks.forEach(link => link.classList.remove('active'));
  if (current && headingMap.has(current)) {{
    headingMap.get(current).classList.add('active');
  }}
}}
window.addEventListener('scroll', updateActiveToc, {{ passive: true }});
updateActiveToc();

// Close sidebar on mobile when clicking a link
tocLinks.forEach(link => {{
  link.addEventListener('click', () => {{
    if (window.innerWidth <= 1024) sidebar.classList.remove('open');
  }});
}});
</script>

</body>
</html>
"""

HTML_PATH.write_text(html_template, encoding="utf-8")
print(f"HTML generated: {HTML_PATH}")
print(f"Size: {HTML_PATH.stat().st_size / 1024:.1f} KB")
