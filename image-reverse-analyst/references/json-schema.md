# JSON Schema 与质量要求

第三段输出的 JSON 必须严格合规。**JSON 是全英文的。**

---

## 固定 Schema

```json
{
  "scene": "string",
  "subjects": [
    {
      "type": "string",
      "description": "string",
      "position": "string"
    }
  ],
  "style": "string",
  "color_palette": [
    "string"
  ],
  "lighting": "string",
  "mood": "string",
  "composition": "string",
  "camera": {
    "angle": "string",
    "distance": "string",
    "lens": "string"
  },
  "typography": {
    "text": "string",
    "font_style": "string",
    "position": "string"
  },
  "symbolism": {
    "concept": "string",
    "representation": "string"
  },
  "rendering_details": {
    "textures": "string",
    "effects": "string"
  }
}
```

**不得增删字段，不得改字段名。** 用户可能拿这个 JSON 直接喂进下游管线。

---

## 字段说明

| 字段 | 内容 | 示例 |
| --- | --- | --- |
| `scene` | 场景整体描述，一句话 | `"a rain-soaked narrow alley at night between six-storey walk-up apartment blocks"` |
| `subjects[]` | 主体数组，每个主体一个对象 | 见下 |
| `subjects[].type` | 主体类型 | `"human"` / `"animal"` / `"object"` / `"architecture"` / `"environment"` |
| `subjects[].description` | 外观描述 | `"a woman in her late twenties wearing a soaked dark forest-green trench coat"` |
| `subjects[].position` | 在画面中的位置 | `"left third, occupying about 55 percent of the frame height"` |
| `style` | 风格名称 | `"cinematic film still, gritty neo-noir"` |
| `color_palette` | 3–7 个具体色名 | `["deep forest green", "cold blue-grey", "warm amber", "wet charcoal"]` |
| `lighting` | 光影描述，含光位方向 | `"single warm amber practical light from frame right, hard directional key with cold ambient fill"` |
| `mood` | 情绪氛围 | `"tense and melancholic"` |
| `composition` | 构图描述 | `"rule of thirds with the subject on the left third and negative space toward the gaze direction"` |
| `camera.angle` | 机位角度 | `"eye level"` / `"low angle"` / `"slight high angle"` |
| `camera.distance` | 拍摄距离 | `"approximately 1.5 meters"` / `"medium shot distance"` |
| `camera.lens` | 焦段（含约数） | `"approximately 85mm, shallow depth of field"` |
| `typography.*` | 文字信息 | 无文字时全部填 `"None"` |
| `symbolism.*` | 象征意义 | 无明显象征时用固定句式 |
| `rendering_details.textures` | 材质细节 | `"natural skin pores, wet fabric weave, brushed metal on the watch"` |
| `rendering_details.effects` | 后期效果 | `"subtle film grain, halation on highlights, rain streaks"` |

---

## 质量要求（逐条强制）

| # | 要求 |
| --- | --- |
| 1 | **valid JSON** —— 必须能通过 `JSON.parse` |
| 2 | **double quotes only** —— 只用双引号，不用单引号 |
| 3 | **no comments** —— 不能有 `//` 或 `/* */` |
| 4 | **no trailing commas** —— 最后一个元素后不能有逗号 |
| 5 | **all values in English** —— 所有值都是英文 |
| 6 | **no Markdown inside JSON** —— 不能有 `**bold**`、`- list` 等 |
| 7 | **no Chinese characters** —— 一个中文字符都不能有 |
| 8 | **no invented text** —— 不编造图片中不存在的文字 |
| 9 | **no unsupported claims** —— 不写没有依据的断言 |

---

## 缺项处理

**如果图片没有某项内容，使用 `"None"`，而不是编造。**

```json
"typography": {
  "text": "None",
  "font_style": "None",
  "position": "None"
}
```

```json
"symbolism": {
  "concept": "No obvious symbolic concept",
  "representation": "The image primarily communicates through visual aesthetics and composition."
}
```

---

## 常见错误

| 错误 | 问题 | 修正 |
| --- | --- | --- |
| 用单引号 | 不是合法 JSON | 全改双引号 |
| 最后一项后有逗号 | 解析失败 | 删掉尾逗号 |
| 值里混中文 | 违反全英文要求 | 译成英文 |
| 值里带 Markdown | 下游管线会读到符号 | 去掉 `**` 和 `-` |
| 编造文字内容 | 用户会以为图上真有这些字 | 填 `"None"` |
| `color_palette` 只给 1–2 个 | 色彩信息不足 | 给 3–7 个 |
| 色名用泛称 | 复现不出具体颜色 | `deep crimson` 而非 `red` |
| `camera.lens` 写成确定值 | 虚构参数 | 加 `approximately` |
| 加了自己想的字段 | 破坏 schema | 严格按 schema，不增不减 |

---

## 输出前自检

把 JSON 复制出来跑一次解析，确认能过：

```bash
node -e "JSON.parse(require('fs').readFileSync('prompt.json','utf8')); console.log('valid')"
```

或者在心里逐字符检查这几点：双引号、无尾逗号、无注释、无中文、无 Markdown。

**这一段是硬性交付物，格式错了整个输出就没用了。**
