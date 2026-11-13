#!/usr/bin/env python3
"""合并多来源收藏导出 -> inventory.json（含 firstSeen）。"""
import argparse, json, os, sys, tempfile
from keys import normalize
from datetime import datetime, timezone

def load(p):
    """fail closed：缺文件或解析失败直接报错，绝不返回空结构覆盖旧数据。"""
    if not os.path.exists(p):
        sys.exit(f"输入不存在: {p}（真实运行请显式传 --x/--yt/--stars；演示用 --demo）")
    try:
        return json.load(open(p, encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"输入解析失败: {p}: {e}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x"); ap.add_argument("--yt"); ap.add_argument("--stars")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--demo", action="store_true", help="使用 sample/ 下的合成样本")
    a = ap.parse_args()
    if a.demo:
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample")
        a.x = a.x or os.path.join(base, "x-export.json")
        a.yt = a.yt or os.path.join(base, "yt-export.json")
        a.stars = a.stars or os.path.join(base, "stars.json")
    if not (a.x and a.yt and a.stars):
        sys.exit("必须显式给 --x --yt --stars（或用 --demo 跑合成样本）")
    os.makedirs(a.out_dir, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    items = []
    x = load(a.x)
    if not isinstance(x, dict) or not isinstance(x.get("bookmarks"), list):
        sys.exit(f"X 导出结构不合法（需要 bookmarks 数组）: {a.x}")
    for b in x["bookmarks"]:
        items.append({"platform": "X", "kind": "书签", "title": (b.get("text") or "")[:160],
                      "url": b["url"], "note": ""})
    y = load(a.yt)
    if not isinstance(y, dict) or not isinstance(y.get("watchLater"), list):
        sys.exit(f"YouTube 导出结构不合法（需要 watchLater 数组）: {a.yt}")
    for v in y["watchLater"]:
        items.append({"platform": "YouTube", "kind": "稍后观看", "title": v.get("title", ""),
                      "url": v.get("url", ""), "note": v.get("info", "")[:80]})
    stars = load(a.stars)
    if not isinstance(stars, list):
        sys.exit(f"stars 输入结构不合法（需要数组）: {a.stars}")
    for r in stars:
        items.append({"platform": "GitHub", "kind": "星标", "title": r.get("name", ""),
                      "url": r.get("url", ""),
                      "note": f"{r.get('label','')} ★{r.get('stars',0)} {r.get('lang','')}"})
    prev_path = os.path.join(a.out_dir, "inventory.json")
    prev = {}
    if os.path.exists(prev_path):
        old = load(prev_path)
        if not isinstance(old, dict) or not isinstance(old.get("items"), list):
            sys.exit(f"已有清单结构不合法，拒绝覆盖: {prev_path}")
        prev = {normalize(i["url"]): i.get("firstSeen") for i in old["items"] if i.get("firstSeen")}
    unique = {}
    for it in items:
        url = it.get("url")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            sys.exit("每条收藏都需要有效的 http/https URL；旧清单未被覆盖")
        key = normalize(url)
        if key not in unique:
            it["firstSeen"] = prev.get(key, now)
            unique[key] = it
    items = list(unique.values())
    fd, tmp = tempfile.mkstemp(dir=a.out_dir, prefix=".inventory.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"generatedAt": now, "items": items}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, prev_path)   # 原子替换：失败不会留下半个文件
    print(f"{len(items)} 条 -> {prev_path}")

if __name__ == "__main__":
    main()
