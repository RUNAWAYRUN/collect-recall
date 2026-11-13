#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
demo_dir="$(mktemp -d "${TMPDIR:-/tmp}/collect-recall.XXXXXX")"
trap 'rm -rf "$demo_dir"' EXIT
printf 'Round 1: baseline (5 synthetic items)\n'
python3 merge_inventory.py --demo --out-dir "$demo_dir"
python3 review_delta.py --dir "$demo_dir"
printf '\nRound 2: unchanged\n'
python3 review_delta.py --dir "$demo_dir"
printf '\nRound 3: one new item\n'
python3 - "$demo_dir" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1]) / 'inventory.json'
data = json.loads(p.read_text())
data['items'].append({'platform': 'X', 'kind': '书签', 'title': 'New synthetic item',
                      'url': 'https://example.com/new', 'note': ''})
p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
PY
python3 review_delta.py --dir "$demo_dir"
