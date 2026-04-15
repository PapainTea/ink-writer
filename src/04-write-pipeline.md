# 写章流程（Pipeline）

本章节定义"写下一章"的完整流程。用户说"写第 N 章"或"写下一章"时，严格按此流程执行。

---

## 流程总览

```
Step 1  确定章节号 + 确认书籍
Step 2  加载 Context（读所有相关文件）
Step 3  规划（Planner）—— 确定本章意图
Step 4  写作前自检（PRE_WRITE_CHECK）
Step 5  写正文（Writer）
Step 6  写后校验（Post-write Validator，机械规则检查）
Step 7  审计（Auditor，**默认必跑**，作者可显式 opt-out）
Step 8  修订（Reviser，如审计发现 critical 问题）
Step 9  结算（Settler）—— 更新 7 个 truth files
Step 10 快照（Snapshot）—— 保存当前状态到 snapshots/N/
Step 11 写入正文文件 + 更新 index.json
Step 12 完成验证（强制）—— 运行 verify-chapter.py，不通过不算完成
```

**硬约束**：
- 绝不跳过 Step 9（结算）、Step 10（快照）、Step 12（验证）
- 绝不在 Step 9 之前就把正文写入 `chapters/` 目录
- Step 2 的读取必须完整，不要凭记忆

---

## Step 1: 确定章节号 + 确认书籍

### 操作

1. 如果用户未指定书名 → 询问（或根据上下文推断）
2. 列出 `<父目录>/books/<书名>/chapters/` 目录
3. 找到最大章节号 N
4. 下一章号 = N + 1

### 边界情况

- 如果 `chapters/` 为空 → 这是第 1 章（需要先确认基础文件齐全）
- 如果用户说"写第 15 章"但当前已有 14 章 → 正常，写第 15 章
- 如果用户说"写第 15 章"但当前已有 20 章 → 警告用户会覆盖已有章节，询问是否确认（或建议用 rework 模式）

---

## Step 2: 加载 Context

### 必读文件清单

从 `<父目录>/books/<书名>/story/` 读：

1. `story_bible.md` — 世界观设定
2. `volume_outline.md` — 卷纲（**定位到当前章节的大纲节点**）
3. `book_rules.md` — 本书规则
4. `current_state.md` — 当前状态卡
5. `particle_ledger.md` — 资源账本
6. `pending_hooks.md` — 伏笔池
7. `chapter_summaries.md` — 章节摘要（重点看最近 3-5 章）
8. `subplot_board.md` — 支线进度板
9. `emotional_arcs.md` — 情感弧线（重点看最近 3-5 章）
10. `character_matrix.md` — 角色交互矩阵

从 `<父目录>/books/<书名>/chapters/` 读：

11. 最近 1 章正文（第 N-1 章）—— 用于过渡衔接
12. `index.json` — 章节索引

### 可选文件

- `author_intent.md`、`current_focus.md`（如果存在）
- 更早的章节正文（如果本章需要回顾较早事件）

### Context 管理

- 如果 truth files 超大（单个文件 > 500 行），只读最近 10 章相关部分 + 本章相关角色
- 但 `current_state.md` 永远全读
- 如果模型 context 不够 → 优先保留 current_state + recent summaries + volume_outline 当前节点

---

## Step 3: 规划（Planner）

### 目标

基于 Context，明确本章要做什么。

### 输出清单

一个简短的规划笔记（不落盘，仅在当前对话中使用）：

```markdown
## 第 N 章规划

### 本章目标（Goal）
<一句话，基于 volume_outline 当前节点 + current_focus>

### 对应大纲节点（Outline Node）
<从 volume_outline 中引用本章对应的节点原文>

### 必须保留（Must Keep，最多 4 项）
- 来自 current_state 的硬状态
- 来自 story_bible 的铁律

### 必须避免（Must Avoid，最多 6 项）
- 来自 book_rules.prohibitions
- 来自 current_focus 的避免项
- 已有伏笔的信息越界

### 本章伏笔议程（Hook Agenda）
- 必须推进：<hook_id 列表>
- 可以回收：<hook_id 列表>
- 陈旧债务：<超过 10 章未推进的 hook>
- 避免新增的 hook 族：<避免重复的 hook 类型>

### 风格重点（Style Emphasis，最多 4 项）
<来自 current_focus + author_intent>
```

