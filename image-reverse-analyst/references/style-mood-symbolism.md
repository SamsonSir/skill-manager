# 十大分析维度（下）· 语义层

覆盖 G 风格 / H 情绪 / I 文字 / J 象征。

---

# G. STYLE ANALYSIS｜风格分析

**必须首先回答：「这是什么风格？」**

风格分析是第一段输出的核心，放在所有分析的最前面。

## 必须回答的八项

| # | 项 | 说明 |
| --- | --- | --- |
| 1 | 风格名称 | 一个准确的命名，不是泛称 |
| 2 | 核心视觉特征 | 3–5 条，可观察的视觉事实 |
| 3 | 属性 | 摄影 / 绘画 / CGI / 插画 / 商业视觉 / 混合 |
| 4 | 光影特征 | 硬软、反差、光源类型 |
| 5 | 色彩特征 | 主调、饱和度、分级风格 |
| 6 | 材质特征 | 质感取向（写实/风格化/数字感） |
| 7 | 构图特征 | 构图法、留白、对称性 |
| 8 | 为什么判断属于这种风格 | 给出推理链，不是贴标签 |

## 风格命名参考

| 类别 | 命名示例 |
| --- | --- |
| 摄影 | editorial fashion photography · documentary street photography · cinematic film still · commercial product photography · fine art portrait |
| 影视 | neo-noir · technicolor musical · spaghetti western · nouvelle vague |
| 数字 | hyperreal CGI · stylized 3D render · game cinematic |
| 插画 | flat vector illustration · watercolor · ink wash · retro poster art |
| 商业 | luxury advertising · minimal product visual · key art |
| 混合 | photographic composite · mixed-media collage |

## 相近视觉语言

如果存在明显相似的经典影视、摄影、动画、艺术作品或创作流派，**可以指出**：

```
相近的视觉语言：与 1970 年代新好莱坞时期的低调光肖像存在相似之处
```

**但不要声称图片就是某位艺术家或某部作品制作的。** 只描述视觉语言的相似性。

```
✅ 与 XX 的视觉语言存在相似之处
❌ 这是 XX 的作品
❌ 模仿 XX 的风格（暗示确定）
```

**重点描述视觉语言，而不是简单贴标签。**

---

# H. MOOD｜情绪氛围

## 判断项

cinematic · elegant · mysterious · nostalgic · futuristic · dramatic · peaceful · surreal · romantic · tense · heroic · melancholic · playful · documentary · luxurious

## 必须解释形成原因

**不能只给一个情绪词。** 必须解释这种情绪是如何通过四个要素共同形成的：

```
composition + lighting + color + subject + environment
```

写法示例：

```
情绪：mysterious

形成原因：
构图 —— 主体被门框切割，只露出局部，信息不完整
光影 —— 单一光源，70% 画面沉入阴影，观众看不清全貌
色彩 —— 冷青主调，几乎没有暖色锚点
主体 —— 面部朝向画面外，视线不交代
环境 —— 空荡的走廊，缺乏生活痕迹
```

**四个要素缺一不可。** 只说"因为光线暗所以神秘"是不够的。

---

# I. TYPOGRAPHY｜文字分析

## 有文字时

| 项 | 内容 |
| --- | --- |
| 文字内容 | 逐字转录（注意：只转录你能看清的） |
| 字体风格 | 衬线 / 无衬线 / 手写 / 装饰 / 等宽 |
| 字重 | 细 / 常规 / 粗 / 特粗 |
| 字体大小 | 相对画面的比例 |
| 排版方式 | 单行 / 多行 / 弧形 / 竖排 / 叠压 |
| 位置 | 九宫格位置 |
| 对齐方式 | 左对齐 / 居中 / 右对齐 |
| 颜色 | 具体色名 |
| 与画面的关系 | 压在图上是/下、是否与主体互动、有无描边或投影 |

## 没有文字时

**固定填法，不得编造：**

```json
"typography": {
  "text": "None",
  "font_style": "None",
  "position": "None"
}
```

## 硬性规则

**不要自行编造图片中不存在的文字。**

看不清的字标 `UNCERTAIN` 并说明"部分字迹无法辨认"，不要猜。

---

# J. SYMBOLISM｜象征意义

## 分析项

symbolism · metaphor · narrative meaning · visual metaphor · cultural references · emotional symbolism

## 没有明显象征时

**使用固定句式，不要强行过度解读：**

```json
"symbolism": {
  "concept": "No obvious symbolic concept",
  "representation": "The image primarily communicates through visual aesthetics and composition."
}
```

## 判断原则

| 应该分析 | 不应该分析 |
| --- | --- |
| 画面中有明确的隐喻性元素（枯萎的花、断裂的桥、紧闭的门） | 强行把普通物体解读成象征 |
| 有明确的文化符号或宗教意象 | 凭个人联想编造含义 |
| 有清晰的叙事线索 | 把画面元素罗列成"象征清单" |

**判断不准就标 `UNCERTAIN` 或直接用"无明显象征"的固定句式。**

过度解读比不解读更糟——它会让用户以为画面里有不存在的东西。

---

# 语义层检查表

- [ ] 第一段开头是「风格：XXX」
- [ ] 风格八项都回答了
- [ ] 「为什么判断」给了推理链，不是贴标签
- [ ] 相近视觉语言用了"存在相似之处"，没声称是某人作品
- [ ] 情绪解释了四个要素如何共同形成
- [ ] 文字逐字转录，看不清的标了 UNCERTAIN
- [ ] 无文字时填的是 "None"，没有编造
- [ ] 无象征时用了固定句式，没有过度解读
