# 飞书学习库（个人 Wiki）

私人学习目录，和本机 HTML 报告分开：HTML 是完整证据与检索；飞书写「能练习的方法 + 群主栏目日报」。默认不发布、不拉人、不发群消息。

## 何时写入飞书

用户说到下面任一说法时，在本机整理之后写入飞书（没有新可读消息则只说明截止时间，不编空日报）：

- 更新学习库 / 补飞书日报 / 整理到飞书 / 飞书知识库
- 补多多日报 / 补夙愿日报 / 把群报写进飞书
- 整理多多到飞书 / 整理夙愿到飞书

只说「整理微信群」「整理多多」「整理夙愿」且没提飞书时，仍以本机 HTML + 长图为主，不默认改 Wiki。

身份一律 `lark-cli ... --as user`。读写走 lark-wiki / lark-doc / lark-drive，不另写飞书客户端。

## 空间与群目录

- 空间名：Joker AI学习知识库
- `space_id`：`7684186386408197367`
- 一个微信群 = 空间根下一棵一级目录，不要把两群写进同一棵树
- 多多：`57947720564@chatroom` → 目录「多多的AI视频交流群」`Wl6mwEiP8i9NRUkpMzXcTnfhnSg`
- 夙愿：`50351187410@chatroom` → 目录「夙愿的AI实验室2026」`HSlcw6cyQi8qQGk026gcq21DnSe`
- 新群先 `wiki +node-create --space-id 7684186386408197367 --title '<群名>'`，再在该节点下建子页

子页顺序（创建时按此顺序，乱了用 `wiki +move` 把节点依次移回同一父节点，后移的排在后面）：

1. 索引
2. 01 … 07（方法站，标题以序号开头）
3. 资源 · 提示词
4. 资源 · 工具与平台
5. 资源 · 文档与教程
6. 群日报（可多篇；最新一篇标题用日期）

首页就是该群一级节点本身，插入 `<sub-page-list></sub-page-list>`。学习地图有本地 PNG 时用 `docs +media-insert --doc <obj_token> --file`（相对 cwd，不要把 wiki URL 当 doc）。

## 日报写法

日报由技能脚本按固定九块生成，不要让 Agent 另起栏目或改标题格式：

```bash
python3 "/Users/joker/.skills-manager/skills/joker-wechat-get-message/scripts/daily.py" build \
  --name 多多 --from-date YYYY-MM-DD --to-date YYYY-MM-DD --publish --json
```

九块顺序写死在 `scripts/daily.py` 的 `BLOCKS`：一句话总览、群聊数据、发言排行、热议话题、重点讨论、关键进展、思考摘录、重点工具/资源、关键词。重点讨论每项写「发生了什么 / 群友可参考 / 参与：人名」。统计、排行、链接、时段簇从 sqlite 算出；Agent 只负责跑脚本和核对发布结果。

- 标题：`YYYY-MM-DD-<群名>-<当日主题>`，例如 `2026-09-06-多多的AI视频交流群-参考图分工、MV音频拆分与产品视频询价`
- 改标题：`lark-cli drive +update-title --url 'https://my.feishu.cn/wiki/<node_token>' --title '...' --as user`（wiki 节点与底层文档标题会一起改）
- 人名用 contacts 的备注，没有备注用昵称；禁止 `成员01`、wxid、乱码占位
- 飞书正文不要写 `来源：#1234` 或括号消息编号；本机 `来源索引.md` 才保留定位
- 变现必须区分询价、供给、成交、回款；没有证据就写没有
- 图片、视频附件未展开就标明未展开，不脑补
- 不要整段搬需要转发许可的千字作品提示词；方法骨架可以留在资源页

覆盖已有日报用 `docs +update --command overwrite`；日报通常无图。首页有地图时不要 overwrite 掉图片，改用 `str_replace` 或局部 block。

## 新鲜度

先跑 `watchlist.py status`，再查该群 `MAX(create_time)`。快照最大时间早于用户要的日期时，先按 [refresh.md](refresh.md) 刷新；刷新失败再写明缺失区间和已有页面链接，**禁止**用空白或想象补那几天。微信进程在跑、加密库文件更新，不等于可读 `聊天记录.sqlite` 已更新。不要把活库当已解密快照。

同一天已有同标题日报且事实没有新消息，不要重写凑进度。

## 验收

- 侧栏顺序是 索引 → 01–07 → 资源三页 → 日报
- 抽查日报与首页：没有 `成员\d+`、没有 `来源：#`
- 标题含日期、群名、主题
- 给用户可点的 wiki 链接，并写清实际覆盖的北京时间