### 规划原则

- **大纲优先于灵感**：volume_outline 是硬约束，不能跳过节点
- **状态自洽优先于爽点**：current_state 中的限制必须尊重
- **伏笔先回收再新埋**：有陈旧债务时优先回收
- **一章一冲突**：本章核心冲突只有一个

---

## Step 4: 写作前自检（PRE_WRITE_CHECK）

### 必须输出的自检表（Markdown 表格格式）

```markdown
### PRE_WRITE_CHECK

| 检查项 | 本章记录 | 备注 |
|--------|----------|------|
| 大纲锚定 | <当前卷名/阶段 + 本章应推进的具体节点> | 严禁跳过节点或提前消耗后续剧情 |
| 上下文范围 | 第 <X> 章至第 <Y> 章 / 状态卡 / 设定文件 | |
| 当前锚点 | 地点：<> / 对手：<> / 收益目标：<> | 锚点必须具体 |
| 当前资源总量 | <与账本一致的数字> | |
| 本章预计增量 | +<数字>（来源：<事件>）| 无增量写 +0 |
| 待回收伏笔 | <Hook-A / Hook-B> | 与伏笔池一致 |
| 本章冲突 | <一句话概括> | |
| 章节类型 | <开篇/过渡/高潮/转折/回忆 等> | |
| 目标字数 | target=<X> / softMin=<A> / hardMin=<B> | 来自 book_rules.length 或作者指定 |
| 字数预算分配 | 见下方场景表 | 总和 ≈ target ± 5% |
| 允许偏短声明 | `是` / `否` | 见下方例外声明 |
| 风险扫描 | OOC / 信息越界 / 设定冲突 / 战力崩坏 / 节奏 / 词汇疲劳 / Markdown 结构泄漏 | 逐项自检 |
```

### 场景级字数预算（必填）

把目标字数拆成 3-6 个场景，每个场景估计 300-1500 字。**预算总和必须等于 target ± 5%**，否则 LLM 会把目标错理解成"情节完整即可"，写完偏短。

```markdown
### 字数预算

| # | 场景概述 | 预算字数 | 在章内的功能 |
|---|---------|--------|------------|
| 1 | <场景 1 概述> | ~600 | 开场、承接、引冲突 |
| 2 | <场景 2 概述> | ~800 | 推进 / 博弈 |
| 3 | <场景 3 概述> | ~1200 | 核心戏 / 高潮 |
| 4 | <场景 4 概述> | ~900 | 转折 / 兑现 |
| 5 | <场景 5 概述> | ~600 | 落幕 / 钩子 |
|   | **合计** | **~4100** | （target=4500，误差 -8.9%，可接受）|
```

**写作时对照预算**：写完一个场景对照一下实际字数，偏离超过预算 30% 要调整后续场景或补写当前场景。

### 允许偏短声明（可选，用于特殊章节类型）

**什么情况下可以声明"本章允许偏短"**（跳过 Step 6 的自动扩写）：

- **转场章**：跨弧转场，节奏紧凑是刻意设计（如 ch15 巡坊→侯城）
- **动作章**：纯动作/打斗，字数紧凑更有冲击力
- **短过渡章**：两个大场景之间的过渡，不需要铺太多
- **其他**：作者明确判断本章情节紧凑、不宜注水

**声明格式**：

```markdown
### 允许偏短声明

**本章允许偏短**：是
**理由**：转场章（ch15 离开巡坊 + 镜核首触发），动作密度高，字数紧凑更有冲击力。预算 3500 字（低于 softMin 4050 但高于 hardMin 3600），情节饱和即停。
```

