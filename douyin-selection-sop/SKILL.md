---
name: douyin-selection-sop
description: 抖音电商选品全流程SOP。当用户要求执行抖店/抖音电商选品、罗盘短视频榜采集、爆品潜质分析、带货视频提取下载、飞书选品清单写入时触发。覆盖 Phase 1-6：罗盘采集→爆品预筛→素材提取→极简报告→飞书入库→上架准备。
---

# 抖音电商选品 SOP

> 版本：V4.3（通用运行契约版，对齐当前批量生产链路）
> 触发：用户说「选品」「抖店选品」「罗盘采集」「爆品分析」等

## 通用化目标

本 skill 必须在任意支持本地 shell、Chrome CDP 与 skill 文件读取的智能体里跑通主链路。不要依赖“当前智能体知道项目目录/脚本位置/飞书字段/浏览器状态”这类隐性上下文。

主链路定义为：

`环境探测 -> 罗盘榜单采集 -> 爆品预筛 -> 素材提取/下载 -> 剪辑成 9:16 投流素材 -> 飞书入库/通知 -> 输出可交给上架或千川的产物`

如果某个外部依赖缺失，先明确指出缺失项与恢复动作；不要把缺依赖解释成业务失败。

## 通用运行契约

### 入口自定位

执行脚本时优先从 skill 自身目录启动，不依赖 vault 项目目录：

```bash
cd ~/.agents/skills/douyin-selection-sop
bash ./scripts/run_selection_to_clip.sh --query "给 <店铺名> 跑3个候选" --cdp-port 9222
```

批量队列入口：

```bash
cd ~/.agents/skills/douyin-selection-sop
bash ./scripts/run_batch_selection.sh \
  --queue-file ./scripts/templates/batch_tasks.example.jsonl \
  --cdp-port 9222 \
  --download
```

不要要求用户进入 `20_项目/抖音电商选品流程跑通` 才能执行。项目目录只允许作为兼容 wrapper 或输出归档位置。

### 可配置项

外部智能体如果不在当前机器或当前账号下执行，必须先检查并按需覆盖这些环境变量：

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `AGENTS_SKILL_ROOT` | `$HOME/.agents/skills` | 其他 skill 的根目录 |
| `DOUYIN_SELECTION_PROJECT_DIR` | `$HOME/Documents/JokerSu-knowledge/20_项目/抖音电商选品流程跑通` | 兼容输出/项目根目录 |
| `DOUYIN_SELECTION_CLIP_SCRIPT` | `$AGENTS_SKILL_ROOT/video-auto-clip/scripts/batch_clip_nl.sh` | 批量剪辑脚本 |
| `DOUYIN_SELECTION_MATERIAL_OCR_BIN` | `$AGENTS_SKILL_ROOT/video-auto-clip/tools/vision_ocr.swift` | 素材轻量 OCR/探测工具 |
| `DOUYIN_SELECTION_FEISHU_BASE_TOKEN` | 当前默认选品 Base | 飞书选品清单 Base |
| `DOUYIN_SELECTION_FEISHU_TABLE_ID` | 当前默认选品表 | 飞书选品清单 Table |
| `LARK_CLI_CONFIG` | `$HOME/.lark-cli/config.json` | 飞书 CLI 配置 |

通用智能体执行前不要改脚本常量；需要迁移账号、Base、项目目录时，用环境变量覆盖。

### 运行前探测清单

1. `command -v agent-browser jq perl python3 lark-cli ffmpeg ffprobe` 均可用。
2. `curl http://127.0.0.1:9222/json/list` 能返回 tab 列表。
3. 9222 浏览器里已有已登录的 `compass.jinritemai.com` 或 `fxg.jinritemai.com` 页面。
4. 如果要写飞书，`lark-cli` 已登录且有目标 Base/Table 权限。
5. 如果要剪辑，`DOUYIN_SELECTION_CLIP_SCRIPT` 存在且可执行。
6. 输出目录可写；默认会在当前执行目录或 `DOUYIN_SELECTION_PROJECT_DIR` 下生成 `deliverables/runs/`。

缺任一项时，停止主链路并给出具体恢复动作；不要继续猜页面或伪造结果。

### 输入契约

自然语言主入口当前支持：

```text
给 <店铺名> 跑<N>个候选
```

批量入口优先使用 JSONL，每行至少包含：

```json
{"product_name":"商品名","category_3":"三级类目","record_id":"飞书记录ID","status":"📝待评估"}
```

`product_name` 必填；其他字段可选。CSV 只作为轻量兼容，复杂商品名建议用 JSONL。

### 输出契约

一次成功运行至少应产出：

