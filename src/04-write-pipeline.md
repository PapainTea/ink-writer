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
Step 7  审计（Auditor，可选，用户决定是否触发）
Step 8  修订（Reviser，如审计发现 critical 问题）
Step 9  结算（Settler）—— 更新 7 个 truth files
Step 10 快照（Snapshot）—— 保存当前状态到 snapshots/N/
Step 11 写入正文文件 + 更新 index.json
```

**硬约束**：
- 绝不跳过 Step 9（结算）和 Step 10（快照）
- 绝不在 Step 9 之前就把正文写入 `chapters/` 目录
- Step 2 的读取必须完整，不要凭记忆

---

## Step 1: 确定章节号 + 确认书籍

### 操作

1. 如果用户未指定书名 → 询问（或根据上下文推断）
2. 列出 `~/.inkos/data/books/<书名>/chapters/` 目录
3. 找到最大章节号 N
4. 下一章号 = N + 1

### 边界情况

- 如果 `chapters/` 为空 → 这是第 1 章（需要先确认基础文件齐全）
- 如果用户说"写第 15 章"但当前已有 14 章 → 正常，写第 15 章
- 如果用户说"写第 15 章"但当前已有 20 章 → 警告用户会覆盖已有章节，询问是否确认（或建议用 rework 模式）

---

## Step 2: 加载 Context

### 必读文件清单

从 `~/.inkos/data/books/<书名>/story/` 读：

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

从 `~/.inkos/data/books/<书名>/chapters/` 读：

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
| 风险扫描 | OOC / 信息越界 / 设定冲突 / 战力崩坏 / 节奏 / 词汇疲劳 | 逐项自检 |
```

### 自检原则

- 所有字段**不能为空**或写"待定"
- 如果某项答不上来 → 回到 Step 3 补齐规划
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

- 目标字数：来自 `book_rules.yaml` 的 `chapterWordCount` 或用户指定
- 软区间：目标 ± 10%（如目标 3000，软区间 2700-3300）
- 硬区间：目标 ± 20%（如目标 3000，硬区间 2400-3600）
- 写作时瞄准目标，偏离软区间会在 Step 6 触发长度归一化

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

机械规则检查，LLM 扫描正文后输出问题列表（不自动修复）。

完整规则见 09-post-write-validation.md，简要：

- 禁止句式检测（"不是...而是..."、破折号）
- 疲劳词密度（≤ 1 次/章）
- 转折标记词密度（≤ 1 次/3000 字）
- 连续"了"字（≥ 6 句连续含"了"）
- 段落过长（≥ 2 段超过 300 字）
- 分析术语泄漏（"核心动机"等）
- 本书禁忌违规

### 结果处理

- 无问题 → 继续 Step 7
- 有 ERROR 级问题 → 自动触发一次 spot-fix（局部修复），然后重新 Step 6
- 有 WARNING 级问题 → 报告给用户，由用户决定是否修

### 防无限循环

同一个问题修复 2 次仍未通过 → 停止自动修复，报告给用户人工介入。

---

## Step 7: 审计（可选）

### 触发条件

- 用户写章时明确说"写完后审计" → 自动触发
- 用户说"审计第 N 章" → 独立触发（跳过 Step 1-6）
- 默认情况下：**不自动触发**，用户可在写完后手动触发

### 执行方式

完整流程见 06-audit-system.md。输出结构化审计报告。

### 结果处理

- passed = true → 继续 Step 9
- 有 critical 问题 → 建议用户触发修订（Step 8）
- 只有 warning → 列出建议，用户决定

---

## Step 8: 修订（如需要）

完整流程见 07-revision-modes.md。

简要：根据审计结果选择模式（spot-fix / polish / rewrite / rework / anti-detect），修订后重新 Step 6 校验。

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
BOOK_DIR=~/.inkos/data/books/<书名>
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