**注意**：即使声明允许偏短，字数**仍然不能 < hardMin**（硬下限无条件生效）。

### 自检原则

- 所有字段**不能为空**或写"待定"
- 如果某项答不上来 → 回到 Step 3 补齐规划
- 字数预算总和必须 ≈ target ± 5%（否则回到 Step 3 重新分配）
- 这张表是写作的"锚"，写的时候要回头看

---

## Step 5: 写正文（Writer）

### 输入

- PRE_WRITE_CHECK 自检表
- §5 的规划
- §6 的完整创作规则（05-writing-rules.md）

### 输出

```markdown
### CHAPTER_TITLE
<章节标题，不含"第 X 章"前缀>

### CHAPTER_CONTENT
<正文内容>
```

### 字数要求

字数配置来自 `book_rules.yaml.length.*`（canonical schema，详见 §03）：

- **target**：目标字数（例 4500）
- **softMin = target × (1 - softMinPct%)**（例 4050）
- **softMax = target × (1 + softMaxPct%)**（例 4950）
- **hardMin = target × (1 - hardMinPct%)**（例 3600）
- **hardMax = target × (1 + hardMaxPct%)**（例 5400）
- **countingMode**：`zh_chars`（按 CJK 字符数）或 `en_words`

**写作策略**：瞄准 target，允许在 softMin ~ softMax 之间波动。偏离处理见 §04 Step 6。

**作者临时覆盖**：作者在当前对话里指定字数（例"这章写 5000"）→ 本章 target 覆盖为 5000，但不改 book_rules。

### 写作铁律（简要，完整见 05-writing-rules.md）

1. 简体中文，手机阅读友好（每段 3-5 行）
2. 禁止"不是...而是..."句式
3. 禁止破折号 `——`
4. 禁止在正文输出 hook_id / 账本式数据 / 分析术语
5. 人设必须与 character_matrix 一致
6. 信息边界必须尊重（角色只知道他知道的事）
7. 资源数值必须与 ledger 一致

---

## Step 6: 写后校验（Post-write Validator）

### 执行方式

机械规则检查 + 字数检查。完整规则见 §09（12 条机械规则）和下方字数分层处理。

### 6.1 机械规则检查

简要 12 条（详见 §09）：

- 禁止句式（"不是...而是..."、破折号、markdown 结构泄漏 `---`/`###`/`**`/列表 等）
- 疲劳词密度 / 转折标记词密度
- 连续"了"字 / 段落过长
- 分析术语泄漏 / 作者说教词 / 集体反应
- 本书禁忌违规

**结果处理**：
- 无问题 → 进入 6.2 字数检查
- ERROR 级 → 自动触发一次 spot-fix（局部修复），然后重新 Step 6.1
- WARNING 级 → 报告给作者，由作者决定是否修

### 6.2 字数分层处理（核心改动）

测量 CJK 字数（`countingMode = zh_chars`）或 en_words，与 `book_rules.yaml.length` 的区间对比：

| 区间 | 条件 | 行为 |
|------|------|------|
| **字数 ≥ softMin** | 正常范围（含 > softMax 但 ≤ hardMax）| 无事，继续 Step 7。若 softMax < 字数 ≤ hardMax，附一条 `lengthWarnings` 提示作者 |
| **softMin > 字数 ≥ hardMin** | 偏短但不硬违规 | 默认触发**一次**扩写循环（见下方）。**例外**：如果 PRE_WRITE_CHECK 中声明了"本章允许偏短"+ 理由，跳过扩写并附 `lengthWarnings` |
| **字数 < hardMin** | 硬违规 | **无条件**硬 block，必须扩写到 ≥ hardMin 才能继续。作者的"允许偏短"声明**无效** |
| **字数 > hardMax** | 超长 | 触发一次压缩循环，目标回到 softMax 以内 |

