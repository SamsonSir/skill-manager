# 成品范例

用这两个范例校准输出质量。注意标注纪律、优先级落地、以及 Negative Prompt 如何从实际风险点推导。

---

# 范例一 · 图片模式

**用户上传**：一张棚拍时尚人像 —— 女性侧脸，深红色背景，硬光打出一道鼻梁高光。
**用户要求**：反推提示词。

## 【视觉分析】

```
主体      [observed] 女性，单人，半身入画，画面唯一焦点
身份      [observed] 20 代中后段，东亚面孔，身形纤细
五官      [observed] 鹅蛋脸，颧骨偏高，单眼皮，眼尾略微上挑，鼻梁挺直鼻头小巧，
                   唇形饱满，唇峰清晰，下颌线利落
发型      [observed] 黑色长发，中分，向后梳光，无碎发，发面有镜面光泽
体型      [observed] 肩窄，锁骨明显，颈部修长
服装      [observed] 黑色高领无袖针织，哑光面料，贴合身体
姿态      [observed] 纯侧脸朝向画面右侧，头部微仰约 10°，肩线下沉
动作      [observed] 静态，无动作
场景      [observed] 棚拍，无缝背景纸，无环境元素
前中后景  [observed] 前景：无 / 中景：人物 / 背景：纯色背景纸，无纵深
空间关系  [observed] 人物居中偏左，右侧留出约 35% 空背景
构图      [observed] 三分构图，主体压在左三分线，占画面高度约 70%
机位      [observed] 平视，约与眼齐高，距离约 1.2m
焦段      [inferred] 85–105mm — 依据：面部无透视形变，鼻与耳的距离被压缩，
                   背景完全无纵深但仍无广角畸变
景深      [observed] 眼睛与鼻梁锐利，耳后与发梢略虚
光圈      [inferred] f/4–f/5.6 — 依据：面部纵深内保持清晰，只有发梢开始虚，
                   比 f/1.4 的景深范围宽
光线      [observed] 硬光源，来自画面右前方约 45°，形成鼻梁与颧骨的清晰高光带；
                   左侧有弱补光，暗部保留细节
阴影      [observed] 硬边阴影，下颌下方投出清晰的三角形阴影
材质      [observed] 皮肤有毛孔与细绒毛质感，无油光；针织面料有细密罗纹；
                   头发为高光泽镜面反射
色彩      [observed] 背景为饱和深红（偏冷调的正红），人物全黑，
                   肤色暖调，形成三色关系
风格      [observed] 时尚杂志硬光人像，当代棚拍
后期      [inferred] 锐度较高，无明显颗粒，暗部略压，肤色做过轻微提亮
画幅      [observed] 4:5 竖版
```

## 【VISUAL DNA】

```
主体 DNA   鹅蛋脸 / 颧骨偏高 / 单眼皮眼尾上挑 / 鼻梁挺直鼻头小巧 /
           唇形饱满唇峰清晰 / 下颌线利落 / 黑发中分梳光 / 窄肩修长颈部
造型 DNA   黑色高领无袖针织，哑光，贴合；无饰品；无磨损
场景 DNA   棚拍无缝背景纸，深红，无环境元素，无纵深
构图 DNA   三分构图，主体压左三分线，占高 70%，右侧 35% 留白，4:5
镜头 DNA   平视眼高，约 1.2m 距离 / [inferred] 85–105mm / f/4–5.6 /
           面部纵深内清晰，发梢起虚
光线 DNA   硬光，右前方 45°，弱左侧补光，硬边阴影，暗部保留细节，
           色温暖调
色彩 DNA   背景饱和深红（偏冷正红）+ 人物全黑 + 肤色暖调，三色关系
材质 DNA   皮肤有毛孔与细绒毛，无油光；针织细密罗纹；头发镜面高光
风格 DNA   时尚杂志硬光人像，当代棚拍
后期 DNA   [inferred] 高锐度，无颗粒，暗部微压，肤色轻微提亮
```

