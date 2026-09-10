# 本机数据与增量规则

## 固定位置

- 账号根目录：`/Users/joker/Documents/微信聊天记录/qq179369161`
- 可读数据库：根目录下 `聊天记录.sqlite`，标准SQLite；只读连接：`sqlite3.connect(Path(db).as_uri()+'?mode=ro', uri=True)`，再执行 `PRAGMA query_only=ON`。
- 已有查询器：根目录下 `读取聊天记录.py`。仅依赖Python标准库。`--stats`读取旧验证报告，不可用于判断当前新鲜度。
- 多多：`57947720564@chatroom`
- 夙愿：`50351187410@chatroom`
- 报告根：`学习整理/Joker/<运行时间>/<多多或夙愿>/`，每次新目录，禁止覆盖旧报告。
- 运行状态：`学习整理/Joker/state.json`。权限目录0700、文件0600；不写进正式知识库或技能目录。

技能内固定的是此用户明确指定的数据位置和两个群；不要搜索其他账号、扩展到所有聊天或读取密钥。

## 每次先查实际数据

参数化SQL，逐群查询：

```sql
SELECT COUNT(*) AS records, MIN(create_time) AS first_time,
       MAX(create_time) AS last_time
FROM messages WHERE chat_username = ?;
```

`create_time`是Unix秒，使用`zoneinfo.ZoneInfo('Asia/Shanghai')`转换，不依赖宿主默认时区。最大消息时间只是快照中的最新记录，不证明实时同步或中间日期完整。与当前时间相差超过24小时明确提示快照滞后；即使不足24小时也不称已全量同步。

## 读取消息

直接SQL适合精确范围与完整定位：

```sql
SELECT source_db, source_table, local_id, server_id,
       chat_username, chat_name, sender_username, sender_name,
       create_time, sort_seq, local_type, decoded_content
FROM messages
WHERE chat_username = ? AND create_time >= ? AND create_time < ?
ORDER BY create_time, sort_seq, source_db, source_table, local_id;
```

或使用已有查询器，群参数必须传固定ID：

```bash
python3 '/Users/joker/Documents/微信聊天记录/qq179369161/读取聊天记录.py' --chat '57947720564@chatroom' --from-date YYYY-MM-DD --to-date YYYY-MM-DD --limit 0 --json
```

查询器日期端点含当日，内部转为次日零点前；默认只返回20条，完整提取必须显式`--limit 0`。全量结果保存到本机本次工作目录后分块阅读，不在工具结果里一次输出全部XML。

常见类型：1文字，3图片，34语音，43视频，47表情，10000系统；高位组合类型包含回复/链接/文件。`decoded_content`可能以`发送者:\n`开头，再跟XML。XML提取title/des/url时避免匹配嵌套refermsg中同名标签；`<des/>`不能误读成后续长XML。无法可靠解析就保留来源定位并标为未展开。不能把被引用文本重复计成一次新发言或独立证据。

图片、音视频、合集与文件本体尚未全部读取。2026-09-06用户已授权去重并将部分重复附件移入废纸篓，因此一些原附件路径可能失效；本技能不恢复或删除这些文件。原文字数据库未由去重流程修改。

## 增量进度

state.json仅保存工作流元数据：版本、群ID、模式、最近成功时间、报告路径和已处理消息定位清单路径，不保存敏感聊天正文。

每群分别维护`general`与`monetization`两个模式；周报及用户指定历史范围是显式范围运行，不推进默认增量游标。首次默认范围是当前日及前两天，不偷偷改成“快照最后三天”。当前范围无数据时报告实际截止时间；可提供已有历史笔记链接，不伪造今日报告。

增量不能只用`create_time > 上次最大时间`：会漏同秒消息和后来补入的历史记录。保存每次成功报告覆盖的稳定消息身份集合：有非零server_id时用`(群ID,server_id)`，否则用`(source_db,source_table,local_id,create_time)`。下次在首次起点之后扫描该群消息身份，差集为新增；跨时间点补入的消息也纳入，标明是补入旧记录。首次起点之前的历史只有用户请求才扩大读取。

已整理身份只在相应报告及长图都完成并验证后追加；失败或无新增不修改已处理集合。用临时文件写好后`os.replace`原子更新；操作前重新读当前state，若另一调用已改变状态，合并已完成身份与报告元数据，避免覆盖。现有旧笔记不是此固定报告流程的成功回执，不自动据此推进状态。

首次和断点恢复的输出状态应明确：完成、部分完成、无新增、数据不可用。技能首次安装验证不能伪造成功报告、创建已处理游标或消耗历史记录。