### 6.3 扩写循环（softMin / hardMin 不达标时）

1. 找正文里"单薄场景"——字数远低于该场景在 PRE_WRITE_CHECK 字数预算里的分配
2. 在**不改事实**的前提下补细节（感官、动作、人物反应、环境）
3. 绝对禁止新增情节、新 hook_id、新角色
4. 扩完再测字数，仍不达标 → 继续循环（最多 2 次）
5. 2 次仍不达标 → 报告作者，让作者决定：人工扩写 / 放弃达标并 approve / 降低 book_rules.length.target

### 6.4 压缩循环（> hardMax 时）

1. 找冗余细节、重复的环境描写
2. 合并/删除（保留所有事实性事件）
3. 压完再测字数

### 6.5 防无限循环

同一个字数问题 2 次循环仍未通过 → 停止自动循环，报告作者介入。同一条机械规则 2 次 spot-fix 仍未通过 → 同样停止。

---

## Step 7: 审计（默认必跑）

### 触发条件（默认行为）

**写章流程走到 Step 7 时必须跑一次审计**，这是默认行为，不需要作者显式触发。产出 `story/audits/ch-N.md`（详见 §06 输出格式）。

### 例外：作者可显式 opt-out

- 作者在同一对话里说"这章先不审计" / "skip audit" / "写完不审" → 跳过 Step 7，status 设为 `draft`
- `book_rules.yaml.pipeline.autoRunAudit = false`（配置层关闭，整本书都跳过审计；作者自担风险）

### 独立触发（跳过写章流程）

- 作者直接说"审计第 N 章" / "审稿第 N 章" / "check chapter N" → 不经过 Step 1-6，直接跑 Step 7，产出审计 md，不改 status 也不进 Step 8-11

### 执行方式

完整流程见 06-audit-system.md。输出结构化审计报告。

### 结果处理（audit-driven spot-fix 循环）

Step 7 跑完后**立即进入循环**：若 audit 有 `critical` 或 `warning`，自动进入 Step 8 spot-fix 修订，然后重审；直到 `0 critical + 0 warning` 才放行 Step 9 结算。

**退出条件**：audit 结果只剩 `followup` 和 `info`（或完全干净）。`followup` 是"后续章需要注意的事"（见 §06），不修本章；`info` 仅记录。都不触发 spot-fix。

**迭代上限**：默认 `MAX_ITER = 3`（第 1 轮审计 + 2 轮 spot-fix 修订）。3 轮仍有 warning+ → 停下来报告作者：
```
ch {N} 经 3 轮修订仍有 {X} 个 warning：
  - [warning] {category}: {description}
  - ...

选项：a) 放行（作者判断这些 warning 可接受，进 Step 9）；
      b) 继续多修 2 轮（MAX_ITER+2）；
      c) 切 rewrite 模式重写段落；
      d) rework 整章重写
```

**issue hash 比对防死循环**：记录上一轮和本轮的 issue hash（category+description 拼串 hash），若两轮完全重合 → 说明 spot-fix 改不动，立即 PAUSE，不硬等到 MAX_ITER。

---

## Step 8: 修订（audit-driven spot-fix，循环由 Step 7 驱动）

完整流程见 07-revision-modes.md。

**默认模式**：`spot-fix`，只针对 Step 7 audit 报告的 `critical` + `warning`（followup / info 不传给 reviser）。

**模式切换**：作者可显式指定其他模式——"润色 ch N" → polish / "改写 ch N 开头" → rewrite / "重写 ch N" → rework / "降 AI 痕迹" → anti-detect。

修订完成后回到 Step 7 重审，直到循环退出条件满足。

---

## Step 9: 结算（Settler）

### 目标

把本章的所有事实性变化同步到 7 个 truth files。

### 执行步骤

按顺序更新以下文件（完整规则见 08-settlement.md）：

