# -*- coding: utf-8 -*-
"""调用智谱 GLM 对当天新闻进行筛选、解读、知识点关联、分级，输出 data/daily_YYYY-MM-DD.json"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"

ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "")
MODEL = os.environ.get("GLM_MODEL", "glm-4-flash")  # 免费模型
COUNT = int(os.environ.get("NEWS_COUNT", "5"))

PROMPT = """你是一名厦门实验小学的小学科学老师助手，服务对象是四到六年级的科学课堂。
下面是今天抓到的新闻列表（JSON 数组，含 source/title/link/summary）。

请挑选出最适合作为课堂拓展讲解的 {count} 条科技/科学前沿新闻，并为每条写出结构化内容。
挑选标准：小学生能听懂、有趣、和科学课内容相关。非常好用的排前面。

输出严格的 JSON 数组（不要任何其他文字），每个元素字段：
- "title": 通俗有趣的标题（适合讲给小学生）
- "source": 原新闻 source
- "link": 原文链接（必须原样照抄输入的 link，一个字都不能改）
- "summary": 一句话摘要，讲给小学生听的版本，50字以内
- "interpretation": 解读：这件事是什么、为什么重要，120字以内，通俗
- "knowledge": 对应的小学科学教材知识点，格式如"六上《工具与技术》/ 四下《电路》"，可写1-2个，需确实相关
- "grade": 好用程度，1-5 的整数，5 表示课堂拓展极好用
- "grade_reason": 一句话说明为什么这个等级

新闻列表：
{news}
"""


def main():
    raw_path = DATA / "raw_news.json"
    items = json.loads(raw_path.read_text(encoding="utf-8"))
    if not items:
        print("今日无新闻可筛选")
        (DATA / "empty.flag").write_text("1", encoding="utf-8")
        return

    # 控制输入长度，取摘要较完整的前 60 条
    news_str = json.dumps(items[:60], ensure_ascii=False)
    prompt = PROMPT.format(count=COUNT, news=news_str)

    resp = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        headers={"Authorization": f"Bearer {ZHIPU_KEY}",
                 "Content-Type": "application/json"},
        json={"model": MODEL,
              "messages": [{"role": "user", "content": prompt}],
              "temperature": 0.3},
        timeout=180,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # 提取 JSON（容忍 ```json 包裹）
    m = re.search(r"\[.*\]", content, re.S)
    if not m:
        raise RuntimeError(f"AI 未返回合法 JSON: {content[:500]}")
    curated = json.loads(m.group(0))

    # 防杜撰：link 必须来自原始输入，否则丢弃
    valid_links = {it["link"] for it in items}
    link_fix = {it["title"]: it["link"] for it in items}
    fixed = []
    for c in curated:
        if c.get("link") not in valid_links:
            # 尝试按标题模糊匹配回正确的链接
            for t, l in link_fix.items():
                if t and (t in c.get("title", "") or c.get("title", "") in t):
                    c["link"] = l
                    break
            else:
                print(f"[drop] 链接对不上，疑似杜撰: {c.get('title')}")
                continue
        c["grade"] = max(1, min(5, int(c.get("grade", 3))))
        fixed.append(c)

    fixed.sort(key=lambda c: -c["grade"])
    today = datetime.now().strftime("%Y-%m-%d")
    out = DATA / f"daily_{today}.json"
    out.write_text(json.dumps({"date": today, "items": fixed}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"筛选出 {len(fixed)} 条 → {out}")


if __name__ == "__main__":
    main()
