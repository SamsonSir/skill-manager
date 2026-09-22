# 运行与交接协议（Pro审查修复）

`SKILL_ROOT` 是实际读取的 SKILL.md 的真实目录；`PROJECT_ROOT` 是当前账号项目；`ROLE_ROOT` 是当前角色专属资产目录。以下命令始终使用绝对路径，不受 cwd 影响。规范文件中的 scripts/ 相对 SKILL_ROOT；references 内文档引用相对所在文档。旧的重复 references/ 前缀不使用。

## 就绪与审核
- 写作就绪：已绑定账号、角色合同、事实策略与认可语气材料；新账号无近期稿件属于合法空历史，明确登记“不适用：新账号”，不能伪造已阅读历史。
- 人物生图就绪：运行 `python3 SKILL_ROOT/scripts/check_identity.py --manifest 身份清单 --account-id 当前账号 --character-id 当前角色 --account-root ROLE_ROOT` 并查看实际参考。以角色专属目录限制素材，不能传包含其他角色的工作区根目录。
- 正文审核：两份审核均含最终正文 article_sha256；style 的 reference_sha256 按 contract_ref 和 anchors_read 原始路径字符串记录文件哈希。执行 `validate_article_packet.py` 时必须同时传 --account-id、--character-id、--contract（账号配置指定的真实合同）；旧结构检查不作为生产就绪证据。来源文件路径相对账本所在目录；外部来源附本地取证文件。哈希不能证明语义真实。
- 保存就绪：账号专用映射及实际后台身份一致、完整图片、固定排版和最终稿验收通过。未知别名不能回退通用账号。浏览器保存前必须取得当前后台稳定账号标识与预期匹配的证据，显示名称或 profile 路径本身不足以证明身份。

## 持久化草稿门禁
每篇/每条独立 content_id 与状态文件，用 `scripts/content_state.py init` 登记批准正文和账号角色。所有命令携带 --state、--account-id、--character-id、--content-id。不保存时 init 加 --no-save；只写正文不调用生图、排版或后台工具。
任何可能创建草稿的调用之前执行 begin；它原子持久化 attempt_id 和 unknown 状态。失败则禁止调用后台。返回明确草稿ID后 saved，回读证据完整后 verified。命令结果内部保存，不发给用户。超时、崩溃、响应未知均保持 unknown，新会话先对账，不自动重复新建；只有本次请求明确未创建的证据才可 failed 后重试。状态文件锁只保护本机共享文件系统，不声称跨云端分布式锁；不同设备须交接完整稿件目录并明确独占保存责任，不能并发双写。
生图、排版、资产摘要按内容ID登记在同一稿件目录，正文变化必须重新审核；状态不明不可凭同标题去重。脚本验证的是证据字段和状态转换，真实回读仍需工具实际取得。

## 固定排版与贴图
浏览器文章和贴图脚本新增必传 `--expected-account-id`，值为配置中事先核实的公众号原始ID（不是显示名称）。当前读取 `window.wx.data.user_name`，取不到则停止；此页面字段已在素琴后台实测读到，其他账号仍须实际核验，不能临时把刚读取的未知值直接当预期值来绕过比较。
保存只消费独立的纯正文 `article.html`，不传带工具栏的 `preview.html`，不重新传 Markdown 套主题。统一复制区 id=article；发布用纯正文可包在 id=output 中供现有保存器提取。图片上传前后保存有序清单与哈希，按所选保存器实际图片约定适配，最终核对文字、样式和图序。
照片贴图保存独立标题、短正文、有序选定图片列表（每项path、sha256）、封面来源及来源文章ID/版本（如转换）。逐个显式传图，不扫描混有废片的素材目录，不按文件名字典序替代清单顺序。超出保存工具长度约束时明确退回调整，不能静默截字；转换不得修改源文章。保存器须写入新版可见标题框和短正文编辑器，并以远程图片URL确认上传完成；界面槽位数量、文件输入值或本地预览不能证明图片已经进入草稿。

## 视觉与依赖
生成计划保存读取的历史版本/哈希、日期或未知、活动ID、场景ID及版本、衣着、配饰、机位与理由。同批次串行选图并更新历史，避免并发丢记录；更新采用临时文件加原子替换。候选、已选、已发布分开，生成后并排验收实际人物和家具，记录资产哈希及结果。
写实生活照只使用支持图像参考的照片生成后端，事先核实能力。不得自动以 baoyu-cover-image 的设计插画规则代替生活照；原生 imagegen 缺失时验证替代后端能力，否则记录待补图。不生图模式生成调用必须为零。运行依赖按 SKILL_ROOT/requirements.txt 安装；图片解码校验依赖 Pillow；缺依赖明确报错，不回退只读文件头。

## 可执行入口与证据边界
- 分阶段配置检查：`python3 SKILL_ROOT/scripts/check_account_readiness.py --config 账号运行配置.json --account-id ACCOUNT --character-id ROLE`。配置字段为 account_id、character_id、project_root（相对配置文件）、contract、voice_anchor、layout_template、role_root、identity（后五项相对项目）、image_backend（reference_images/photorealistic 能力声明）、backend（method、original_id 或 app_id、binding_evidence）。结果只表示配置完整度；缺少人物图不会否决可写作，配置通过不等于登录可用。
- 保存器初始化先读 EXTEND.md。参数可从用户已确认账号配置取得，不重新要求用户选主题；固定 HTML 不套默认主题。浏览器 CLI 必传 --expected-account-id；API CLI 必传 --expected-app-id。两者含义不同，不能互换。
- `content_state.py init` 对每份封面、正文图片和最终 HTML 重复传 `--artifact PATH`。saved 回执必须含 account_id、character_id、content_id、attempt_id、draft_id、article_sha256；空文件、空对象不能证明保存。
- 保存后重新打开同一 `draft_id`。文章核对标题、正文HTML、固定排版、摘要、正文图片和封面；贴图核对可见标题、短正文、远程图片数量与顺序、封面和规格提示。只有这些检查全部通过，`content_state.py verified` 才可写入。
- 视觉记录：`visual_history.py --history 历史.json --entry 本次条目.json --expected-revision N`。读取历史再计划，提交时版本不符须重新评估，不能覆盖别人的更新。日期未知用 null；candidate 不等于 selected，更不等于 published。旧 Markdown 历史先核对再迁移，不生成虚假旧记录。
- 当前保存技能原生能力是 API、Chrome/CDP。已在 Ego 登录不等于该技能有连接；未经明确适配并验收，不能用 Ego 手动替代保存后称技能全流程通过。不能因为连接失败自动启动另一个浏览器。只测保存函数、人工填表或故障替身，必须按其真实范围报告。
