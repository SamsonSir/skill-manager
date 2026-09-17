# 图片反推专家 · 说明

本技能是 [`visual-reverse-engineer`](../../) 仓库的一部分。

**只做图片，不做视频。** 固定输出三段：风格分析 → 中文图片提示词 → 全英文 JSON。

---

## 这是什么

上传一张图片，自动输出三样东西：

1. **风格分析** —— 这是什么风格、为什么这么判断、与哪些视觉语言相近
2. **中文图片提示词** —— 一段可直接使用的中文 Prompt，覆盖 14 个要素
3. **全英文 JSON** —— 严格 schema 的结构化描述，可直接喂进下游管线

定位是 **Image Reverse Engineering**，不是 Image Captioning。

### 和普通"图片描述器"的区别

| 描述器 | 本技能 |
| --- | --- |
| 「一个女人站在窗边，光线很柔和」 | 「85mm 焦段、浅景深、侧窗硬光 45°、主体压左三分点、暖调低反差」 |
| 一段文字 | 风格分析 + 中文提示词 + 结构化 JSON |
| 参数随口编 | 区分 `OBSERVED` / `INFERRED` / `UNCERTAIN` |
| 编造图上的文字 | 看不清就标 UNCERTAIN，没有就填 `"None"` |

---

## 安装

本技能随仓库一起安装。

### 方式一：skills CLI（推荐）

```bash
npx skills add <sundny8>/visual-reverse-engineer -s image-reverse-analyst -g -y
```

### 方式二：npm

```bash
npx visual-reverse-engineer install -s image-reverse-analyst --all
# 或全局安装后用短别名
npm i -g visual-reverse-engineer && vre install --all
```

### 方式三：克隆仓库后跑脚本

```bash
git clone https://github.com/<sundny8>/visual-reverse-engineer.git
cd visual-reverse-engineer

# Node（零依赖）
node bin/cli.js install --all

# 或 Python 3.7+（零依赖，无需 Node）
python scripts/install.py --all
```

### 方式四：手动复制

把本文件夹（`skills/image-reverse-analyst/`）整个复制到目标 agent 的 skills 目录即可：

```bash
cp -r image-reverse-analyst ~/.claude/skills/
```

安装后**重启对应工具**才会加载新技能。

---

## 怎么用

直接上传图片说需求：

```
反推这张图
```

```
这张图是什么风格？
```

```
提取这张图的 JSON
```

```
分析这张图的摄影参数
```

手动触发（支持 `/` 命令的工具）：

```
/image-reverse-analyst 分析这张图
```

### 输出长什么样

```
① 风格分析

风格：cinematic documentary street photography, 1970s film aesthetic

风格特点：
* 现场实用光源为主，霓虹与店铺灯构成唯一光源
* 高感光度胶片质感，可见明显颗粒与高光溢出
* ...

为什么判断为这种风格：
画面的光源全部来自画面内的霓虹与店铺橱窗，人物脸部有明确的方向性
照明而非均匀布光，说明未使用影棚灯或反光板。...

相近的视觉语言：
与 1970 至 1980 年代东亚城市的夜间街头纪实摄影存在相似之处。

② 图片生成提示词

一位 20 代后半的东亚女性站在夜间店铺门前的中景画面，...

③ JSON Prompt

{
  "scene": "a night-time urban street outside a shop entrance...",
  "subjects": [...],
  ...
}
```

完整范例见 `references/examples.md`。

---

## 十大分析维度

| 组 | 维度 |
| --- | --- |
| 视觉层 | A 主体 · B 构图 · C 摄影 · D 光影 · E 色彩 · F 材质 |
| 语义层 | G 风格 · H 情绪 · I 文字 · J 象征 |

细节见 `references/analysis-dimensions.md` 与 `references/style-mood-symbolism.md`。

---

## 几条关键纪律

### 角度只给近似值

```
✅ head turned approximately 15 degrees / three-quarter view / profile view
❌ head turned exactly 17.5 degrees
```

不要假装精确到无法从图片判断的程度。

### 材质不能只写 high detail

必须解释**细节是什么**、以及**为什么产生这种质感**：

```
✅ natural skin pores, subtle facial micro-texture, fine hair strands,
   realistic fabric weave, soft specular highlights
❌ highly detailed, ultra detailed
```

### 不编造文字

图上看不清就标 `UNCERTAIN`，没有就填 `"None"`。

### 不过度解读象征

没有明显象征就用固定句式：

```json
"symbolism": {
  "concept": "No obvious symbolic concept",
  "representation": "The image primarily communicates through visual aesthetics and composition."
}
```

### 不声称知道原始 Prompt

图像是**多对一**的——不同 Prompt 可以生成相似画面。正确表述：

> 这是根据最终图像反向重建的高概率 Prompt。

### JSON 必须严格合规

valid JSON、双引号、无注释、无尾逗号、全英文、无 Markdown、无中文字符、无编造内容。缺项填 `"None"`。

---

## 目录结构

```
image-reverse-analyst/          ← 本技能目录（位于仓库的 skills/ 下）
├── SKILL.md                              主入口：工作流 + 硬性约束 + 输出契约
├── README.md                             本文件
└── references/
    ├── analysis-dimensions.md            十大维度（上）：主体/构图/摄影/光影/色彩/材质
    ├── style-mood-symbolism.md           十大维度（下）：风格/情绪/文字/象征
    ├── reverse-prompt.md                 提示词重组 + 12 级优先级 + 空词替换表
    ├── json-schema.md                    JSON schema + 九条质量要求 + 常见错误
    ├── uncertainty-and-safety.md         三级可信度 + 安全替换对照表
    ├── output-format.md                  三段式固定格式
    ├── examples.md                       完整成品范例
    └── full-prompt.md                    单段式提示词（给只吃 system prompt 的工具）
```

---

## 给不支持 Skills 的工具用

网页版大模型、自定义 GPT 等没有 Skills 机制。这些场合用 `references/full-prompt.md`：整段复制粘贴到 system prompt 或角色设定里即可，功能等价。

---

## 自定义

| 想改什么 | 改哪里 |
| --- | --- |
| 分析维度 | `references/analysis-dimensions.md`、`references/style-mood-symbolism.md` |
| 提示词优先级 | `references/reverse-prompt.md` |
| JSON 字段 | `references/json-schema.md`（注意：改字段会破坏下游兼容性） |
| 输出段落结构 | `references/output-format.md` |
| 可信度分级规则 | `references/uncertainty-and-safety.md` |

改完若用 `--link` 方式安装，所有 agent 立即生效；用复制方式则需重跑一次安装命令。

---

## 同仓库的另一个技能

| 技能 | 输入 | 输出 | 适用 |
| --- | --- | --- | --- |
| **image-reverse-analyst**（本技能） | 一张图片 | 风格分析 + 中文提示词 + 英文 JSON | 只要图片，要结构化 JSON |
| [`visual-reverse-engineer`](../visual-reverse-engineer/) | 图片**或视频** | VISUAL DNA + 图片/视频 Prompt + Negative Prompt | 要视频反推、要一致性锁定、要负面词 |

**怎么选**：

- 要 **JSON**、要**风格分析**、只处理图片 → 用本技能
- 要 **视频反推**、要 **REFERENCE LOCK**、要 **Negative Prompt** → 用 `visual-reverse-engineer`

两者可同时安装，按描述自动触发。
