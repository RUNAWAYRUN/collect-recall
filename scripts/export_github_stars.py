#!/usr/bin/env python3
"""Export public GitHub stars. Python 3.9+; atomic output, no external packages."""
import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.request import Request, urlopen


def collect(user, fetch):
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})', user):
        raise ValueError('Invalid GitHub username')
    rows, seen = [], set()
    page = 1
    while True:
        batch = fetch(f'https://api.github.com/users/{user}/starred?per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Unexpected API response')
        if not batch:
            return rows
        added = 0
        for repo in batch:
            name = repo['full_name']
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            rows.append({'name': name, 'url': repo['html_url'],
                         'lang': repo.get('language'), 'stars': repo.get('stargazers_count'),
                         'label': repo.get('description') or ''})
            added += 1
        if not added:
            raise ValueError('Pagination stopped making progress; old output preserved')
        page += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'collect-recall',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token

    def fetch(url):
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            return json.load(response)

    try:
        rows = collect(args.user, fetch)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=args.out.parent, delete=False) as handle:
                name = handle.name
                json.dump(rows, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
            os.replace(name, args.out)
        finally:
            if name and os.path.exists(name):
                os.unlink(name)
        print(f'Exported {len(rows)} public stars to {args.out}')
    except Exception:
        # Do not echo request/credential details from network exceptions.
        parser.exit(1, 'Export failed (network, rate limit, or invalid response); old output preserved.\n')


if __name__ == '__main__':
    main()
