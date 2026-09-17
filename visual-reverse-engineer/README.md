# 视觉逆向工程 · 安装说明

一个独立的跨工具 Agent Skill。把图片或视频反向拆解成 Visual DNA，再重构出可复现原始视觉效果的提示词。

**本技能是独立包,不依赖也不属于 `ai-visual-skills` 仓库**,可单独安装、单独分发。

---

## 这是什么

用户上传图片或视频,技能自动执行:

```
视觉识别 → 结构拆解 → Visual DNA → Prompt 重构
```

产出:图片模式下输出【视觉分析 + VISUAL DNA + 图片 Prompt + Negative Prompt】;视频模式下额外输出【人物动作 + 环境运动 + 摄影机运镜 + 焦点变化 + 镜头节奏 + 时间轴 + 连续性锁定】。

### 和普通"图片描述器"的区别

| 描述器 | 本技能 |
| --- | --- |
| 回答"看到了什么" | 回答"这张画面是如何生成的" |
| "一个女孩站在窗边" | "85mm 中长焦、f/2 级浅景深、单侧窗光 45° 打光、主体压右三分点、暖调低反差分级" |
| 参数随口编 | 焦段/光圈/灯位一律标 `[inferred]` 并给出推测依据 |

---

## 一、安装

本技能是 [`visual-reverse-engineer`](../../) 仓库的一部分,推荐用仓库级安装器。

### 方式一:skills CLI(推荐)

```bash
npx skills add <sundny8>/visual-reverse-engineer -g -y
```

### 方式二:npm

```bash
npx visual-reverse-engineer install --all
# 或全局安装后用短别名
npm i -g visual-reverse-engineer && vre install --all
```

### 方式三:克隆仓库后跑脚本

```bash
git clone https://github.com/<sundny8>/visual-reverse-engineer.git
cd visual-reverse-engineer

# Node(零依赖)
node bin/cli.js install --all

# 或 Python 3.7+(零依赖,无需 Node)
python scripts/install.py --all
```

### 方式四:手动复制

把本文件夹(`skills/visual-reverse-engineer/`)整个复制到目标 agent 的 skills 目录即可,唯一要求是**文件夹内必须有 `SKILL.md`**:

```bash
cp -r visual-reverse-engineer ~/.claude/skills/
cp -r visual-reverse-engineer ~/.workbuddy-ai/skills/
```

Windows PowerShell:

```powershell
Copy-Item -Recurse -Force .\visual-reverse-engineer "$env:USERPROFILE\.claude\skills\"
```

安装后**重启对应工具**才会加载新技能。

---

## 二、各 agent 目录对照

| Agent | 用户级(全局) | 项目级 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex CLI | `~/.codex/skills/` | `.agents/skills/` |
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| Qoder | `~/.qoder/skills/` | `.qoder/skills/` |
| WorkBuddy | `~/.workbuddy-ai/skills/` | `.workbuddy-ai/skills/` |
| GitHub Copilot | `~/.copilot/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.agents/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |

> Windows 上 `~` 即 `C:\Users\<用户名>`。软链接需要开启开发者模式,脚本会自动降级为复制。

---

## 三、怎么用

装好后不用记命令,直接上传图片或视频说需求:

```
反推这张图的提示词
```

```
照着这张图写提示词,尽量一模一样,只把背景换成雪山
```

```
分析这段视频的运镜和节奏,给出 Seedance 可用的提示词
```

```
提取这张图的画面参数,我要在 Midjourney 里复现
```

```
只要提示词,不用分析
```

手动触发(支持 `/` 命令的工具):

```
/visual-reverse-engineer 分析这张图
```

### 四种输出模式

| 模式 | 触发 | 输出区块 |
| --- | --- | --- |
| 图片模式 | 素材是图片 | 4 个 |
| 视频模式 | 素材是视频 | 11 个 |
| 只要提示词 | 用户说"只要提示词" | 2 个 |
| 对比模式 | 多张参考图 | 逐图分析 + 对比表 + 融合 Prompt |

完整范例见 `references/examples.md`(图片、视频各一个)。

---

## 四、七条核心原则怎么落地的

| 原则 | 实现方式 |
| --- | --- |
| 1️⃣ 反推而非描述 | Prompt 里写光位角度、焦段区间、景深范围,不写"很美""有氛围感" |
| 2️⃣ 先分析后生成 | 强制先输出 VISUAL DNA,Prompt 从 DNA 推导 |
| 3️⃣ 事实与推测分离 | 每项标 `[observed]` / `[inferred]`,焦段光圈灯位必须标推测并附依据 |
| 4️⃣ 最大化一致性 | 九级优先级阶梯:人物身份 ＞ 构图 ＞ 空间 ＞ 镜头 ＞ 光线 ＞ 材质 ＞ 色彩 ＞ 风格 ＞ 后期 |
| 5️⃣ REFERENCE LOCK MODE | 十项锁定清单,只改用户指定项,并说明连带影响 |
| 6️⃣ 视频连续性 | 逐项列出锁定清单 + 状态继承规则,禁止项写进 Negative |
| 7️⃣ 动态 Negative | 扫描参考图实际风险元素,逐项生成,**没有的元素不加** |

---

## 五、目录结构

```
visual-reverse-engineer/         ← 本技能目录(位于仓库的 skills/ 下)
├── SKILL.md                              主入口:工作流 + 硬性约束 + 输出契约
├── README.md                             本文件
└── references/
    ├── analysis-dimensions.md            23 个分析维度与识别方法
    ├── visual-dna.md                     VISUAL DNA 结构与九级优先级
    ├── image-mode.md                     图片模式输出规范
    ├── video-mode.md                     视频模式:七个新增区块
    ├── reference-lock.md                 REFERENCE LOCK MODE 十项锁定
    ├── negative-prompt.md                动态负面词生成规则与词库
    ├── output-format.md                  四种输出模式与排版规范
    ├── examples.md                       图片 + 视频两个完整范例
    └── full-prompt.md                    单段式提示词(给只吃 system prompt 的工具)
```

**渐进式披露**:`SKILL.md` 只放工作流和硬性规则,细节按需读 `references/`。

---

## 六、给不支持 Skills 的工具用

网页版大模型、自定义 GPT 等没有 Skills 机制。这些场合用 `references/full-prompt.md`:整段复制粘贴到 system prompt 或角色设定里即可,功能等价。

---

## 七、自定义

| 想改什么 | 改哪里 |
| --- | --- |
| 分析维度的颗粒度 | `references/analysis-dimensions.md` |
| 一致性优先级顺序 | `references/visual-dna.md` |
| REFERENCE LOCK 的锁定项 | `references/reference-lock.md` |
| 负面词库 | `references/negative-prompt.md` |
| 输出区块的增减 | `references/output-format.md` |

改完若用 `--link` 方式安装,所有 agent 立即生效;用复制方式则需重跑一次安装命令。

---

## 八、与其他技能的关系

本技能**独立可用**,不需要任何其他技能。

如果你还有 `ai-visual-skills` 仓库(含 `image-prompt-director` 和 `seedance-director`),三者的分工是:

| 技能 | 输入 | 用途 |
| --- | --- | --- |
| `image-prompt-director` | 一句话想法 | **正向创作**:从零生成图片提示词 |
| `seedance-director` | 一句话想法 | **正向创作**:从零生成 30 秒视频提示词 |
| `visual-reverse-engineer` | 一张图/一段视频 | **逆向复现**:从成品反推提示词 |

前两个是"无中生有",本技能是"照猫画虎"。三者互不依赖,可单独安装。