## 【图片 Prompt】

```
high-fashion studio beauty portrait, hard-light editorial style, a woman in her
mid-to-late twenties of East Asian descent, oval face with high cheekbones,
monolid eyes with an upward tilt at the outer corners, straight nose with a
small tip, full lips with a defined cupid's bow, sharp jawline, long black hair
center-parted and slicked back with a mirror-like sheen and no flyaways, narrow
shoulders and a long slender neck, wearing a black high-neck sleeveless knit top
in a matte ribbed fabric, pure side profile facing frame right with the head
tilted up about ten degrees and the shoulder line dropped, static and composed,
shot against a seamless deep saturated red studio backdrop with no environmental
elements and no depth, rule of thirds composition with the subject on the left
third line occupying about seventy percent of the frame height and thirty-five
percent of clean negative space on the right, eye-level camera at roughly 1.2
meters, shot on a real cinema camera with an 85mm lens, moderate depth of field
around f/4 to f/5.6 with the eyes and nose bridge razor sharp and the hair tips
beginning to soften, a single hard key light from the front right at roughly
forty-five degrees carving a crisp highlight band along the nose bridge and
cheekbone, a weak fill on the left holding detail in the shadows, hard-edged
shadows including a clear triangular shadow under the jaw, visible skin pores and
fine facial hair with no shine, fine ribbed knit texture, high-gloss specular
reflections in the hair, warm skin tones against the cold-leaning saturated red
backdrop, high sharpness with no visible grain and slightly crushed shadows,
8K UHD, Ultra realistic, Photorealistic, Professional photography, Highly
detailed, Realistic texture, Natural skin --ar 4:5 --style raw --v 6.1
```

## 【Negative Prompt】

画面里有：**人脸特写**、**皮肤大面入画**、**发丝**、**针织织物**、**纯色背景**、**无手部入画**。

据此生成（**未加手部词**，因为画面里没有手）：

```
low quality, blurry, out of focus, jpeg artifacts, watermark, signature, text,
logo, AI artifacts, flat lighting, unrealistic shadows, oversaturated,
no face distortion, no identity drift, no asymmetrical eyes, no dead eyes,
no plastic skin, no over-smoothed skin, no airbrushed skin, no waxy texture,
no oily shine, no messy flyaway hair, no dull hair, no fabric clipping,
no distorted knit pattern, no background gradient, no background texture,
no visible studio equipment, no harsh color banding
```

---

# 范例二 · 视频模式

**用户上传**：一段 6 秒的城市街头跟拍视频 —— 女性撑伞快步走过雨后街道。
**用户要求**：反推视频提示词，用于 Seedance。

## 【视觉分析】（节选，23 维度全量输出的摘要）

```
主体      [observed] 女性，单人，跟随拍摄
五官      [observed] 圆脸，眉眼柔和，鼻梁中等，唇形偏薄
服装      [observed] 米色长款风衣，深蓝牛仔裤，白色帆布鞋，黑色单肩包
场景      [observed] 雨后夜晚的城市商业街，两侧店铺，路面湿滑反光
前中后景  [observed] 前景：虚化的路人肩膀 / 中景：人物 / 背景：霓虹招牌与街灯
构图      [observed] 中景跟拍，人物在画面中轴偏右
机位      [observed] 平视略低，手持
焦段      [inferred] 35mm — 依据：透视自然，能容纳两侧街景，无明显压缩
景深      [observed] 人物清晰，背景中等虚化
光线      [observed] 多光源实用光：店铺暖光 + 霓虹冷光 + 路灯，湿地面形成反射
色彩      [observed] 青蓝主调 + 暖黄点缀，青橙分级
```

## 【VISUAL DNA】

