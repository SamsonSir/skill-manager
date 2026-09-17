# 反推生成提示词

完成视觉分析后，把所有信息**重新组合**成一份可直接用于 AI 图像生成的完整提示词。

---

## 14 个必备要素

| # | 要素 | 说明 |
| --- | --- | --- |
| 1 | Subject | 主体是什么 |
| 2 | Appearance | 外观细节 |
| 3 | Pose | 姿态与朝向 |
| 4 | Clothing | 服装与配饰 |
| 5 | Environment | 环境与场景 |
| 6 | Composition | 构图方式 |
| 7 | Camera | 机位与取景 |
| 8 | Lens | 焦段与景深 |
| 9 | Lighting | 光影 |
| 10 | Color | 色彩 |
| 11 | Materials | 材质 |
| 12 | Style | 风格 |
| 13 | Atmosphere | 氛围 |
| 14 | Fine Details + Image Quality | 细节与画质 |

**一个都不能少。** 缺哪个都会让复现度下降。

---

## 12 级优先级

要素的**书写顺序**按这个优先级排，越靠前权重越高：

```
1.  Subject
2.  Identity / Appearance
3.  Pose / Action
4.  Environment
5.  Composition
6.  Camera
7.  Lighting
8.  Color
9.  Materials
10. Style
11. Fine Details
12. Image Quality
```

**顺序即权重。** 把最重要的信息放在最前面，别让画质词挤占开头的位置。

---

## 必须是自然语言

**Prompt 必须是自然语言，而不是关键词垃圾堆。**

```
❌ 女人, 窗边, 侧脸, 85mm, 浅景深, 电影感, 高级, 4k, 8k, masterpiece, best quality

✅ 一位 20 代后半的女性以四分之三侧脸站在窗边，身体略向画面右侧转约 30 度，
   视线落在画面外的光源方向；她穿一件深墨绿防水风衣，衣料因雨水浸湿而颜色加深、
   贴在肩线上。取景为胸部以上的近景，主体压在画面左侧三分线上，占画面高度约 55%，
   右侧留出大片柔和的窗光背景。85mm 焦段，浅景深，焦点落在眼睛与侧脸轮廓线上，
   背景柔和虚化。硬质侧光从画面右侧的窗户斜射进来，在颧骨与下颌投下边缘锐利的阴影，
   高光集中在鼻梁与颧骨高点。整体为冷蓝灰基调，仅窗光带来暖橙点缀……
```

---

## 禁止空词堆砌

```
❌ masterpiece, best quality, ultra amazing, perfect, extremely detailed,
   extremely detailed, extremely detailed, 8k 8k 8k
```

**理由**：这些词不描述任何可拍摄的特征。同样的字数用来写材质、光位、动作，效果差十倍。

### 替换对照

| 空词 | 替换为 |
| --- | --- |
| beautiful | 具体的五官与气质描述 |
| stunning | 具体的光影反差描述 |
| masterpiece | 删掉 |
| best quality | 删掉，或用具体的材质描述 |
| extremely detailed | natural skin pores, visible fabric weave |
| cinematic | 具体的光位 + 色彩分级 |
| 4k / 8k | 删掉，模型不响应分辨率数字 |
| award winning | 删掉 |
| perfect lighting | 光位方向 + 光质 + 色温 |

---

## 可信度标注

提示词里凡是来自 `INFERRED` 的参数，**用约数或区间表达**：

```
✅ shot with an 85mm lens, shallow depth of field around f/2
✅ camera at roughly eye level, approximately 1.5 meters away
❌ shot with an 85mm f/1.4 lens at 1/250s ISO 400
```

`UNCERTAIN` 的项**不要写进提示词**，或者写得很模糊：

```
✅ the exact lens is uncertain, but the compression suggests a medium telephoto
```

---

## 中文提示词的排版

**写成一段，不分行、不用 bullet。**

分行会被部分模型当作多条独立提示解析，破坏权重。

如果内容确实很长（超过 200 字），按 12 级优先级的顺序自然连写，用逗号与句号分隔，不要换行。

---

## 检查表

- [ ] 14 个要素全部覆盖
- [ ] 书写顺序符合 12 级优先级
- [ ] 是自然语言，不是关键词堆叠
- [ ] 没有 masterpiece / best quality 这类空词
- [ ] INFERRED 参数用了约数或区间
- [ ] UNCERTAIN 的项没有写成确定值
- [ ] 整段不分行
