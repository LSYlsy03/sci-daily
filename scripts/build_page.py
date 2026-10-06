# -*- coding: utf-8 -*-
"""根据 data/daily_*.json 生成/更新静态网页到 site/，含首页（最新一天）和历史归档"""
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SITE = BASE / "site"
SITE.mkdir(exist_ok=True)

STARS = {i: "★" * i + "☆" * (5 - i) for i in range(1, 6)}

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         max-width: 720px; margin: 0 auto; padding: 16px; background: #f7f8fa; color: #222; }}
  header {{ border-bottom: 2px solid #2b6cb0; padding-bottom: 8px; margin-bottom: 16px; }}
  h1 {{ font-size: 1.3em; margin: 4px 0; }}
  .date {{ color: #667; font-size: .9em; }}
  .card {{ background: #fff; border-radius: 12px; padding: 14px 16px; margin-bottom: 14px;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .stars {{ color: #f5a623; font-size: 1.05em; }}
  h2 {{ font-size: 1.1em; margin: 4px 0 6px; }}
  .meta {{ color: #888; font-size: .85em; margin-bottom: 6px; }}
  .kw {{ background: #e8f0fe; color: #2b6cb0; border-radius: 6px; padding: 1px 8px;
         font-size: .85em; margin-right: 6px; display: inline-block; }}
  .summary {{ font-size: .98em; }}
  .interp {{ font-size: .92em; color: #444; margin-top: 6px; }}
  .why {{ font-size: .85em; color: #999; margin-top: 4px; }}
  a.btn {{ display: inline-block; margin-top: 8px; color: #2b6cb0; text-decoration: none;
           border: 1px solid #2b6cb0; border-radius: 6px; padding: 3px 12px; font-size: .88em; }}
  .empty {{ text-align: center; color: #999; padding: 40px 0; }}
  nav a {{ color: #2b6cb0; text-decoration: none; margin-right: 12px; }}
  ul.archive {{ list-style: none; padding: 0; }}
  ul.archive li {{ background: #fff; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; }}
</style>
</head>
<body>
<header>
  <h1>🧪 小学科学 · 每日前沿拓展</h1>
  <div class="date">四—六年级科学课堂拓展素材 · {date}</div>
</header>
{body}
<footer style="color:#aaa;font-size:.8em;text-align:center;margin-top:20px">
  每天自动抓取生成 · 原文版权归原作者所有
</footer>
</body>
</html>
"""


def item_html(c):
    kws = "".join(f'<span class="kw">{k.strip()}</span>'
                  for k in str(c.get("knowledge", "")).replace("，", ",").split(",") if k.strip())
    return f"""<div class="card">
  <div class="stars">{STARS[c['grade']]} <span style="color:#999;font-size:.8em">好用程度</span></div>
  <h2>{c['title']}</h2>
  <div class="meta">来源：{c.get('source','')} · {c.get('grade_reason','')}</div>
  <div class="summary">🎯 {c.get('summary','')}</div>
  <div class="interp">📖 {c.get('interpretation','')}</div>
  <div style="margin-top:6px">{kws}</div>
  <a class="btn" href="{c['link']}" target="_blank">查看原文 ↗</a>
</div>"""


def build_day(day_data):
    items = day_data["items"]
    if not items:
        body = '<div class="empty">今天没有筛选出合适的新闻</div>'
    else:
        body = "\n".join(item_html(c) for c in items)
    return PAGE_TMPL.format(title=f"每日科学拓展 {day_data['date']}",
                            date=day_data["date"], body=body)


def main():
    days = sorted(DATA.glob("daily_*.json"))
    if not days:
        print("没有 daily 文件，跳过")
        return

    # 各日期页
    dates = []
    for f in days:
        d = json.loads(f.read_text(encoding="utf-8"))
        (SITE / f"{d['date']}.html").write_text(build_day(d), encoding="utf-8")
        dates.append(d["date"])

    # 首页 = 最新一天
    latest = json.loads(days[-1].read_text(encoding="utf-8"))
    (SITE / "index.html").write_text(build_day(latest), encoding="utf-8")

    # 归档页
    lis = "\n".join(f'<li><a href="{dt}.html">{dt}</a></li>' for dt in reversed(dates))
    (SITE / "archive.html").write_text(
        PAGE_TMPL.format(title="历史归档", date="全部",
                         body=f'<nav><a href="index.html">← 最新一期</a></nav><h2>📚 历史归档</h2><ul class="archive">{lis}</ul>'),
        encoding="utf-8")
    print(f"网页已生成/更新：{len(dates)} 期，最新 {dates[-1]}")


if __name__ == "__main__":
    main()
