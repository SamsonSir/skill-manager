# 成品范例

一个完整走通三段输出的范例。用这个校准质量。

**用户上传**：一张复古胶片风格的夜间街头照片 —— 一位穿风衣的女性站在亮着霓虹招牌的店铺门前，招牌上有可辨认的汉字。
**用户要求**：反推这张图。

---

## ① 风格分析

```
风格：cinematic documentary street photography, 1970s film aesthetic

风格特点：
* 现场实用光源为主，霓虹与店铺灯构成唯一光源，无人工补光痕迹
* 高感光度胶片质感，可见明显颗粒与高光溢出（halation）
* 冷青主调中嵌入单一暖橙霓虹锚点，饱和度整体偏低
* 中景取景，主体与街景环境信息量接近，非突出人物的肖像式构图
* 竖构图，主体略偏画面右侧，左侧留出街道纵深

为什么判断为这种风格：
画面的光源全部来自画面内的霓虹与店铺橱窗，人物脸部有明确的方向性照明而
非均匀布光，说明未使用影棚灯或反光板。颗粒分布均匀且在高光边缘出现明显的
光晕扩散，这是胶片在过曝高光处的典型表现，数字传感器不会产生这种扩散。
色彩上整体冷青但霓虹呈现高饱和暖橙，且暖色的边缘有轻微的色散，符合老式
镜头在最大光圈下的表现。构图采用中景而非近景，环境占据了大量画面面积，
说明拍摄意图是记录场景而非塑造人物，这是纪实摄影的典型取景习惯。

相近的视觉语言：
与 1970 至 1980 年代东亚城市的夜间街头纪实摄影存在相似之处，
也与当代以胶片模拟方式处理的城市夜景作品在色彩与颗粒取向上接近。
```

---

## ② 图片生成提示词

```
一位 20 代后半的东亚女性站在夜间店铺门前的中景画面，身体略向画面左侧转约 20 度，
头部转向画面右侧看向街面，视线略低于水平线；她穿一件米灰色中长款风衣，衣领立起，
内搭深色高领针织，右手插在风衣口袋里，左肩挂一只深棕色皮质单肩包；背景是夜间
城市街道，她身后是一块亮着暖橙与品红霓虹的竖式店铺招牌，招牌上有可辨认的汉字，
招牌下方是透出暖黄光的橱窗，街道向左后方延伸并逐渐消失在雾气中，湿滑的路面
反射着霓虹的色彩；取景为中景，主体压在画面右侧三分线上，占画面高度约 50%，
左侧留出街道纵深，竖构图；相机在平视略低于眼高的位置，距离约 2 米，正面略偏左；
镜头推测在 35mm 左右，中等景深，人物与身后招牌清晰，远处街道柔和虚化；光线
来自画面后方的霓虹招牌与橱窗，形成暖橙色的侧逆光，人物脸部的左半边被照亮、
右半边落入阴影，阴影边缘柔和，环境中冷青色的天光提供极弱的补光；色彩为冷青
主调，仅霓虹呈现高饱和暖橙，整体饱和度偏低，接近青橙分级的低饱和版本；
材质上可见皮肤的自然纹理与轻微油光、风衣面料的斜纹织构与因穿着产生的自然褶皱、
皮包表面的细微颗粒与边缘磨损、湿路面的镜面反射与水膜纹理；整体氛围为疏离而
安静的都市夜归感，人物与繁华招牌之间存在情绪反差；细节包含胶片颗粒、
高光边缘的光晕扩散、霓虹在湿路面上的破碎倒影、空气中极淡的雾气、
风衣下摆因微风的轻微偏移；画面为高感光度胶片质感，可见颗粒，
高光有轻微溢出，整体锐度中等，边缘有轻微色散。
```

---

## ③ JSON Prompt

```json
{
  "scene": "a night-time urban street outside a shop entrance with illuminated neon signage, wet pavement reflecting the lights, the street receding into faint haze toward the left background",
  "subjects": [
    {
      "type": "human",
      "description": "an East Asian woman in her late twenties wearing a mid-length light grey trench coat with the collar turned up, a dark high-neck knit underneath, her right hand in her coat pocket, a dark brown leather shoulder bag on her left shoulder",
      "position": "right third of the frame, occupying about 50 percent of the frame height"
    }
  ],
  "style": "cinematic documentary street photography with a 1970s film aesthetic",
  "color_palette": [
    "cold cyan",
    "warm amber neon",
    "magenta neon accent",
    "light grey",
    "deep charcoal",
    "wet asphalt black"
  ],
  "lighting": "practical neon signage and shop window as the only light sources, warm amber side-backlight from behind the subject at frame right, soft-edged shadows across the face, extremely weak cold ambient fill from the night sky",
  "mood": "solitary and quietly melancholic, with an emotional contrast between the isolated figure and the vibrant signage behind her",
  "composition": "medium shot, subject on the right third line with the street receding into depth on the left, vertical framing, moderate depth of field keeping both the subject and the signage sharp",
  "camera": {
    "angle": "eye level, slightly below eye height, frontal with a slight offset to the left",
    "distance": "approximately 2 meters",
    "lens": "approximately 35mm, medium depth of field"
  },
  "typography": {
    "text": "Chinese characters on the vertical neon shop sign, partially legible",
    "font_style": "vertical neon signage with blocky sans-serif character strokes",
    "position": "behind the subject, upper center of the frame"
  },
  "symbolism": {
    "concept": "No obvious symbolic concept",
    "representation": "The image primarily communicates through visual aesthetics and composition."
  },
  "rendering_details": {
    "textures": "natural skin texture with subtle oil sheen, twill weave and natural creases in the trench coat fabric, fine grain and edge wear on the leather bag, mirror-like reflections and water film texture on the wet pavement",
    "effects": "visible film grain, halation and light bloom around the neon highlights, slight chromatic aberration at the frame edges, faint atmospheric haze, broken neon reflections on the wet ground, subtle motion in the coat hem"
  }
}
```

---

## 这个范例示范了什么

1. **风格分析放最前**，且「为什么判断」给了完整推理链（光源全在画面内 → 无人工补光；高光边缘扩散 → 胶片特征；暖色边缘色散 → 老式镜头），不是贴标签。

2. **相近视觉语言用了"存在相似之处"**，没有声称是某位摄影师的作品。

3. **可信度标注贯穿全文**：光源方向、阴影边缘、色彩是 `OBSERVED`；焦段 35mm、距离 2 米、光圈是 `INFERRED`（写作"推测在 35mm 左右"、"约 2 米"）；招牌上部分字迹不清标 `UNCERTAIN`。

4. **材质解释了"细节是什么"**：不是写 `highly detailed`，而是写"风衣面料的斜纹织构与因穿着产生的自然褶皱""皮包表面的细微颗粒与边缘磨损"。

5. **中文提示词是一段自然语言**，覆盖全部 14 个要素，没有换行，没有 `masterpiece` 这类空词。

6. **JSON 全英文、严格 schema、无尾逗号**，`color_palette` 给了 6 个具体色名而不是泛称。

7. **象征意义没有强行解读** —— 画面里没有明确的隐喻元素，所以用了固定句式，而不是把风衣或霓虹硬说成象征。

8. **文字处理诚实** —— 招牌上有汉字且部分可辨，JSON 里如实写了 `"partially legible"`，没有编造完整文字内容。
