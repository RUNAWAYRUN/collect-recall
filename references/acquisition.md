# 采集与存储

只获取用户已授权的数据。先检查已有目录、工具版本和登录状态；不要覆盖正在使用的聊天库，或复制本机凭据、定时任务进技能包。下列命令需按安装版本的 `--help` 核对；技能不负责自动安装第三方软件。

## 同一个资料根目录

沿用已有根目录；没有时可用 `~/personal-archive/`：

```text
personal-archive/
  chats/msgvault/       # msgvault 管理，勿直接改库
  collections/raw/     # 各平台原始导出、采集记录
  collections/current/ # x.json / youtube.json / stars.json
  collections/review/  # inventory.json / .last_snapshot.json
  reports/             # 按主题的聊天+收藏摘要
```

同根目录不是同一个数据库。先在 msgvault 搜索聊天，再在收藏清单筛链接，Agent 合并引用与摘要。每轮记录采集时间、来源、数量、分页/滚动停止原因及完整/部分/失败；保留旧的成功导出，失败不能写空数组代替。

## Beeper：首次与增量

先确认 Beeper Desktop 正在运行、本地 API 可用，运行 `msgvault --help`，检查已有 `--home` 和账号。已有存档就沿用它的 home；以下用新目录演示，只有确认需要新库时才使用。

```sh
msgvault --home ~/personal-archive/chats/msgvault add-beeper
msgvault --home ~/personal-archive/chats/msgvault list-accounts
msgvault --home ~/personal-archive/chats/msgvault sync-beeper
msgvault --home ~/personal-archive/chats/msgvault stats
msgvault --home ~/personal-archive/chats/msgvault search 'project' --limit 10 --json
```

`add-beeper` 交互输入 Beeper Desktop Settings → Developer 生成的本地 token；让用户在本机输入，不在聊天中索取。新增网络后可重跑以发现账号。选择部分账号前检查该版本 `sync-beeper --help` 的 `--account` 及配置范围。

第一次 `sync-beeper` 回填 **Beeper 本地可提供的历史**，后续重复该命令做可恢复增量。`--limit` 限制每聊天本轮数量，不等于完整采集；中断后重跑并核查同步状态。`--full` 是重取/upsert，不证明保留编辑/删除历史。云端已有而本地尚不可用的消息可能缺失。

附件默认尝试下载；`--no-media` 只取消息。补附件先看 `backfill-beeper-media --help` 再执行。附件元数据条数、下载成功文件数、失败数分开报告，不能把元数据叫做文件备份。正文、附件和编辑/删除历史分别说明覆盖情况。

用已知存在的短中文和英文各验证一次搜索；英文成功不证明中文可搜。失败时说明限制，可复用用户已有中文索引，未实际建立则不声称支持。摘要引用消息ID/时间/来源，只导出完成当前任务需要的记录，不公开聊天内容。

持续采集必须另行确认用户要自动更新；复用现有调度器，验证实际运行和失败日志。一次同步成功不等于后台归档已运行。

## GitHub stars：公开 API 分页

```sh
python3 <skill>/scripts/export_github_stars.py --user octocat \
  --out ~/personal-archive/collections/current/stars.json
```

脚本只访问 api.github.com 的公开 stars API，每页100条，直到空页。可选从现有 `GITHUB_TOKEN` 环境变量读取授权；不要把 token 写到命令行或文件。网络错误/限流会失败并保留旧文件；成功只代表 API 访问到的公开 stars，非完整 GitHub 数据备份。收藏时间不在此导出中。

来源：[GitHub starred repositories API](https://docs.github.com/en/rest/activity/starring#list-repositories-starred-by-a-user)。

## X bookmarks / YouTube 稍后看

优先已有导出，确认导出工具确实包含书签/目标播放列表。用浏览器采集时使用已授权登录会话：X `https://x.com/i/bookmarks`；YouTube `https://www.youtube.com/playlist?list=WL`。登录失效或权限不足就停下该源，不自动绕过权限。

动态列表会虚拟化，**边滚动边累计** status ID / video ID 与标题、原文链接；只在最后一次 DOM 抓取会丢掉已卸载条目。可按每批提取→去重→滚动→等待加载循环。页面结构变化时重新观察元素，不盲用固定选择器。重试有界，遇到限流、登录或连续多轮无新增即停止并记录原因。

滚动无新增仅证明本轮停止，不能保证完整；与页面显示总数/旧导出对账。不可见或已删除视频单独计缺口，不能编造链接。原始结果保存在 raw，再转换为 [输入格式](input-format.md)。例如：

```json
{"bookmarks":[{"url":"https://x.com/example/status/1234567890","text":"标题或可见摘录"}]}
```

```json
{"watchLater":[{"url":"https://www.youtube.com/watch?v=EXAMPLE0001","title":"标题"}]}
```

这是采集操作指引，不是随附的 X/YouTube 自动采集器。无浏览器或授权导出时，报告该源未采集；不要用样例冒充用户数据。列表通常只有元数据，全文/视频/附件存档需另选受支持工具并验证。
