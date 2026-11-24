#!/usr/bin/env python3
"""抓 Google 新聞 RSS，把新的新聞累積到 docs/news.json（只用 Python 內建套件）。"""
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

KEYWORDS = ["台北世聯商旅", "世聯商旅", "台北梅樓驛站", "府中棧精品商旅", "府中棧商旅"]
MAX_PER_RUN = 20  # 每次只取「最新 N 則」
OUT = Path(__file__).resolve().parent.parent / "docs" / "news.json"
TZ = timezone(timedelta(hours=8))  # 台北時間


def fetch_rss(keyword):
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote('"' + keyword + '"')
           + "&hl=zh-TW&gl=TW&ceid=TW:zh-Hant")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hotel-news-tracker)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_rss(text):
    items = []
    for it in ET.fromstring(text).iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = it.findtext("pubDate")
        if not (title and pub):
            continue
        try:
            dt = parsedate_to_datetime(pub).astimezone(TZ)
        except (TypeError, ValueError):
            continue
        items.append({"title": title, "link": link, "dt": dt})
    return items


def main():
    data = {"updated": "", "news": []}
    if OUT.exists():
        data = json.loads(OUT.read_text(encoding="utf-8"))
    known = {n["link"] for n in data["news"]} | {n["title"] for n in data["news"]}
    next_id = max([n["id"] for n in data["news"]] + [0]) + 1

    merged, seen = [], set()
    for kw in KEYWORDS:
        try:
            for item in parse_rss(fetch_rss(kw)):
                key = item["link"] or item["title"]
                if key not in seen:
                    seen.add(key)
                    merged.append(item)
        except Exception as e:  # 單一關鍵字失敗不影響其他
            print(f"抓取失敗（{kw}）：{e}", file=sys.stderr)
        time.sleep(1)

    merged.sort(key=lambda x: x["dt"], reverse=True)
    fresh = [i for i in merged[:MAX_PER_RUN] if i["link"] not in known and i["title"] not in known]
    fresh.sort(key=lambda x: x["dt"])  # 舊的先編號

    for item in fresh:
        data["news"].append({
            "id": next_id,
            "ts": int(item["dt"].timestamp() * 1000),
            "time": item["dt"].strftime("%Y-%m-%d %H:%M"),
            "title": item["title"],
            "link": item["link"],
        })
        next_id += 1

    data["news"].sort(key=lambda n: n["ts"], reverse=True)
    data["updated"] = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"新增 {len(fresh)} 則，共 {len(data['news'])} 則。")


if __name__ == "__main__":
    main()
