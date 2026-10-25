# 群聊对标发现

用户说「找群里分享的对标账号」「提取公众号名片」时，先扫指定会话的公开名片与文章卡片，不要求卡片本身包含主题关键词：

```bash
python3 /Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/benchmarks.py --chat-id '精确会话ID'
```

支持日期、`--db`、`--output`。仅读现有快照，不刷新、发消息、关注或推送。输出默认 `账号根/学习整理/Joker/对标发现/<运行时间>/cards.jsonl` 和 `summary.jsonl`；原子替换，相同输入重复运行内容不增加。

提取公众号名片（公开名称、简介、原始公开主页链接如有）、文章卡片（来源公众号、标题、原始文章链接、__biz如有；图片消息的数量、封面尺寸和公开封面URL）、引用与可解析转发合集中的这些记录。`context` 标记 direct/quoted/forwarded/embedded；结构证据通过 source 与 sent_at 定位。`account_id` 仅写有证据的 gh_ 标识；alias另列；v3_*@stranger、biznamecardinfo、反垃圾票据、媒体密钥与CDN地址不导出。没有公开链接就留null，不拼造公众号主页。原始文章URL保留定位参数。

脚本输出是「分享线索」，不是自动认定的对标名单。按同群相邻文字判断是直接对标、群友自有号、内容参考还是无关分享；一个账号名不能推断其图片、收入或全部历史内容。仅文字提名的账号用 search.py 搜索补证；不能自动把同名卡片合并。

已支持带裸&属性的名片。嵌套解析限制四层与每条2MB；未知结构或加密转发可能漏提，不能声称覆盖所有分享。纯图片截图中的名称尚不支持OCR；可读图片获取和截图OCR是独立缺口，不以名片简介替代原图视觉分析。

关键词搜索现已包含名片公开显示字段，matches.jsonl 增加 cards 字段。裸图片XML经发送者前缀清理后不再误输出。
