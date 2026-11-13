"""把 URL 归一化成稳定 ID：同一条内容的不同跟踪参数视为同一项，不同内容不会撞车。"""
import re
from urllib.parse import urlsplit, parse_qs, urlencode

# 只剔除明确的广告跟踪参数；t/list/index/si/ref 等可能是业务参数，保留。
TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "utm_id", "utm_name", "fbclid", "gclid", "dclid", "msclkid", "igshid", "spm"}


def normalize(url: str) -> str:
    try:
        u = urlsplit(url.strip())
    except ValueError:
        return url
    host = (u.hostname or "").lower().removeprefix("www.")
    path = u.path.rstrip("/")
    q = parse_qs(u.query, keep_blank_values=True)

    if host in ("youtube.com", "m.youtube.com") and path == "/watch" and q.get("v"):
        return f"yt:{q['v'][0]}"
    if host == "youtu.be" and path:
        return f"yt:{path.lstrip('/')}"
    if host in ("x.com", "twitter.com"):
        m = re.search(r"/status/(\d+)", path)
        if m:
            return f"x:{m.group(1)}"
    if host == "github.com":
        parts = [p for p in path.split("/") if p]
        if len(parts) == 2:                       # 只有 owner/repo 才归并；子路径保持原样
            return f"gh:{parts[0].lower()}/{parts[1].lower()}"

    kept = {k: v for k, v in q.items() if k.lower() not in TRACKING}
    base = f"{host}{path}"
    if u.fragment:
        base += "#" + u.fragment
    return f"{base}?{urlencode(sorted(kept.items()), doseq=True)}" if kept else base