```
主体 DNA   圆脸 / 眉眼柔和 / 鼻梁中等 / 唇形偏薄 / 黑色中长发 / 中等身高
造型 DNA   米色长款风衣 + 深蓝牛仔裤 + 白色帆布鞋 + 黑色单肩包 + 透明长柄伞
场景 DNA   雨后夜晚商业街，两侧店铺，湿滑反光路面，霓虹与街灯
构图 DNA   中景跟拍，人物中轴偏右，约占画面高度 60%
镜头 DNA   [inferred] 35mm / 平视略低 / 手持轻微晃动 / 中等景深
光线 DNA   多光源实用光（店铺暖光 + 霓虹冷光 + 路灯），湿地面反射
色彩 DNA   青蓝主调 + 暖黄点缀，青橙分级
材质 DNA   湿风衣有深色水痕，湿发，积水反光
风格 DNA   纪实感城市夜拍，手持跟随
后期 DNA   [inferred] 轻颗粒，暗部微提
```

## 【人物动作】

```
[observed] 她右手握伞柄，左臂自然摆动，步伐偏快，视线朝前略偏右
[inferred] 步频约每秒 2 步，摆臂幅度小，重心平稳

动作链拆解（一个完整步态周期）
  准备  右脚落地承重，左腿抬起准备前摆
  动作  左腿前摆，左臂向后摆，右臂持伞基本不动
  接触  左脚掌先着地，脚掌接触积水
  反馈  水花向外溅起约 15cm 并落回，风衣下摆因惯性滞后半拍
  结果  重心前移，右腿开始抬起，进入下一周期
```

## 【环境运动】

```
天气      [observed] 无雨，地面有积水，空气中有薄雾
光线      [observed] 霓虹招牌有轻微闪烁，店铺灯光稳定
倒影      [observed] 湿地面反射街灯与霓虹，随步伐产生波纹扰动
人群      [observed] 背景有稀疏路人，虚化后移动
植被      [observed] 无
烟雾      [observed] 无，但有轻微雾气使远处灯光扩散
```

## 【摄影机运镜】

```
类型      [observed] 手持跟拍 Tracking Shot
方向      [observed] 与人物同向，向右前方移动
速度      [inferred] 与人物步速同步，约 1.2 m/s
稳定性    [observed] 轻微手持晃动，幅度小，无剧烈抖动
轴线      [observed] 始终在人物左后方，未越轴
```

## 【焦点变化】

```
初始焦点  [observed] 人物面部
跟焦      [observed] 人物移动时持续跟焦，面部保持清晰
拉焦      [observed] 无
景深      [observed] 全程恒定，背景保持中等虚化
```

## 【镜头节奏】

```
镜头数量  [observed] 单镜到底
单镜时长  [observed] 约 6 秒
切换      [observed] 无
节奏      [observed] 匀速
情绪节拍  [observed] 无高点，平稳叙事
```

## 【时间轴】

```
0.0–1.5s   中景跟拍，人物从画面左侧入画，快步前行，伞面占据画面上部
1.5–3.0s   镜头跟随前进，背景霓虹招牌掠过，湿地面反射被脚步打散
3.0–4.5s   人物略微偏头看向右侧店铺，视线短暂停留，脚步未停
4.5–6.0s   镜头继续跟随，人物走出画面右侧边缘，画面留出空荡街道与雾气
```

## 【连续性锁定】

```
人物身份   圆脸、眉眼、年龄感、肤色 —— 全片不得变化
发型       黑色中长发 —— 不得变化
服装       米色长款风衣 + 深蓝牛仔裤 + 白色帆布鞋 —— 不得换装、不得增减件数
道具       透明长柄伞 —— 全程在右手，不得消失或换手
           黑色单肩包 —— 全程在左肩，不得消失
环境       雨后夜晚商业街，湿滑反光路面
空间关系   人物始终在画面中轴偏右，镜头在左后方
光线       多光源实用光，霓虹有轻微闪烁
天气       无雨，地面有积水，空气中薄雾
时间       全程夜晚

状态继承
  0.0s 起人物即处于雨中行走后的状态：风衣下摆有深色水痕、发梢微湿
  全程保持水痕与湿发，不得变干
  3.0s 起人物偏头 → 4.5s 后回归正前方，视线方向变化要连续过渡
```

