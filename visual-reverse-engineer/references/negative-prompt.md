# Negative Prompt 动态生成

## 核心规则

**禁止无脑堆砌。** Negative Prompt 必须从**参考图的实际风险点**出发。

通用词串的问题是：该防的没防，不该防的挤占了权重。一张没有人物的风景图加 `no extra fingers` 是纯噪音。

---

## 生成流程

### Step 1 — 扫描参考图，列出实际存在的高风险元素

| 画面里有 | 风险 | 对应负面词 |
| --- | --- | --- |
| 手 | 多指、粘连、畸形 | no extra fingers, no fused fingers, no claw hands, no missing fingers |
| 人脸 | 换脸、五官漂移、双眼不对称 | no face distortion, no identity drift, no asymmetrical eyes, no dead eyes |
| 皮肤特写 | 塑料感、过度磨皮 | no plastic skin, no over-smoothing, no airbrushed skin, no waxy texture |
| 文字/招牌 | 乱码、无意义字母 | no garbled text, no nonsensical letters, no unreadable signage |
| 镜面/玻璃 | 反射错误 | no incorrect reflections, no warped reflections |
| 多人 | 重复脸、身体融合 | no duplicate faces, no merged bodies, no extra people |
| 动物/生物 | 多腿、双头 | no extra legs, no two heads, no impossible anatomy |
| 车辆/机械 | 融化、多轮 | no melted parts, no extra wheels, no floating components |
| 精细饰品 | 变形、消失 | no warped jewelry, no disappearing accessories |
| 织物 | 穿模、僵硬 | no clipping fabric, no rigid cloth simulation |
| 水体 | 不自然的流动 | no unrealistic water flow, no static water |
| 建筑 | 结构歪斜、垂直线不平行 | no warped architecture, no converging verticals |
| 大片天空/水面 | 噪点、色带 | no banding, no heavy noise |
| 全身 | 比例失调 | no wrong proportions, no elongated limbs |

**只加参考图里真实存在的元素对应的词。** 没有的不要加。

### Step 2 — 追加基础质量词

```
low quality, blurry, out of focus, jpeg artifacts, watermark, signature,
AI artifacts, flat lighting, oversaturated
```

### Step 3 — 视频模式追加

```
no identity drift, no outfit change, no morphing features, no disappearing props,
no background jump, no flickering, no frame inconsistency, no unstable camera,
no unnatural motion, no weightless movement, no teleporting
```

### Step 4 — REFERENCE LOCK MODE 追加

```
no face change, no hairstyle change, no outfit change, no identity drift,
no composition shift, no camera angle change, no lighting change,
no color grading change, no style drift
```

### Step 5 — 冲突检查

**正向词与负面词不得冲突。** 逐条比对：

| 正向写了 | 就不能写 |
| --- | --- |
| shallow depth of field | blurry background |
| soft lighting | harsh shadows |
| film grain | no noise |
| muted color palette | desaturated（同义反复） |
| natural skin texture | no skin texture |

虚化背景不是模糊，胶片颗粒不是噪点——这类词搞混会互相抵消。

---

## 词库

### 基础（每次必加）

```
low quality, blurry, out of focus, jpeg artifacts, watermark, signature, text,
logo, AI artifacts, flat lighting, unrealistic shadows, oversaturated
```

### 人物

```
deformed hands, extra fingers, missing fingers, fused fingers, claw hands,
malformed limbs, wrong anatomy, bad proportions, plastic skin,
over-smoothed skin, airbrushed, uncanny face, asymmetrical eyes, dead eyes,
duplicate faces, identical twins, merged bodies
```

### 产品

```
cluttered background, product blur, blown highlights, cheap plastic look,
distorted proportions, fingerprints, dust on surface
```

### 场景

```
warped architecture, converging verticals, shifted geometry,
impossible architecture, inconsistent scale
```

### 风格

```
cheap CGI look, video game render, cartoon, illustration, anime, painting,
3d render, low poly
```

### 视频专用

```
identity drift, outfit change, morphing features, disappearing props,
background jump, flickering, frame inconsistency, unstable camera,
unnatural motion, weightless movement, teleporting, rubber limbs, clipping
```

---

## 数量控制

| 场景 | 建议数量 |
| --- | --- |
| 简单主体（产品、风景） | 15–25 个 |
| 常规（单人、单场景） | 25–40 个 |
| 复杂（多人 + 文字 + 精细道具） | 40–60 个 |
| 超过 80 个 | **过多，会互相干扰，需精简** |

---

## 输出格式

```
【Negative Prompt】

<针对本图实际风险点的词>, <基础质量词>, <视频专用词（视频模式）>
```

**不要解释为什么加这些词**——除非用户问了。

---

## 常见错误

| 错误 | 问题 | 修正 |
| --- | --- | --- |
| 固定词串套所有图 | 风景图里加手部词 | 按实际元素生成 |
| 堆到上百个 | 互相干扰，效果变差 | 控制在 60 内 |
| 与正向词冲突 | 互相抵消 | 做冲突检查 |
| 用否定式描述主体 | 模型会读到被否定的词 | 只写要排除的缺陷，不写 `not a man` |
| 漏掉视频专用词 | 第二镜就崩 | 视频模式必加连续性词 |
