# VISUAL DNA

VISUAL DNA 是 Prompt 的依据。**先建立 DNA，再生成 Prompt。**

DNA 的本质：把 23 个维度的观察结果，压缩成一组**可复用的生成参数**。

---

## 十个分区

| 分区 | 内容 | 主要来源维度 |
| --- | --- | --- |
| 主体 DNA | 人物身份特征（脸型/五官/发/体型/年龄感） | 2, 3, 4 |
| 造型 DNA | 服装/饰品/材质/磨损/穿着方式 | 5 |
| 场景 DNA | 环境/建筑/天气/时代/空间层次 | 8, 9, 10 |
| 构图 DNA | 构图法/主体位置与占比/画幅/留白 | 11, 23 |
| 镜头 DNA | 机位/焦段/景深/透视 | 12, 13, 14, 15 |
| 光线 DNA | 光位/光质/色温/反差/光源数量与来源 | 16, 17 |
| 色彩 DNA | 主调/辅助/点缀/饱和度/分级风格 | 19 |
| 材质 DNA | 皮肤/织物/金属/玻璃/环境材质 | 18 |
| 风格 DNA | 摄影风格/流派/年代/参考方向 | 20 |
| 后期 DNA | 锐化/颗粒/光晕/调色/合成痕迹 | 21, 22 |

---

## 标注规范

**每一项都要带标注**，这是本技能最重要的纪律。

```
[observed]  画面中可直接看见，描述准确、可验证
[inferred]  合理推测，给出推测依据
```

### 必须标 `[inferred]` 的项目

以下参数**物理上无法从单张画面确定**，一律标 `[inferred]`：

- 焦段 Focal Length
- 光圈值 Aperture
- 快门速度 Shutter Speed
- ISO
- 灯位与灯型（画面外的灯你看不见）
- 后期软件与调色工具
- 拍摄机型

**违反这条 = 虚构。** 后果是用户拿着错误的参数去复现，怎么调都不像，还找不到原因。

### 标注示例

```
镜头 DNA
  机位      [observed] 平视略低，约与胸口齐高
  焦段      [inferred] 85mm 左右 —— 依据：面部透视自然无明显形变，
                       背景压缩明显，人物与背景尺度差被拉大
  景深      [observed] 眼睛与鼻尖清晰，耳后开始虚化，背景完全糊化
  光圈      [inferred] f/1.8–f/2.2 —— 依据：景深过渡范围极窄
  透视      [observed] 无广角畸变，垂直线平行
```

---

## 一致性优先级

发生冲突时**自上而下**取舍。数字越小越不能动。

```
1. 人物身份   ← 最高，脸不能变
2. 构图
3. 空间
4. 镜头
5. 光线
6. 材质
7. 色彩
8. 风格
9. 后期       ← 最低，可牺牲
```

**实际含义**：
- 用户要求换服装 → 可以，但脸和构图必须守住
- 用户要求换场景 → 空间关系尽量保留，光线方向尽量继承
- 生成结果与参考图不像 → 优先检查前四项，别急着调后期

---

## DNA 输出格式

```markdown
## VISUAL DNA

### 主体 DNA
脸型 [observed] ...
五官 [observed] ...
发型发色 [observed] ...
体型 [observed] ...
年龄感 [observed] ...

### 造型 DNA
上装 [observed] ...
下装 [observed] ...
鞋履 [observed] ...
饰品 [observed] ...
材质与磨损 [observed] ...

### 场景 DNA
场所 [observed] ...
时代 [observed] ...
建筑与结构 [observed] ...
天气 [observed] ...
空间层次 [observed] 前景：... / 中景：... / 背景：...

### 构图 DNA
构图法 [observed] ...
主体位置与占比 [observed] ...
画幅 [observed] ...
留白 [observed] ...

### 镜头 DNA
机位 [observed] ...
焦段 [inferred] ... 依据：...
景深 [observed] ...
光圈 [inferred] ... 依据：...
透视 [observed] ...

### 光线 DNA
光位 [observed] ...
光质 [observed] ...
光源数量与来源 [observed] ...
反差 [observed] ...
色温 [observed] 冷暖倾向 / [inferred] 具体 K 值
阴影 [observed] ...

### 色彩 DNA
主调 [observed] ...
辅助色 [observed] ...
点缀色 [observed] ...
饱和度 [observed] ...
分级风格 [inferred] ...

### 材质 DNA
皮肤 [observed] ...
织物 [observed] ...
金属 [observed] ...
环境材质 [observed] ...

### 风格 DNA
摄影风格 [observed] ...
流派与年代 [observed] ...
参考方向 [inferred] ...

### 后期 DNA
锐化 [inferred] ...
颗粒 [inferred] ...
光晕 [inferred] ...
调色 [inferred] ...
合成痕迹 [inferred] ...
```

---

## DNA 到 Prompt 的映射

DNA 建立后，Prompt 按这个顺序拼装：

```
[画质与风格] + [主体 DNA] + [造型 DNA] + [动作/姿态] + [场景 DNA]
+ [空间层次] + [构图 DNA] + [镜头 DNA] + [光线 DNA] + [色彩 DNA]
+ [材质 DNA] + [后期 DNA]
```

**规则**：DNA 里标 `[inferred]` 的项目，写进 Prompt 时用**约数或区间**表达，不要写成确定值。

```
Correct:  shot on an 85mm lens, shallow depth of field around f/2
Wrong:    shot on an 85mm f/1.4 lens at 1/250s ISO 400
```

前者诚实，后者编造。用户拿前者能复现，拿后者会被误导。
