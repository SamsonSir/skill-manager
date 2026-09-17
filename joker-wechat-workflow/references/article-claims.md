# 正文事实账本

每篇最终正文对应一个 `正文事实账本.json`。账本是发布门禁证据，不是文章正文的一部分。

```json
{
  "schema_version": 1,
  "account_id": "账号ID",
  "character_id": "角色ID",
  "article": "正文文件名",
  "fact_policy": "source_bound",
  "claims": [
    {
      "line_start": 3,
      "line_end": 3,
      "claim": "正文表达的具体主张",
      "type": "experience",
      "source_type": "user_material",
      "source_ref": "项目内相对路径#可定位段落",
      "public_framing": "real"
    }
  ],
  "semantic_review": {
    "reviewed_from_final_article": true,
    "reviewer": "Agent名称",
    "result": "pass"
  }
}
```

`type` 仅可为：

- `opinion`：人物观点、偏好或当下判断，不声称发生过具体事件。
- `general_observation`：不指向人物亲历的普遍观察。
- `experience`：人物做过、看过、拥有、遇到或记得的具体事情与习惯。
- `biography`：年龄、地域、职业、教育、婚姻、家庭、居住、健康、经济等履历。
- `dialogue`：声称真实发生的对话或他人原话。
- `quote`：书籍、文章、公开资料等可核引语或具体外部事实。

`source_type` 可使用 `user_material`、`project_fact`、`authorized_interview`、`published_source`、`explicit_fiction`、`none`。`experience`、`biography`、`dialogue`、`quote` 在 `source_bound` 模式下必须提供非空 `source_ref`，且不得使用 `none` 或 `explicit_fiction`。

逐段检查正文。含“我／我的／我们”、过去时间词、具体物件、动作、数量、对话或习惯的段落通常需要登记；同一段多个独立主张分别登记。校验脚本只提供最低限度的结构与覆盖检查，语义审稿仍必须执行。

## 角色风格验收

另存 `角色风格验收.json`：

```json
{
  "schema_version": 1,
  "account_id": "账号ID",
  "character_id": "角色ID",
  "article": "正文文件名",
  "contract_ref": "账号配置中角色合同的路径",
  "anchors_read": ["实际读取的认可样文路径"],
  "reviewed_from_final_article": true,
  "dimensions": {
    "stance": {"result": "pass", "article_evidence": "正文原句或段落定位", "anchor_basis": "合同或锚点依据"},
    "speaking_position": {"result": "pass", "article_evidence": "...", "anchor_basis": "..."},
    "concreteness": {"result": "pass", "article_evidence": "...", "anchor_basis": "..."},
    "rhythm": {"result": "pass", "article_evidence": "...", "anchor_basis": "..."},
    "ending": {"result": "pass", "article_evidence": "...", "anchor_basis": "..."},
    "recent_structure": {"result": "pass", "article_evidence": "与近期稿件的具体异同", "anchor_basis": "实际对照的近期稿件路径"}
  },
  "overall": "pass",
  "deviations": []
}
```

六个维度必须全部有正文证据和依据。角色一致指人物的价值立场和说话方式稳定，不要求每篇复制相同句式、情绪或结构。若某一维度无法判断、近期稿件未实际读取、或正文只能靠模仿锚点措辞显得相似，该项写 `fail`。