1. **current_state.md** — 整体覆盖为本章末状态
2. **particle_ledger.md** — 追加本章的资源事件行
3. **pending_hooks.md** — 推进/回收/新增伏笔
4. **subplot_board.md** — 更新支线活跃章数和进度
5. **emotional_arcs.md** — 追加本章出场角色的情感行
6. **character_matrix.md** — 更新 3 子表（角色档案、相遇记录、信息边界）
7. **chapter_summaries.md** — 追加本章摘要行

### 更新原则

- 每个文件独立读→改→写
- 使用合并 key 判断"同一条记录"（见 02-truth-schema.md）
- 写回前做 Schema 守卫自检（见 02-truth-schema.md）
- 如果本章未影响某个 truth file → 不要触碰该文件（但 current_state 和 chapter_summaries 每章必改）

### 结算完整性检查

结算完成后，快速自检：

- [ ] current_state.md 的"当前章节"字段已更新为 N
- [ ] particle_ledger.md 所有新行的"期末"= 期初 + 变动
- [ ] pending_hooks.md 所有推进的 hook 的"最近推进" = N
- [ ] chapter_summaries.md 有且只有一行新章（第 N 行）
- [ ] character_matrix.md 仍保留 3 个 `### ` 子表结构

任一失败 → 排查后重新结算，不要继续 Step 10。

---

## Step 10: 快照（Snapshot）

### 操作

完整规则见 10-snapshot-rollback.md。

简要命令：

```bash
BOOK_DIR=<父目录>/books/<书名>
SNAP_DIR=$BOOK_DIR/story/snapshots/<N>

mkdir -p $SNAP_DIR
cp $BOOK_DIR/story/current_state.md $SNAP_DIR/
cp $BOOK_DIR/story/particle_ledger.md $SNAP_DIR/
cp $BOOK_DIR/story/pending_hooks.md $SNAP_DIR/
cp $BOOK_DIR/story/chapter_summaries.md $SNAP_DIR/
cp $BOOK_DIR/story/subplot_board.md $SNAP_DIR/
cp $BOOK_DIR/story/emotional_arcs.md $SNAP_DIR/
cp $BOOK_DIR/story/character_matrix.md $SNAP_DIR/
```

### 快照的语义

`snapshots/N/` = 写完第 N 章后、当时的累积状态。**绝不用后来的数据覆盖此目录**。

---

## Step 11: 写入正文文件 + 更新 index.json

### 操作

1. 写入 `chapters/000<N>_<title>.md`（编号补零到 4 位）
2. 更新 `chapters/index.json`：
   - 新增一项（或替换 rework 场景下的已有项）
   - 字段：number, title, filename, status="approved", wordCount, createdAt, auditIssues

### 文件名示例

- 第 14 章，标题"收网" → `0014_收网.md`
- 第 1 章，标题"逆刻醒来" → `0001_逆刻醒来.md`

### status 枚举（4 种状态）

| 状态 | 含义 | 触发 |
|------|------|------|
| `draft` | 初稿，未审计 | 写完 Step 5 但跳过 Step 7 |
| `audited` | 已审计但有未修复 warning | 走完 Step 7 但有 warning 未处理 |
| `approved` | 审计通过/全部修复 | 完整流程通过（Step 1-11）|
| `needs_revision` | 审计发现 critical 问题待修 | Step 7 报 critical 后未走 Step 8 |

默认走完全流程后 status = `approved`。

### 写入 index.json 的字段（精简集，无 lengthTelemetry）

```json
{
  "number": <N>,
  "title": "<标题>",
  "status": "approved",
  "wordCount": <最终字数>,
  "createdAt": "<ISO timestamp>",
  "updatedAt": "<ISO timestamp，rework/revise 时更新>",
  "lengthWarnings": []
}
```

