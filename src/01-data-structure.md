# 数据目录结构

## 标准布局

每本书的数据存放在 `~/.inkos/data/books/<书名>/` 下，结构固定：

```
~/.inkos/data/books/<书名>/
├── story/                          # 世界状态层（truth files + 基础文件）
│   │
│   ├── 【基础文件（用户手写或 Architect 生成，少改）】
│   ├── story_bible.md              # 世界观设定
│   ├── volume_outline.md           # 卷纲 / 章节大纲
│   ├── book_rules.md               # 本书专属规则（YAML frontmatter + 正文）
│   ├── author_intent.md            # 作者意图（可选）
│   ├── current_focus.md            # 当前聚焦（可选）
│   │
│   ├── 【7 个真相文件（每章结算后更新）】
│   ├── current_state.md            # 当前状态卡（字段键值表）
│   ├── particle_ledger.md          # 资源账本（7 列）
│   ├── pending_hooks.md            # 伏笔池（7 列）
│   ├── subplot_board.md            # 支线进度板（9 列）
│   ├── emotional_arcs.md           # 情感弧线（6 列）
│   ├── character_matrix.md         # 角色交互矩阵（3 子表）
│   ├── chapter_summaries.md        # 章节摘要（8 列）
│   │
│   ├── audits/                     # 审计结果（每章一个 md，Obsidian callout 格式）
│   │   ├── ch-1.md                 # 第 1 章审计
│   │   ├── ch-2.md
│   │   └── ...                     # 详见 §06 审计系统
│   │
│   └── snapshots/                  # 历史快照（只读档案）
│       ├── 0/                      # 开书初始状态（新建书时创建）
│       ├── 1/                      # 写完第 1 章后的状态
│       ├── 2/                      # 写完第 2 章后的状态
│       └── ...                     # 每章一个目录
│           ├── current_state.md    # 快照版本
│           ├── particle_ledger.md
│           ├── pending_hooks.md
│           ├── subplot_board.md
│           ├── emotional_arcs.md
│           ├── character_matrix.md
│           ├── chapter_summaries.md
│           └── audits/             # 该章及之前的审计 md（与 truth files 一并归档）
│               └── ch-N.md
│
└── chapters/                       # 章节正文
    ├── 0001_<标题>.md              # 正文：第一行 `# 第 N 章 <标题>`，文件名也带标题
    ├── 0002_<标题>.md
    ├── ...
    └── index.json                  # 章节索引（含标题、状态、字数等元数据）
```

### 不创建的目录（与原项目差异）

skill 模式不创建以下目录——它们是原项目 pipeline / memory 检索的辅助产物，skill 模式下 LLM 直接读 truth files 完成全部工作：

| 不创建 | 原项目用途 | skill 模式为何不需要 |
|--------|----------|---------------------|
| `story/state/` | 结构化 JSON 事实索引（给 memory.db 做 source of truth） | Markdown truth files 本身就是事实层，无需重复 |
| `story/runtime/` | pipeline 中间产物（chapter intent / context package / rule stack / trace） | skill 模式无 planner/composer 分阶段，没有中间产物 |
| `story/memory.db` | SQLite 事实索引（给 retrieveMemorySelection 做 context 选择） | LLM 直接读 truth files，1M context 放得下 |

如果未来书超长（>100 章）需要 context 检索，可以按需重新引入 memory.db。当前默认不维护。

## 快照语义（重要）

`snapshots/N/` 表示"**写完第 N 章后、当时的累积状态**"，不是"最终结果的副本"。

**硬约束**（任何操作都要遵守）：
1. 绝不向 `snapshots/N/` 写入第 N 章之后才出现的数据
2. 绝不批量用一个最终结果覆盖所有快照
3. 绝不修改 `snapshots/N/` 下的任何文件
4. 恢复/重建时必须逐章"递增生成"每个快照

## chapter index.json 结构

`chapters/index.json` 是 JSON 数组（不是 `{chapters: [...]}` 对象包裹），每个元素代表一章：

```json
[
  {
    "number": 1,
    "title": "<标题>",
    "status": "approved",
    "wordCount": 3240,
    "createdAt": "2026-01-15T12:00:00.000Z",
    "updatedAt": "2026-01-15T12:00:00.000Z",
    "lengthWarnings": []
  }
]
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `number` | int | 章节号 |
| `title` | string | 章节标题（不含"第 X 章"前缀）|
| `status` | enum | `draft` / `audited` / `approved` / `needs_revision`（4 种状态，**用于判断章节是否过审**） |
| `wordCount` | int | 最终字数（按 zh_chars 计数） |
| `createdAt` | ISO timestamp | 首次创建时间 |
| `updatedAt` | ISO timestamp | 最后修订时间 |
| `lengthWarnings` | string[] | 字数超出软/硬区间的警告 |

**注**：审计结果**不在 index.json 内**，而是写入 `story/audits/ch-<N>.md`（详见 §06）。

### status 状态机（判断章节是否过审）

| 状态 | 含义 | 触发 |
|------|------|------|
| `draft` | 初稿，未审计 | 写完 Step 5 但跳过 Step 7 |
| `audited` | 已审计但有未修复 warning | 走完 Step 7 但有 warning 未处理 |
| `approved` | 审计通过/全部修复 | 完整流程通过 |
| `needs_revision` | 审计发现 critical 问题待修 | Step 7 报 critical 后未走 Step 8 |

### 文件名命名约定

- 章节文件命名规则：**4 位章节号 + 下划线 + 标题 + .md**。章节号不足 4 位前面补 0。
  - 第 1 章 → `0001_序章.md`
  - 第 14 章 → `0014_收网.md`
  - 第 150 章 → `0150_xxx.md`
  - 第 1500 章 → `1500_xxx.md`
- 补零目的：让文件按文件名排序时章节顺序自然正确（否则 `1.md, 10.md, 11.md, 2.md` 会乱）
- Truth file 备份（如恢复操作）：`<filename>.backup-<YYYYMMDDhhmmss>`

## 文件命名约定

- 章节文件命名：4 位章节号（不足补 0）+ 下划线 + 标题 + `.md`。例：第 1 章 `0001_序章.md` / 第 14 章 `0014_收网.md` / 第 150 章 `0150_xxx.md`
- 标题中的特殊字符保留（空格、中文标点都可以，文件系统能处理）
- Truth files 文件名全小写 + 下划线，不带 extension 前缀

## 读取优先级

当 LLM 加载 context 时，按此优先级读取：

1. **必读（写章/审计都要）**：current_state.md, story_bible.md, volume_outline.md, book_rules.md
2. **写章必读**：所有 7 个 truth files + 最近 1-2 章正文
3. **审计必读**：被审章节正文 + 前一章正文 + 所有 truth files
4. **修订必读**：被修章节正文 + 审计结果 + current_state + ledger + hooks
