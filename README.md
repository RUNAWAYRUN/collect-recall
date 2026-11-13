# collect-recall skill

A small agent skill for turning exported X bookmarks, YouTube watch-later items and GitHub stars into a collection you actually revisit.

收藏整理与回顾技能：合并去重、记住首见时间、只看新增，再由 Agent 按你的目标整理重点。

- Entry point: [SKILL.md](SKILL.md)
- Offline helpers: Python 3.9+, standard library only
- No server, web app, platform login or AI API dependency
- Synthetic examples only; no personal exports or credentials
- MIT licensed

## Install

```sh
git clone https://github.com/RUNAWAYRUN/collect-recall.git ~/.agents/skills/collect-recall
```

Use your agent's skill directory if it differs. Reload its skill list if needed, then ask:

> 用 collect-recall 整理这些收藏导出，告诉我新增了什么，哪些值得先看。

The skill does not include platform exporters. Give your agent existing exports or authorized access through tools available in its environment. Exact helper inputs and limitations: [input format](references/input-format.md).

## Try without an agent

```sh
bash scripts/demo.sh
python3 -m unittest discover -s tests -v
```

The offline demo uses a temporary directory: first round 5 new items, second 0, third 1. The scripts merge and compare lists; the agent reads and summarizes the content. This is not a full page/media archive.

真实收藏放在技能目录外。不要把私人导出提交到公共仓库。
