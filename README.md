# collect-recall skill

A small agent skill for acquiring and revisiting X bookmarks, YouTube watch-later items, GitHub stars and Beeper chat archives.

聊天与收藏技能：采集 → 同根目录存档 → 搜索/合并 → 总结与回顾。Beeper 复用 msgvault，收藏复用浏览器和导出工具，不另造后台服务。

- Entry point: [SKILL.md](SKILL.md)
- Offline helpers: Python 3.9+, standard library only
- No bundled server or web app; live acquisition needs authorized platform access
- Beeper needs Beeper Desktop + msgvault; offline bookmark helpers need only Python
- Synthetic examples only; no personal exports or credentials
- MIT licensed

## Install

```sh
git clone https://github.com/RUNAWAYRUN/collect-recall.git ~/.agents/skills/collect-recall
```

Use your agent's skill directory if it differs. Reload its skill list if needed, then ask:

> 用 collect-recall 整理这些收藏导出，告诉我新增了什么，哪些值得先看。

Start with [acquisition and storage](references/acquisition.md): GitHub has a paginated exporter; X/YouTube use authorized browser/export workflows; Beeper uses existing msgvault commands. These workflows need their respective tools and access. Exact bookmark helper inputs: [input format](references/input-format.md).

## Try without an agent

```sh
bash scripts/demo.sh
python3 -m unittest discover -s tests -v
```

The offline demo uses a temporary directory: first round 5 new items, second 0, third 1. The scripts merge and compare lists; the agent reads and summarizes the content. This is not a full page/media archive.

真实收藏放在技能目录外。不要把私人导出提交到公共仓库。
