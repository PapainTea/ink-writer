# ink_writer

> 一份 markdown，把多 agent 长篇小说写作系统装进任何 AI CLI 工具。

ink_writer 是一个**纯 prompt 驱动**的写作系统，配合 Claude Code（或 Codex / Cursor 等 AI CLI 工具）使用。它把世界状态、伏笔追踪、角色一致性、审计校验、修订流程等长篇创作必备能力，全部用 markdown 表达出来——零 npm 依赖、零桌面安装包、跨平台。

如果你想严肃地写一本网文（10 万字以上），又不想 LLM 写到第 5 章就忘了第 2 章发生过什么，这个工具是给你的。

---

## 这是什么

**核心价值**：让 AI 写作者像专业编辑团队一样工作。

每写完一章，AI 会自动：
- 追踪资源变动（你的灵石数量、情报权、人情债——都是可验算的）
- 推进/回收伏笔（伏笔池里的每条都有状态、最近推进章节、预期回收章节）
- 更新角色档案、相遇记录、信息边界（谁在哪一章知道了什么）
- 维护章节摘要、情感弧线、支线进度
- 保存当时的快照（写错了可以回滚整章重写）

每章之后你可以让 AI 审计：
- 37 个维度（OOC / 信息越界 / 设定冲突 / 战力崩坏 / 节奏 / 词汇疲劳 ...）
- 输出 markdown 审计报告（Obsidian callout 格式，红黄蓝按严重度高亮）
- 存到 `story/audits/ch-N.md`，可以双链跳转

支持 5 种修订模式：定点修复 / 润色 / 改写 / 重写 / 反检测改写。

---

## 安装（3 步）

### Step 1：自己决定 books 根目录

ink_writer **不强制任何固定路径**。你可以把书籍数据放在任何地方，例如：
- `~/novels/`
- `~/Documents/writing/`
- `~/Projects/my-book/`
- 甚至 iCloud Drive / Dropbox 下的目录

本文档用 `<父目录>/books` 代表你选的根目录。

### Step 2：手动创建书籍目录

```bash
# 假设你决定把 books 放在 ~/novels/
export BOOKS_ROOT=~/novels
mkdir -p $BOOKS_ROOT/<你的书名>/{story,chapters}
mkdir -p $BOOKS_ROOT/<你的书名>/.claude

# 把 ink_writer 的 CLAUDE.md 复制到这本书的 .claude/ 目录
cp /path/to/ink_writer/dist/CLAUDE.md \
   $BOOKS_ROOT/<你的书名>/.claude/CLAUDE.md
```

### Step 3：在书籍项目下打开 Claude Code

```bash
cd $BOOKS_ROOT/<你的书名>
claude
```

第一次对话时 Claude 会主动问你 books 根目录在哪，告诉它绝对路径即可。

### Step 4：用自然语言写作

直接说话即可，Claude 会自动加载 instruction 并按规则执行。

---

## 跨平台支持

| 平台 | instruction 文件 | 放在哪里 |
|------|----------------|---------|
| **Claude Code** | `CLAUDE.md` | `<书籍项目>/.claude/CLAUDE.md`（或项目根）|
| **Codex CLI** | `AGENTS.md` | `<书籍项目>/AGENTS.md` |
| **Cursor** | `.cursorrules` | `<书籍项目>/.cursorrules` |
| **Windsurf** | `.windsurfrules` | `<书籍项目>/.windsurfrules` |

> **注**：当前 `dist/` 下只有 `CLAUDE.md`。`AGENTS.md` 等其他平台版本由对应平台的 AI 自己生成，或参考 `src/` 模块自行拼接。

---

## 用法示例

### 新建一本书

```
你：我想写一本玄幻，主角是个被宗门赶出来的废柴，意外觉醒了能"借用别人战斗经验"的能力，目标是回去打脸的那种爽文

Claude：[问几个补充问题：书名、平台口味、字数偏好]
       [产出 5 个基础文件：story_bible / volume_outline / book_rules / current_state / pending_hooks]
       [初始化空真相文件 + snapshots/0/]
       [告诉你"准备好就说写第 1 章"]
```

### 写章

```
你：写第 1 章

Claude：[加载所有 truth files + 大纲 + 上一章正文]
       [Step 1-11 完整流程：规划 → 自检 → 写正文 → 校验 → 审计可选 → 结算 → 快照 → 写文件]
       [产出 chapters/0001_<标题>.md + 更新 7 个真相文件 + snapshots/1/]
```

### 审计

```
你：审计第 14 章

Claude：[加载被审章节正文 + 前一章 + 所有 truth files + 大纲]
       [按 37 维度逐项检查：OOC / 信息越界 / 设定冲突 / 节奏 / 词汇疲劳 / 大纲偏离 ...]
       [输出审计报告到 story/audits/ch-14.md（Obsidian callout 格式）]
       [报告 critical / warning / info 各几条]
```

### 修订（5 种模式）

```
你：润色第 14 章                    → polish 模式（只改表达不改事实）
你：修第 14 章的破折号问题          → spot-fix 模式（定点修复）
你：改写第 14 章的开头              → rewrite 模式（段落重组）
你：重写第 14 章                    → rework 模式（恢复 ch13 快照 + 整章重写）
你：降低第 14 章 AI 痕迹            → anti-detect 模式（口语化 + 句式破壁）
```

### 查询

```
你：当前状态                        → 读 current_state.md 汇报
你：列出未回收伏笔                  → 读 pending_hooks.md 过滤
你：列出陈旧伏笔                    → 超过 10 章未推进的
你：第 5 章写了什么                 → 读 chapter_summaries.md 对应行
```

