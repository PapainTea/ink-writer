# 用户命令参考

用户用**自然语言**触发命令，下面是各类常用意图与对应的 pipeline 动作。

---

## 1. 写章类

| 用户说 | 动作 | 链接 |
|---|---|---|
| "写第 N 章" | 完整写章流程：Planner → Composer → Writer → Length-normalizer → Auditor → Post-write-validator → Settler → snapshot | [§04](./04-write-pipeline.md) |
| "写下一章" | 同上，N = `chapter index` 里最后一章 + 1 | [§04](./04-write-pipeline.md) |
| "续写" | 接着上次未完成的草稿继续，不新开章 | [§04](./04-write-pipeline.md) |

---

## 2. 审计类

| 用户说 | 动作 | 链接 |
|---|---|---|
| "审计第 N 章" | 单章 Auditor：OOC / 信息越界 / 设定冲突 / 战力崩坏 / 节奏 / 词汇疲劳 | [§06](./06-audit-system.md) |
| "审计全书" | 逐章跑 Auditor，汇总成报告 | [§06](./06-audit-system.md) |
| "检查第 N 章的 X 问题" | 针对性维度检查（例如只跑"战力一致性" / "信息边界"）| [§06](./06-audit-system.md) |

---

## 3. 修订类（[§07](./07-reviser-modes.md)）

| 用户说 | 模式 | 幅度 |
|---|---|---|
| "润色第 N 章" | `polish` | 表达 / 节奏（不动结构）|
| "修第 N 章的 X 问题" | `spot-fix` | 单句或段落定点修复 |
| "改写第 N 章 XX 段落" | `rewrite` | 段落级重组 |
| "重写第 N 章" | `rework` | 整章推翻重生成（回到 snapshots/(N-1) + 跑完整 Writer pipeline）|
| "降低第 N 章 AI 痕迹" | `anti-detect` | 反 AIGC 检测清洗 |

---

## 4. 查询类

| 用户说 | 动作 |
|---|---|
| "当前状态" | 读 `current_state.md`，口头汇报 |
| "列出未回收伏笔" | 读 `pending_hooks.md`，过滤 `状态 != resolved` |
| "列出陈旧伏笔" | 读 `pending_hooks.md`，筛出"最近推进"距当前章 ≥ 10 章的 |
| "第 N 章写了什么" | 读 `chapter_summaries.md` 对应行 |
| "主角现在和谁是敌人" | 读 `current_state.md` 的"当前敌我"字段 |
| "某某角色的信息边界" | 读 `character_matrix.md` 的"信息边界"子表 |
| "最近 N 章的情绪走势" | 读 `emotional_arcs.md` 按章节筛选 |

---

## 5. 管理类

| 用户说 | 动作 | 链接 |
|---|---|---|
| "新建一本书" | Architect 流程（询问书名/题材/平台/主角 → 生成 5 基础文件 → 初始化 3 真相文件 → snapshots/0）| [§12](./12-init-book.md) |
| "回滚到第 N 章" | 从 `snapshots/N/` 恢复 7 个真相文件，删除 > N 的章节正文和 index 条目 | [§10](./10-snapshot-rollback.md) |
| "重建资源账本" | 逐章跑 chapter-analyzer，从正文重抽取 → 合并 → 重写 `particle_ledger.md` | [§11](./11-data-recovery.md) |
| "重建伏笔池" | 同上，针对 `pending_hooks.md` | [§11](./11-data-recovery.md) |
| "重建章节摘要" | 从正文重新抽取 `chapter_summaries.md` | [§11](./11-data-recovery.md) |
| "备份" | `cp -R story/ story.backup-<timestamp>/` | [§10](./10-snapshot-rollback.md) |

---

## 6. 操作原则

- **先确认再动手**：破坏性动作（回滚、rework、重建）前先复述一遍意图，等用户确认
- **先备份再破坏**：任何会覆盖文件的操作，先 `cp -R` 一份 `.backup-<timestamp>/`
- **先读后写**：所有合并操作必须 read → merge → write，不要整体覆盖（否则触发 Bug E 家族）