- `deliverables/runs/<时间>_<店铺>/products/商品报告_YYYY-MM-DD.md`
- `deliverables/runs/<时间>_<店铺>/products/<商品>/带货视频/*.mp4`
- `deliverables/runs/<时间>_<店铺>/clip_outputs/<商品目录>/*_clip.mp4`
- `.runtime/` 下的抓取 manifest、运行日志、失败/重试摘要

交给千川投流的唯一素材入口是 `clip_outputs/<商品目录>/*_clip.mp4`；投流阶段不负责重新修尺寸。

### 降级策略

- 罗盘页面无法自动进入：提示用户在 9222 浏览器手动打开 `compass.jinritemai.com/shop/chance/rank-product`，再继续。
- 飞书不可用：允许加 `--skip-feishu` 跑本地产物，但必须在汇报中说明未入库。
- 通知不可用：完整链路默认通知；只有用户明确要求或通知依赖缺失时才跳过，并说明原因。
- 剪辑依赖不可用：不要把原始带货视频当投流素材；停止在素材下载完成态，要求恢复剪辑依赖。

## 前置依赖

| 依赖 | 说明 |
|------|------|
| Chrome CDP 9222 | 已登录抖音罗盘（compass.jinritemai.com） |
| agent-browser skill | 浏览器自动化操作 |
| 飞书 Base `QqKbbaGvvah8CgsMSWzcHZcMn1c` | 选品清单表 `tblmnpex440PHytL` |
| `jq` / curl | 数据处理 |

## 流程总览

```
Phase 1 罗盘采集 → Phase 2 爆品预筛 → Phase 3 素材提取/下载 → Phase 4 极简报告 → Phase 5 飞书入库 → Phase 6 上架准备
```

**执行规范：采集过程保持静默，完成后一次性汇报。中间不停、不等确认。**

---

## Phase 1: 罗盘采集

### 导航路径

```
compass.jinritemai.com/shop/chance/rank-product → 切换到「短视频榜」tab
```

### 页面导航规则

执行采集前必须先枚举 `http://127.0.0.1:9222/json/list`，确认 `9222` 里已有登录态页面。

目标榜单页 URL：

`https://compass.jinritemai.com/shop/chance/rank-product`

推荐顺序：

1. 如果已有 tab URL 包含 `compass.jinritemai.com/shop/chance/rank-product`，直接复用。
2. 如果当前在 `fxg.jinritemai.com` 抖店后台、`compass.jinritemai.com` 罗盘首页或其他罗盘页面，先在同一 tab 直接导航到目标榜单页。
3. 如果直达后被重定向或空白，再只尝试固定入口：抖店后台 `商品` → `商品榜单`，或罗盘页面内搜索/入口词 `商品榜单`、`机会榜单`、`短视频榜`。
4. 如果 2-3 分钟内仍不能到达目标榜单页，停止探索并让用户手动打开目标榜单页；不要无限截图、点击、搜索。

榜单页判定：

- URL 包含 `/shop/chance/rank-product`。
- 页面出现 `短视频榜`、`总榜`、`搜索榜`、`直播榜`、`商品卡榜` 等榜单 tab。
- 必须切到 `短视频榜`，不能停在总榜/搜索榜/直播榜。

### 筛选设置

| 项目 | 值 |
|------|-----|
| 榜单 | 短视频榜 |
| 时间 | 近 7 天 |
| 类目 | 根据当次目标选择三级类目 |
| 排序 | 热度上升优先 或 7天GMV 降序 |

### 采集字段

商品名称、行业类目（三级）、榜单排名、7天销量、7天营业额、素材量（带货视频数）、热度趋势、商品链接（好货详情页 URL）

### 采集量

TOP 50（预筛后）

### 输出

候选商品列表 JSON，进入 Phase 2。

---

## Phase 2: 爆品预筛

### Step 2.1 硬性排除

**知名大品牌直接排除，不入库。** 判断标准：是否有广泛消费者认知度 + 官方渠道（天猫旗舰店/京东自营等）。品牌因类目而异，由 AI 自行判断。

### Step 2.2 AI 爆品潜质判断

基于榜单层字段做轻量判断，不进好货详情页，不写飞书：

- 榜单排名
- 7天销量 / 7天营业额
- 带货视频数
- 热度趋势
- 客单价合理性
- 差异化空间
- 店铺匹配度（是否适合当前店铺）

输出：

- `通过`
- `观察`
- `不通过`

仅 `通过` 项进入后续素材提取与入库。

---

## Phase 3: 素材提取与下载

### Step 3.1 获取好货链接与视频清单

优先从页面数据层直接提取：

- `product_detail_h5_url`
- `video_list`
- `video_id`
- `video_play_url`