**注**：
- 原项目的 `lengthTelemetry`（10+ 子字段）skill 模式不写入（无独立 normalize/revise 阶段）
- 原项目的 `auditIssues` 字段也不写入——审计结果存在 `story/audits/ch-<N>.md`（Obsidian callout 格式，详见 §06）

### 章节正文文件约定

- 文件名规则：4 位章节号（不足补 0）+ 下划线 + 标题 + `.md`。例：第 1 章 `0001_序章.md`，第 14 章 `0014_收网.md`
- **正文第一行写章节标题**：`# 第 N 章 <标题>`（文件名和正文都有标题，便于 markdown 直接阅读）
- 例：文件 `0014_收网.md` 的正文第一行是 `# 第14章 收网`，然后空一行进入正文

---

## Step 12: 完成验证（强制）

写完 Step 11 后，**必须**运行验证脚本确认所有副作用都到位。这是章节完成的最终门槛——不通过不算完成。

### 执行命令

```bash
python3 <ink_writer 仓库路径>/scripts/verify-chapter.py <books 绝对路径> <书名> <N>
```

例：

```bash
python3 <ink_writer_root>/scripts/verify-chapter.py \
    <books-root> \
    <书名> <N>
```

如果 PRE_WRITE_CHECK 声明了"本章允许偏短"，加 `--allow-short` 参数：

```bash
python3 .../verify-chapter.py <books-root> <书名> <N> --allow-short
```

### 三层检查内容（详见 `scripts/verify-chapter.py` 文件头注释）

| Layer | 检查内容 | 失败即 |
|-------|---------|--------|
| **1 强制不变量** | 正文存在 + index 条目 + snapshots/N/ 含 7 truth files + current_state 章节号对 + chapter_summaries 有 ch N 行 + audits/ch-N.md 存在 | exit 1 |
| **2 机械规则** | 破折号=0 / 不是而是=0 / 分析术语=0 / md 结构泄漏=0 / 字数≥hardMin（softMin 受 `--allow-short` 控制）| exit 2 |
| **3 条件性副作用** | 审计 md 里声明"推进 X truth file"时，对应文件必须有 ch N 行/变化 | exit 3 |

### 失败处理（首次 ❌ 不直接硬停，先进入自动补救循环）

首次 verify 出现 ❌ 时，**不要立即停下来让作者介入**。先按 §Step 12.1 的规则自动补救（最多 2 轮），仍 ❌ 才向作者报告不能盲修的部分。

**永远不要靠"章节看起来写完了"就收工**。人眼看不出 chapter_summaries 某行粘连、snapshots 某个文件缺失、audits 声明和实际 truth files 不一致——这些都是 verify 脚本擅长捕捉的机械问题。

---

## Step 12.1: verify ❌ 的自动补救循环（单章 + 连写共用）

### 可自动补救的 ❌（LLM 盲做，无需问作者）

| ❌ 环节 | 补救动作 |
|---------|---------|
| **Step 10 快照**：`snapshots/N/` 不存在或缺文件 | 按 §10 规则用 `cp` 把 7 个 truth files + `audits/ch-N.md` 复制到 `snapshots/N/`（含 `mkdir -p`）|
| **Step 11 索引**：`index.json` 无 ch N 条目 | 追加条目：`{number: N, title: 从文件名抽, status: approved/audited（按审计结果）, wordCount: 现场测量, createdAt/updatedAt: 当前 ISO 时间, lengthWarnings: []}` |
| **Step 7 审计**：`audits/ch-N.md` 缺失 | Read `.claude-modules/audit.md` 后重跑审计流程，输出 ch-N.md |
| **Step 6 机械禁令**：破折号 / 不是而是 / 分析术语 / markdown 泄漏出现 | Read `.claude-modules/revise.md` 走 spot-fix 清理，重跑 verify |
| **Step 6 字数**：`softMin > 字数 ≥ hardMin`（偏短但未触底）| 走 §04 Step 6.3 的一次扩写循环 |
| **Step 9 chapter_summaries 缺 ch N 行** | 基于正文生成 ch N 摘要行追加（8 列：章节/标题/出场/关键事件/状态变化/伏笔动态/情绪/类型）|
| **Step 9 current_state 当前章节 < N** | 整体覆盖 current_state.md 使"当前章节" = N，其他 7 字段按本章最新状态重写 |

