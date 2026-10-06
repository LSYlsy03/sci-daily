# -*- coding: utf-8 -*-
"""把当天推送链接通过 PushPlus 发到微信，并记录已推送链接防止重复。"""
import json
import os
from datetime import datetime
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")
PUSH_URL = "http://www.pushplus.plus/send"
SITE_URL = os.environ.get("SITE_URL", "")  # 如 https://用户名.github.io/sci-daily


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    daily = DATA / f"daily_{today}.json"
    if not daily.exists():
        print("今天没有生成内容，跳过推送")
        return
    data = json.loads(daily.read_text(encoding="utf-8"))
    items = data["items"]
    if not items:
        return

    # 防重复：同一日期只推一次
    pushed_path = DATA / "pushed_dates.json"
    pushed_dates = json.loads(pushed_path.read_text(encoding="utf-8")) if pushed_path.exists() else []
    if today in pushed_dates:
        print(f"{today} 已推送过，跳过")
        return

    top = items[0]
    titles = "；".join(f"[{c['grade']}★]{c['title']}" for c in items)
    content = (f"{today} 共 {len(items)} 条<br>" + titles.replace("；", "<br>")
               + f'<br><br><a href="{SITE_URL}">点此查看完整解读</a>')

    if TOKEN and SITE_URL:
        r = requests.post(PUSH_URL, json={
            "token": TOKEN, "title": f"🧪今日科学拓展：{top['title'][:20]}",
            "content": content, "template": "html"}, timeout=30)
        print("PushPlus 返回:", r.text[:200])

    # 记录已推送
    pushed_dates.append(today)
    pushed_path.write_text(json.dumps(pushed_dates[-90:], ensure_ascii=False), encoding="utf-8")

    links_path = DATA / "pushed_links.json"
    links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else []
    links.extend(c["link"] for c in items)
    links_path.write_text(json.dumps(links[-500:], ensure_ascii=False), encoding="utf-8")
    print(f"已记录 {today} 推送，{len(items)} 条链接入库")


if __name__ == "__main__":
    main()
