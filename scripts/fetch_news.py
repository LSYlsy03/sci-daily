# -*- coding: utf-8 -*-
"""抓取各路 RSS 新闻源，输出近 3 天的条目到 data/raw_news.json"""
import json
import os
import time
import html
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser  # pip install feedparser

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

# 新闻源配置：可随时增删
SOURCES = [
    # 官方/权威
    {"name": "科普中国-科普要闻", "url": "https://www.kepu.gov.cn/rss/kepuzaixian.xml"},
    {"name": "人民网-科技", "url": "http://www.people.com.cn/rss/IT.xml"},
    {"name": "科技日报", "url": "https://www.stdaily.com/rss/kjrb.xml"},
    # 科普类
    {"name": "果壳网", "url": "https://www.guokr.com/rss/"},
    # 国际源
    {"name": "NASA News", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss"},
    {"name": "ScienceDaily-Top Science", "url": "https://www.sciencedaily.com/rss/top/science.xml"},
    {"name": "ScienceDaily-Technology", "url": "https://www.sciencedaily.com/rss/matter_energy/technology.xml"},
]

DAYS = 3


def clean(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def entry_date(entry):
    for key in ("published_parsed", "updated_parsed"):
        if getattr(entry, key, None):
            return datetime(*time.struct_time(getattr(entry, key))[:6], tzinfo=timezone.utc)
    return None


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS)
    items, seen_links = [], set()

    # 读取已推送记录做去重
    pushed_path = DATA / "pushed_links.json"
    pushed = set()
    if pushed_path.exists():
        pushed = set(json.loads(pushed_path.read_text(encoding="utf-8")))

    for src in SOURCES:
        try:
            feed = feedparser.parse(src["url"])
            if feed.bozo and not feed.entries:
                print(f"[warn] 源解析失败: {src['name']}")
                continue
            for e in feed.entries:
                link = e.get("link", "")
                if not link or link in seen_links or link in pushed:
                    continue
                d = entry_date(e)
                if d and d < cutoff:
                    continue
                summary = clean(e.get("summary", ""))
                if len(summary) > 300:
                    summary = summary[:300] + "…"
                items.append({
                    "source": src["name"],
                    "title": clean(e.get("title", "")),
                    "link": link,
                    "summary": summary,
                    "date": d.strftime("%Y-%m-%d") if d else "",
                })
                seen_links.add(link)
            print(f"[ok] {src['name']}: 累计 {len(items)} 条")
        except Exception as ex:
            print(f"[error] {src['name']}: {ex}")

    out = DATA / "raw_news.json"
    out.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"共抓取 {len(items)} 条 → {out}")


if __name__ == "__main__":
    main()