## 【视频 Prompt】

```
cinematic handheld tracking shot, documentary urban night style, a woman in her
late twenties of East Asian descent with a round face, soft eyes, medium nose
bridge and thin lips, black mid-length hair, medium build, wearing a long beige
trench coat with dark water stains along the hem, dark blue jeans, white canvas
sneakers, a black shoulder bag on her left shoulder, holding a transparent long
umbrella in her right hand, walking quickly forward with a small arm swing while
her gaze drifts slightly to frame right, through a rain-washed commercial street
at night with shops on both sides and wet reflective pavement, out-of-focus
passerby shoulders in the immediate foreground, the woman sharp in the midground,
neon signage and street lamps softly blurred in the background, medium shot with
the subject on the center-right, eye-level slightly low camera following from her
rear left at a matched pace of about 1.2 meters per second, shot on a 35mm lens
with moderate depth of field holding focus on her face throughout, motivated
multi-source practical lighting from warm shop windows, cold neon signage and
street lamps, wet pavement reflecting the lights and rippling with each footstep,
cool blue-cyan grade with warm yellow accents in teal and orange, wet trench coat
and damp hair catching specular highlights, thin mist diffusing the distant
lights, no rain falling but standing water present, water splashing outward from
each footfall and falling back, the trench coat hem lagging half a beat behind
her stride, neon flickering subtly, sparse blurred pedestrians moving in the
background, single continuous take, steady pace with slight handheld sway, no
cuts, maintaining identical facial features, identical hairstyle, identical
outfit, identical props and identical environment throughout, 8K UHD, Ultra
realistic, Photorealistic, Cinematic lighting, Highly detailed, Realistic texture,
Natural skin, Professional photography, real motion blur, subtle film grain
--ar 9:16 --duration 6s
```

## 【Negative Prompt】

画面里有：**人脸（跟拍全程）**、**手（持伞、摆臂）**、**道具（伞、包）**、**文字招牌**、**多人**、**织物**、**水体**。视频模式必加连续性词。

```
low quality, blurry, out of focus, jpeg artifacts, watermark, signature, logo,
AI artifacts, flat lighting, unrealistic shadows, oversaturated,
no face distortion, no identity drift, no asymmetrical eyes, no dead eyes,
no plastic skin, no over-smoothed skin, no airbrushed skin,
no extra fingers, no fused fingers, no claw hands, no malformed hands,
no warped umbrella, no disappearing umbrella, no hand switching,
no disappearing bag, no warped jewelry,
no garbled text, no nonsensical letters, no unreadable signage,
no duplicate faces, no extra people, no merged bodies,
no clipping fabric, no rigid cloth simulation,
no unrealistic water flow, no static water, no floating water,
no outfit change, no hairstyle change, no morphing features,
no disappearing props, no background jump, no flickering,
no frame inconsistency, no unstable camera, no unnatural motion,
no weightless movement, no teleporting, no rubber limbs
```

---

## 两个范例示范了什么

1. **标注纪律** —— 每一项都有 `[observed]` / `[inferred]`，焦段光圈全部标推测并给出依据。
2. **不描述"看到了什么"，而是反推"如何生成"** —— 写的是光位角度、焦段区间、景深范围，不是"她很漂亮"。
3. **前中后景三层** —— 图片范例里明确写了"前景无"，视频范例里前景是虚化路人肩膀。
4. **视频环境运动独立成块** —— 霓虹闪烁、积水反射、路人移动、雾气扩散。
5. **连续性锁定逐项列出** —— 伞、包、水痕、湿发都写了继承规则。
6. **Negative Prompt 从实际风险推导** —— 图片范例**没有加手部词**（画面里没有手），视频范例加了手部词（持伞摆臂）。
7. **Prompt 一段到底** —— 没有换行、没有 bullet。
