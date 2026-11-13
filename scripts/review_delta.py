#!/usr/bin/env python3
"""跟上一次快照比对，只输出新增/消失。"""
import argparse, json, os, tempfile
from keys import normalize
from datetime import datetime

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    a = ap.parse_args()
    inv = json.load(open(os.path.join(a.dir, "inventory.json"), encoding="utf-8"))
    if not isinstance(inv, dict) or not isinstance(inv.get("items"), list):
        raise SystemExit("inventory.json 结构不合法（需要 items 数组）")
    cur = inv["items"]
    snap = os.path.join(a.dir, ".last_snapshot.json")
    prev = set(json.load(open(snap, encoding="utf-8"))) if os.path.exists(snap) else set()
    key = lambda i: normalize(i["url"])
    now = {key(i) for i in cur}
    new = [i for i in cur if key(i) not in prev]
    gone = sorted(prev - now)
    fd, tmp = tempfile.mkstemp(dir=a.dir, prefix=".snapshot.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(sorted(now), f)
    os.replace(tmp, snap)   # 原子替换
    print(f"新增 {len(new)} / 本次未观测 {len(gone)}（总计 {len(cur)}；未观测不等于取消收藏，可能只是本次采集范围波动）")
    for i in new[:10]:
        print(f"  + [{i['platform']}] {i['title'][:60]}")
    for u in gone[:10]:
        print(f"  - {u}")

if __name__ == "__main__":
    main()
