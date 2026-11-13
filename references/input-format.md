# 输入格式与脚本行为

这是本技能约定的输入，不保证兼容平台原始导出。所有文件为 UTF-8 JSON。示例见 `../scripts/sample/`。

```json
{"bookmarks":[{"url":"https://x.com/example/status/1234567890","text":"Example bookmark"}]}
```

```json
{"watchLater":[{"url":"https://www.youtube.com/watch?v=EXAMPLE0001","title":"Example video","info":"Optional note"}]}
```

```json
[{"name":"example/tool","url":"https://github.com/example/tool","lang":"Python","stars":42,"label":"Optional note"}]
```

每项必须有 http/https `url`，其余字段可选。三个源路径必须显式提供；确定没有使用某个平台时用 `{"bookmarks":[]}`、`{"watchLater":[]}`、`[]`，不要用空输入替代采集失败。

`merge_inventory.py` 输出 `inventory.json`，含 UTC `generatedAt` 与各项 `firstSeen`。按归一化URL去重，首次出现的元数据优先（X→YouTube→GitHub）。不生成网页、Markdown报告或内容摘要。

`review_delta.py` 比较上次快照 `.last_snapshot.json`，打印新增/本次未观测数量，各最多展示10项，并保存新的基线。它不访问链接，不识别编辑、死链或真正的取消收藏。

首见时间在前一份inventory仍有该项时保留；消失后再出现会重新计时。缺文件、JSON解析错误会停止而不覆盖旧inventory。单个JSON使用原子替换，不支持并发写入或跨文件事务。

URL标识：YouTube watch与短链接按视频ID；X/Twitter按status ID；GitHub仓库按owner/repo。通用URL去已知广告跟踪参数，保留业务参数和片段；不是内容相似度去重，也不保证识别所有URL变体。

真实数据放在技能目录之外。脚本不联网、不读凭据、不含遥测；不要把私人清单跟随技能提交到GitHub。