### 不能盲目自动补救的 ❌（必须硬停询问作者）

| ❌ 环节 | 为什么不能盲修 |
|---------|--------------|
| **Step 5 正文文件本身缺失或空** | 写章步骤就出错，不能凭空生文 |
| **Step 6 字数 `> hardMax`** | 压缩涉及删哪段的内容判断，需要作者参与 |
| **Step 6 字数 `< hardMin`（硬下限）** | 扩写 2 轮仍不过说明故事容量不够，需要作者给新情节/细节方向 |
| **Step 9 truth file 审计声明涉及但找不到 ch N 相关行** | 结算遗漏事实性改动，需要 LLM 回到 Context 重结算（基于语义判断），盲修易错 |

对这类硬停 ❌，向作者直接报：

```
❌ ch {N} 自动补救后仍有以下环节未过：
  - {环节 1}：{为什么不能盲修}
  - {环节 2}：...

需要你决定：a) 重跑本章（rework）；b) 提供具体指示；c) 暂停，人工介入
```

### 补救循环伪代码

```
exit_code, stdout = run_verify(N)
if exit_code == 0:
    🎉 完成

remediation_attempt = 0
while exit_code != 0 and remediation_attempt < 2:
    errors = parse_errors(stdout)
    hard_stop_errors = []
    for err in errors:
        if err in AUTO_FIXABLE_TABLE:
            apply_fix(err)
            告知作者: 🔧 检测到 <err>，已应用 <fix>，重跑 verify...
        else:
            hard_stop_errors.append(err)
    if hard_stop_errors:
        break  # 不继续补救，直接报告作者
    exit_code, stdout = run_verify(N)
    remediation_attempt += 1

# 最终结果
show_to_author(stdout)  # 完整 13 环节 ✅/❌
if exit_code == 0:
    🎉 完成
else:
    硬停: report(hard_stop_errors + remaining_❌)
```

### 每轮补救都告知作者

补救过程不是闷声做。每应用一个 fix，用一行告诉作者：

```
🔧 检测到 Step 10 ❌（snapshots/16/ 缺失），已复制 7 truth files + audits/ch-16.md 到 snapshots/16/，重跑 verify...
```

作者看得见 LLM 补了什么；发现补得不对（例如漏 cp 了某文件）可以立即喊停。

### 例外：`autoRunVerify = false`

`book_rules.yaml.pipeline.autoRunVerify = false` 时 Step 12 跳过（作者自担风险）。**默认开启**。

---

## 总结：关键不变量

无论流程如何分支，以下不变量必须保持：

1. **Truth files 的行数永远只增不减**（除非用户明确要求）
2. **Snapshots 永不修改**
3. **正文中永远不出现 hook_id / ledger 格式 / 分析术语**
4. **章节编号严格递增**（除非走 rework 流程主动删除后续章节）
5. **current_state.md 和 chapter_summaries.md 每章必更新**

---

## 常见错误

| 错误 | 后果 | 预防 |
|------|------|------|
| 跳过 Step 2（凭记忆写）| truth files 不同步，信息越界 | 每次都完整读 |
| 跳过 Step 9（忘记结算）| 下一章 context 错误 | 把结算当作强制步骤 |
| 跳过 Step 10（忘记快照）| rework 模式无法回滚 | 结算后立刻快照 |
| Step 9 整体重写 truth file | 旧数据丢失 | 使用定点修改 + Schema 守卫 |
| 正文先写入 chapters/ 再结算 | 结算失败时数据不一致 | 严格按 Step 顺序 |
