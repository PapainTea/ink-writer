# 用户命令参考

用户用**自然语言**触发命令。下面的路由表定义每个意图触发时 **LLM 必须先 Read 哪个按需模块**，再按该模块流程执行。

---

## §13.0 按需加载模块（关键协议）

**核心 CLAUDE.md 只含基础规则（系统角色 / 数据目录 / 机械规则 / 硬性禁令 / 命令路由）**。写章、审计、修订、新建书、回滚这五大流程的**完整定义不在核心里**，位于：

```
<booksRoot>/.claude-modules/
├── write.md        # 写章流程（§02+§03+§04+§05+§08+§11）
├── audit.md        # 审计流程（§02+§06）
├── revise.md       # 修订流程（§02+§07）
├── init.md         # 新建书流程（§12）
└── snapshot.md     # 回滚恢复流程（§10）
```

`<booksRoot>` 从 `.ink-writer.yaml` 读取（见 §00 启动流程）。

### 强制原则（违反即失败）

**当用户触发非查询类意图时，你必须先用 Read 工具读取对应模块的完整内容，再按该模块流程执行。** 不可凭记忆执行写章 / 审计 / 修订 / 新建书 / 回滚——核心 CLAUDE.md 不含这些流程的完整定义，靠记忆会遗漏步骤（例如跳过 Step 7 审计、跳过 Step 10 快照、跳过场景级字数预算）。

### 意图 → 模块映射

| 用户意图 | 触发词示例（按语义判断，不是完整清单）| 先 Read 哪个 |
|---------|----------------------------------|-------------|
| 写新章 | "写第 N 章" / "写下一章" / "续写" | `.claude-modules/write.md` |
| 审计 | "审计第 N 章" / "审稿" / "check chapter N" / "检查 X 问题" / "审计全书" | `.claude-modules/audit.md` |
| 修订 | "润色" / "修第 N 章的 X" / "spot-fix" / "改写" / "重写"（rework）/ "反检测" / "降低 AI 痕迹" | `.claude-modules/revise.md` |
| 新建书 | "新建一本书" / "建一本新书" / "我想写一本 XX" | `.claude-modules/init.md` |
| 回滚 / 恢复 | "回滚到第 N 章" / "备份" / "重建 ledger" / "重建 hooks" / "重建章节摘要" | `.claude-modules/snapshot.md` |
| **查询类（不 Read 任何模块）** | "当前状态" / "列出未回收伏笔" / "列出陈旧伏笔" / "第 N 章写了什么" / "主角现在和谁是敌人" / "某角色的信息边界" / "最近 N 章情绪走势" | **核心已足够**，直接按下表读 truth files 汇报 |

---

## §13.1 查询类（核心内置，不 Read 模块）

| 用户说 | 动作 |
|---|---|
| "当前状态" | 读 `current_state.md`，口头汇报 |
| "列出未回收伏笔" | 读 `pending_hooks.md`，过滤 `状态 != resolved` |
| "列出陈旧伏笔" | 读 `pending_hooks.md`，筛出"最近推进"距当前章 ≥ 10 章的 |
| "第 N 章写了什么" | 读 `chapter_summaries.md` 对应行 |
| "主角现在和谁是敌人" | 读 `current_state.md` 的"当前敌我"字段 |
| "某某角色的信息边界" | 读 `character_matrix.md` 的"信息边界"子表 |
| "最近 N 章的情绪走势" | 读 `emotional_arcs.md` 按章节筛选 |

**查询类不修改任何文件**，只汇报信息。

---

## §13.2 写章类 → 先 Read `.claude-modules/write.md`

| 用户说 | 动作 |
|---|---|
| "写第 N 章" | 完整写章流程：Planner → PRE_WRITE_CHECK → Writer → Post-write-validator → Auditor → Settler → snapshot → verify |
| "写下一章" | 同上，N = `chapter index` 里最后一章 + 1 |
| "续写" | 接着上次未完成的草稿继续，不新开章 |

详细 11+1 步流程见 `.claude-modules/write.md`（§04 部分）。

---

## §13.3 审计类 → 先 Read `.claude-modules/audit.md`

| 用户说 | 动作 |
|---|---|
| "审计第 N 章" | 单章 Auditor：37 维度（OOC / 信息越界 / 设定冲突 / 节奏 / 词汇疲劳 / 大纲偏离 等）|
| "审计全书" | 逐章跑 Auditor，汇总成报告 |
| "检查第 N 章的 X 问题" | 针对性维度检查 |

审计结果落盘到 `story/audits/ch-<N>.md`，Obsidian callout 格式。

---

## §13.4 修订类 → 先 Read `.claude-modules/revise.md`

| 用户说 | 模式 | 幅度 |
|---|---|---|
| "润色第 N 章" | `polish` | 表达 / 节奏（不动结构）|
| "修第 N 章的 X 问题" | `spot-fix` | 单句或段落定点修复 |
| "改写第 N 章 XX 段落" | `rewrite` | 段落级重组 |
| "重写第 N 章" | `rework` | 整章推翻重生成（回到 snapshots/(N-1) + 跑完整 Writer pipeline）|
| "降低第 N 章 AI 痕迹" | `anti-detect` | 反 AIGC 检测清洗 |

---

## §13.5 管理类

### 新建书 → 先 Read `.claude-modules/init.md`

"新建一本书" / "建一本新书" / "我想写一本 XX" → 对话采集书名/题材/主角/梗概，产出 5 个基础文件 + 4 个空真相文件 + snapshots/0/。

### 回滚 / 数据恢复 → 先 Read `.claude-modules/snapshot.md`

| 用户说 | 动作 |
|---|---|
| "回滚到第 N 章" | 从 `snapshots/N/` 恢复 7 个真相文件，删除 > N 的章节正文和 index 条目 |
| "重建资源账本" / "重建 ledger" | 逐章从正文重抽取 → 合并 → 重写 `particle_ledger.md`（调 `scripts/merge-truth.py`）|
| "重建伏笔池" / "重建 hooks" | 同上，针对 `pending_hooks.md` |
| "重建章节摘要" | 从正文重新抽取 `chapter_summaries.md` |
| "备份" | `cp -R story/ story.backup-<timestamp>/` |

---

## §13.6 操作原则

- **先确认再动手**：破坏性动作（回滚、rework、重建）前先复述一遍意图，等用户确认
- **先备份再破坏**：任何会覆盖文件的操作，先 `cp -R` 一份 `.backup-<timestamp>/`
- **先读后写**：所有合并操作必须 read → merge → write，不要整体覆盖
- **先 Read 模块再执行**（§13.0 强制原则）：非查询类意图必须先加载对应按需模块