如数据层缺失，再回退到 tooltip 交互链路。

### Step 3.2 manifest 生成与即时下载

先生成 manifest，再立即下载，不复用过期 URL。

视频文件命名要求：

- 仅英文、数字、日期、下划线
- 全局不重复
- 推荐格式：`shop_alias_YYYYMMDD_r{rank}_v{index}_{aweme_id}.mp4`

用户可见目录只保留：

- `商品报告_YYYY-MM-DD.md`
- `带货视频/*.mp4`
- `clip_outputs/<商品目录>/*_clip.mp4`

投流素材硬约束（必须在选品剪辑阶段完成）：

- `clip_outputs/<商品目录>/*_clip.mp4` 必须是竖版 `9:16`
- 推荐分辨率：`720x1280` 或 `1080x1920`
- 不允许把“尺寸修正”留到投流阶段兜底
- 进入投流前应先用 `ffprobe` 抽检宽高，异常素材在选品链路内重剪/重编码

`video_urls_*.jsonl`、`video_fetch_summary_*.json` 这类抓取元数据不放在商品可见目录，统一转入隐藏的 `.runtime/`。

### Step 3.3 输出内容

- 带货短视频
- 全局 manifest / 单商品 manifest
- 下载结果汇总

---

## Phase 4: 极简报告

```
商品报告_YYYY-MM-DD.md
```

当前按日期汇总，同一天内新增商品继续追加；若同一商品重复跑，则更新该商品条目。

每个商品条目当前只保留：

- 商品名
- 好货链接

---

## Phase 5: 写入飞书

仅将通过预筛并完成素材提取的商品写入飞书。

字段映射：

| 飞书字段 | 来源 | 初始值 |
|----------|------|--------|
| 商品名称 | 罗盘标题 | - |
| 分类 | 三级类目 | - |
| 素材链接 | 好货页 URL | - |
| 销量 | 7天销量 | - |
| 客单价 | 7天营业额 ÷ 销量 | 计算 |
| 素材量 | 带货视频数 | - |
| 榜单排行 | 排名 | - |
| 热度趋势 | 趋势标识 | - |
| 营业额(7天) | 7天GMV | - |
| 选品状态 | - | **✅已选** |

**重复处理：** 商品已存在时更新原记录（不改 created_at），不新增。

完成整轮链路后，默认通过飞书发送完成通知；如果同一项失败超过 2 次，再生成失败记录并在通知中带出。

通知口径必须默认开启：

- 自然语言触发完整链路时，不要主动加 `--no-notify`。
- 只有用户明确说“不要通知”“跳过飞书通知”“本地验证不通知”时，才允许使用 `--no-notify`。
- 默认通知走飞书应用内加急；只有用户明确说“电话通知”“电话加急”“打电话给我”时，才优先使用电话加急。

---

## Phase 6: 上架准备

对通过商品生成上架所需的结构化输入，供后续上架/投流链路复用。

---

## 脚本说明

这个 skill 本身带有自己的：

- `scripts/`
- `references/`

也就是说，skill **可以直接引用自己目录下的脚本和参考文件**。

当前已随 skill 收编的脚本位于：
```
~/.agents/skills/douyin-selection-sop/scripts/
```

| 脚本 | 用途 |
|------|------|
| `run_batch_selection.sh` | 批量任务入口（jsonl 队列） |
| `fetch_short_videos.sh` | 单商品带货视频提取/下载 |
| `sync_feishu_selection.sh` | 飞书重复记录更新 |

当前有一个例外：

- `run_selection_to_clip.sh`

它现在已经正式收编回 skill 自身目录：
```
~/.agents/skills/douyin-selection-sop/scripts/run_selection_to_clip.sh
```

也就是说，`douyin-selection-sop` 目前是：

- 叶子执行脚本：已在 skill 自身目录
- 总控脚本：也已在 skill 自身目录

项目目录中仍保留一个同名兼容入口：
```
~/Documents/JokerSu-knowledge/20_项目/抖音电商选品流程跑通/scripts/run_selection_to_clip.sh
```

它只做一件事：转发到 skill 自身目录里的正式实现，避免留下两份分叉逻辑。

批量执行示例：
```bash
cd ~/.agents/skills/douyin-selection-sop
bash ./scripts/run_batch_selection.sh \
  --queue-file ./scripts/templates/batch_tasks.example.jsonl \
  --cdp-port 9222 \
  --download
```

---

## 详细参考

- 完整 SOP 含导航路径、异常处理、历史数据 → `references/sop-full.md`
- 参数报告 16 章节模板 → `references/report-template.md`
- 能力边界与已知限制 → `references/boundary.md`