### 回滚

```
你：回滚到第 12 章                  → 从 snapshots/12/ 恢复 + 删除 ch13+ 正文
```

---

## 数据目录结构

```
<父目录>/books/<书名>/
├── story/                          # 世界状态层
│   ├── story_bible.md              # 世界观（你手写或 AI 生成，少改）
│   ├── volume_outline.md           # 卷纲 / 章节大纲
│   ├── book_rules.md               # 本书专属规则（YAML + 正文）
│   │
│   ├── current_state.md            # 当前状态卡（每章覆盖）
│   ├── particle_ledger.md          # 资源账本（7 列含事件ID）
│   ├── pending_hooks.md            # 伏笔池（7 列）
│   ├── subplot_board.md            # 支线进度板（9 列）
│   ├── emotional_arcs.md           # 情感弧线（6 列）
│   ├── character_matrix.md         # 角色交互矩阵（3 子表）
│   ├── chapter_summaries.md        # 章节摘要（8 列）
│   │
│   ├── audits/                     # 审计结果（每章一个 md，Obsidian callout）
│   │   ├── ch-1.md
│   │   └── ch-N.md
│   │
│   └── snapshots/                  # 历史快照
│       ├── 0/                      # 开书初始
│       ├── 1/
│       └── N/                      # 写完第 N 章后的状态（含当时的 audits/）
│
└── chapters/                       # 章节正文
    ├── 0001_<标题>.md              # 文件名带标题，正文第一行也是 `# 第 N 章 <标题>`
    ├── 0002_<标题>.md
    └── index.json                  # 章节索引（number/title/status/wordCount/... 元数据）
```

---

## 推荐配套工具

ink_writer 自身只是一份 markdown，但配合下面的工具体验更好：

| 工具 | 用途 |
|------|------|
| **Claude Code / Codex CLI / Cursor** | 写作主战场，自然语言交互 |
| **Obsidian** | 浏览 truth files、审计 callout 高亮、章节双链 |
| **VSCode** | 编辑 markdown / 看 chapters/index.json 元数据 |
| **Git** | 版本管理（章节正文 + truth files + snapshots 全 git） |

---

## 我的写作流程长什么样

一个典型写作 session：

1. `cd` 到书籍目录，打开 Claude Code
2. 说"看一下当前状态"——Claude 读 current_state.md 汇报
3. 说"写第 N 章"——Claude 走完 11 步流程产出新章
4. 看一眼正文，不满意就说"重写第 N 章"或"改写第 N 章某段"
5. 满意后说"审计第 N 章"——Claude 给审计报告
6. 根据审计修订（多数 warning 可以不改，critical 必修）
7. 关掉 Claude Code，去喝杯咖啡

---

## 设计哲学

### 1. 真相文件是事实，对话是过程

7 个真相文件（current_state / particle_ledger / pending_hooks / subplot_board / emotional_arcs / character_matrix / chapter_summaries）是**世界状态的唯一持久层**。LLM 凭这些文件做事，不凭记忆。

### 2. 流程步骤是硬约束，但 LLM 不一定 100% 遵守

写章流程定义了 11 步（规划 → 写 → 校验 → 审计 → 修订 → 结算 → 快照 → 落盘）。LLM 大概率会按步骤走，但不保证。所以：
- truth files 行数永远只增不减（即使 LLM 漏了一步，下次也能从文件状态推断）
- 快照是回滚保险
- 审计报告独立成文件，便于人工 review

### 3. 不做 UI

CLI 工具天然支持：实时输出、文件 diff、版本控制、跨平台。UI 是 bug 主要来源，砍掉 UI = 消除整个 bug 面。如果你想可视化浏览，用 Obsidian。

### 4. 平台无关源 + 平台特定生成

`src/` 模块用能力级别描述（"读取文件""定点修改""执行 shell"），不绑定具体工具名。生成步骤把能力描述替换为平台具体工具。

---

## 局限性

诚实说：

- **依赖大 context 模型**：当前 Claude Opus 4.6（1M）/ GPT-5.4 都满足，但小模型可能塞不下所有 truth files
- **LLM 不保证 100% 遵守流程**：上面提到了，需要 golden-case 验证。如果你发现 LLM 经常跳步骤，可以更具体地说"严格按流程走"
- **超长书（>100 章）可能需要额外索引**：当前不创建 memory.db，1M context 应该够，但极限场景未验证
- **没有 UI**：如果你必须用图形界面，这个工具不适合你

---

## 项目状态

- ✅ 14 个源模块完成（src/）
- ✅ Python 兜底脚本（merge-truth.py）
- ✅ 拼接生成器（generate.py）
- ✅ Claude Code 版（dist/CLAUDE.md，2622 行）
- ⬜ Codex CLI 版（dist/AGENTS.md，待 Codex 自行生成）
- ⬜ Golden-case 验证完成（写章 / 审计 / 修订三任务在 2 本书上跑稳）

详细进度看 `CLAUDE.md`（项目内部开发指引）。

---

## 来源

ink_writer 的前身是 [PapainTea/inkos](https://github.com/PapainTea/inkos)（TypeScript monorepo），从中提取核心 prompt 算法 + truth file schema 而成。如果你对实现细节感兴趣，可以去原仓库翻 `packages/core/src/agents/` 下的 `.ts` 文件——所有创作规则、审计维度、修订模式的源头都在那里。

---

## 许可

待定。

---

*版本：v1.0 | 2026-04-13*
