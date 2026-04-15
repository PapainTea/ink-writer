# ink.skill 迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ink_writer 从"markdown instruction 分发 + 本地 Python 脚本"形态，迁移为**单一跨平台 skill（ink.skill）**，同时保留旧形态给现有用户继续使用。

**Architecture:**
- skill 源放在 `<ink_writer>/ink-skill-dev/`（开发期）→ 稳定后 push 到 `PapainTea/ink-skill` → 用户 `git clone` 到 `<父目录>/books/ink-skill/` → 各平台 skill 路径软链过去
- 每本书目录含 2 个动态文件：各平台的 init（`CLAUDE.md`/`AGENTS.md`/`GEMINI.md` 等，作者所在平台的 agent 自写）+ `PROGRESS.md`（skill 维护）
- 迁移 & 新建 & 跨平台自部署 & PROGRESS.md 维护 **全部内置在 skill 中**，不再需要外部 `install.py`/`new-book.py` 脚本

**Tech Stack:** Markdown + YAML frontmatter + Python3（stdlib only）+ git CLI

**Scope clarification:** V1（激活可靠性）+ V2（书识别）+ V3（跨会话续接）一次性做进 v1

---

## 阶段 0：施工前置

### Task 0.1: 确认仓库同步 & 建开发目录

**Files:**
- Create: `ink-skill-dev/` (新目录)

- [ ] **Step 1: 确认 ink_writer 主仓库干净**

```bash
cd /Users/admin/Codex/Project/Own/ink_writer
git status  # 期望 clean
git log --oneline origin/main..HEAD  # 期望 empty
```

- [ ] **Step 2: 创建开发目录骨架**

```bash
mkdir -p ink-skill-dev/{reference,scripts,templates,docs}
```

- [ ] **Step 3: 把 ink-skill-dev 加到 .gitignore OR 把它作为 submodule**

决策：**不加 submodule**，先在 ink_writer 仓库内同步开发，稳定后整体迁移到 ink-skill 独立仓库。`ink-skill-dev/` 会被正常 track 在 ink_writer 仓库里（作为 v2 开发分支的一部分）。

```bash
# 不改 .gitignore
```

- [ ] **Step 4: 提交初始目录**

```bash
git add ink-skill-dev/
echo "# ink-skill-dev\n\nink.skill 开发目录。稳定后整体迁移到 PapainTea/ink-skill 独立仓库。" > ink-skill-dev/README.md
git add ink-skill-dev/README.md
git commit -m "chore: scaffold ink-skill-dev folder for skill migration v2 work"
```

### Task 0.2: 预检 test fixture 兼容性（应对 R10）

**Files:**
- Check: `tests/fixtures/test-book/`

- [ ] **Step 1: 确认 fixture 存在且当前 verify-chapter.py 能跑**

```bash
ls tests/fixtures/test-book/chapters/ tests/fixtures/test-book/story/
cd tests/fixtures/test-book && python3 ../../../scripts/verify-chapter.py 1 ; cd -
```

期望：无 error（或按 fixture 预期 exit code）。

- [ ] **Step 2: 记录现状到 plan 备注**

如果 fixture 不存在或 verify 跑不通，在这里加一个新任务"Task 0.3: 修复/重建 fixture"，阻塞阶段 5 开始。

---

## 阶段 1：SKILL.md 骨架 + 触发词设计

### Task 1.1: 写 SKILL.md 第一版（最小可触发版本）

**Files:**
- Create: `ink-skill-dev/SKILL.md`

- [ ] **Step 1: 起 frontmatter 和触发策略**

SKILL.md frontmatter：

```yaml
---
name: ink
description: |
  ink.skill — 跨平台小说写作 skill。Use when user mentions: ink（大小写不敏感）、ink 初始化、ink 迁移、ink 安装、写书、写小说、新建书、新建章节、写第 N 章、续写、连写、连写 N 章、审计章节、润色章节、结算章节、followup、伏笔、粒子账本、人物矩阵、世界观、章节大纲。本 skill 独占覆盖所有长篇小说创作流程（架构 / 写作 / 审计 / 修订 / 结算 / 快照），涵盖 37 维度审计 / 5 种修订模式 / 7 个 truth files 维护。不要同时触发 writing-skills / doc-coauthoring / brainstorming。用户消息含 "ink" 字样必须触发本 skill。
---
```

- [ ] **Step 2: 写 SKILL.md body 核心段（参考 src/00-system-role.md + src/13-commands.md）**

Body 至少包含：
1. 系统角色（你是小说写作 agent，非通用助手）
2. 激活自检 - **四步**：
   - (a) 检查 cwd 是否在某本书根（含 `chapters/` 和 `story/`）
   - (b) **若 cwd 不是书根（如在 `books/` 父目录）**：强制询问作者"你要在哪本书上操作？"，作者回答前不执行任何写操作（应对 R7 多书歧义）
   - (c) Read `<书根>/PROGRESS.md`；不存在 → 走 init bootstrap
   - (d) Read PROGRESS.md 中"📚 真相文件索引"段，按本次任务需要 Read 对应 truth files
3. 路由表：意图 → 按需加载 reference/ 下哪个模块（write / audit / revise / init / snapshot / truth-schema）
4. PROGRESS.md 读写协议（覆盖/追加规则，见阶段 3）
5. 跨平台 init 文件生成规则（见阶段 4）
6. 迁移老书触发词和流程（见阶段 6）
7. 强制律：用户消息含 "ink"（大小写不敏感）必触发本 skill；不得同时激活 writing-skills / doc-coauthoring / brainstorming

- [ ] **Step 3: 大小上限检查（应对 R9）**

```bash
wc -c ink-skill-dev/SKILL.md
# 期望 < 15000 字节（15k chars）
# 如果超出：把详细规则放 reference/，SKILL.md 只留协议和路由
```

- [ ] **Step 4: commit**

```bash
git add ink-skill-dev/SKILL.md
git commit -m "feat(ink-skill): add SKILL.md skeleton with trigger keywords + activation protocol"
```

### Task 1.2: 验证 SKILL.md 能被识别

- [ ] **Step 1: 软链到 Claude Code skills 目录临时测试**

```bash
ln -sf /Users/admin/Codex/Project/Own/ink_writer/ink-skill-dev ~/.claude/skills/ink-dev
```

- [ ] **Step 2: 在新会话说"ink 测试一下"，确认 skill 被激活**

期望：触发 `ink-dev` skill。若未触发，回到 Task 1.1 调整 description 的触发词密度。

- [ ] **Step 3: 清掉临时软链**

```bash
rm ~/.claude/skills/ink-dev
```

---

## 阶段 2：reference/ 模块（从 src/ 移植）

### Task 2.1: 核心方法论模块（写作层）

**Files:**
- Create: `ink-skill-dev/reference/write.md` ← 合并自 `src/04-write-pipeline.md` + `src/05-writing-rules.md` + `src/02-truth-schema.md`（相关段）

- [ ] **Step 1: 复制原文 + 去掉本项目特定的开发元信息**

```bash
cat src/04-write-pipeline.md src/05-writing-rules.md > ink-skill-dev/reference/write.md
```

- [ ] **Step 2: 检查并移除任何具体书籍名泄漏**

```bash
grep -nE "顾悬|周巡事|镜源|长夜|西角|乙九|候潮人|锁符|顾家" ink-skill-dev/reference/write.md
# 期望 empty
```

- [ ] **Step 3: 在文件头加 skill-context 说明**

```markdown
# write — 章节写作参考

> 本模块由 ink.skill 在用户意图为"写章节 / 续写 / 连写 / 新建章节"时 Read。
> 前置：先读 `<book_root>/PROGRESS.md` 获取当前章号和 followup。
```

- [ ] **Step 4: commit**

```bash
git add ink-skill-dev/reference/write.md
git commit -m "feat(ink-skill): port write pipeline + writing rules into reference/write.md"
```

### Task 2.2: 审计模块

**Files:**
- Create: `ink-skill-dev/reference/audit.md` ← 移植自 `src/06-audit-system.md` + `src/09-post-write-validation.md` + `src/core-hard-bans.md`

- [ ] **Step 1: 合并源文件**

```bash
cat src/06-audit-system.md src/09-post-write-validation.md src/core-hard-bans.md > ink-skill-dev/reference/audit.md
```

- [ ] **Step 2: 书名泄漏检查（同 Task 2.1 Step 2）**

- [ ] **Step 3: 加 skill-context 头**

```markdown
# audit — 章节审计参考

> 本模块由 ink.skill 在用户意图为"审计章节"时 Read。
> 输出：`<book_root>/story/audits/ch-N.md`（Obsidian callout 格式），同时回填 `PROGRESS.md` 的 followup 段
```

- [ ] **Step 4: commit**

```bash
git add ink-skill-dev/reference/audit.md
git commit -m "feat(ink-skill): port audit system into reference/audit.md"
```

### Task 2.3: 修订模块

**Files:**
- Create: `ink-skill-dev/reference/revise.md` ← 移植自 `src/07-revision-modes.md`

- [ ] **Step 1: 复制**

```bash
cp src/07-revision-modes.md ink-skill-dev/reference/revise.md
```

- [ ] **Step 2: 书名检查 + skill-context 头**

```markdown
# revise — 章节修订参考

> 本模块由 ink.skill 在用户意图为"润色 / 修订 / 重写 / 扩写 / 压缩"时 Read。
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/reference/revise.md
git commit -m "feat(ink-skill): port revision modes into reference/revise.md"
```

### Task 2.4: 初始化模块

**Files:**
- Create: `ink-skill-dev/reference/init.md` ← 移植自 `src/12-init-book.md` + `src/03-foundation-files.md`

- [ ] **Step 1: 合并 + 调整语境（原来是"作者对话新建书"，现在是 "skill 触发 ink 初始化"）**

```bash
cat src/12-init-book.md src/03-foundation-files.md > ink-skill-dev/reference/init.md
```

- [ ] **Step 2: 改写开头，强调"skill 内置流程，不再外跑脚本"**

```markdown
# init — 新建书 / 迁移老书参考

> 本模块由 ink.skill 在用户意图为"新建书 / ink 迁移 / ink 初始化"时 Read。
> **关键区别**：
> - 新建书：从 `templates/` 复制骨架 + 作者对话填充 5 个基础文件
> - 迁移老书：检测 `index.json` + `current_state.md` 存在 → 自动补齐 PROGRESS.md + init 文件
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/reference/init.md
git commit -m "feat(ink-skill): port init + foundation files into reference/init.md"
```

### Task 2.5: 快照模块

**Files:**
- Create: `ink-skill-dev/reference/snapshot.md` ← 移植自 `src/10-snapshot-rollback.md` + `src/11-hook-governance.md` + `src/08-settlement.md`

- [ ] **Step 1: 合并**

```bash
cat src/10-snapshot-rollback.md src/11-hook-governance.md src/08-settlement.md > ink-skill-dev/reference/snapshot.md
```

- [ ] **Step 2: skill-context 头**

```markdown
# snapshot — 快照、结算、伏笔治理参考

> 本模块由 ink.skill 在用户意图为"章节结算 / 创建快照 / 回滚 / 查伏笔"时 Read。
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/reference/snapshot.md
git commit -m "feat(ink-skill): port snapshot + settlement + hook governance into reference/snapshot.md"
```

### Task 2.6: Truth schema 模块（独立，多个模块共享）

**Files:**
- Create: `ink-skill-dev/reference/truth-schema.md` ← 直接复制 `src/02-truth-schema.md`

- [ ] **Step 1: 复制 + 头**

```bash
cp src/02-truth-schema.md ink-skill-dev/reference/truth-schema.md
```

加头：

```markdown
# truth-schema — 7 个真相文件的 schema 参考

> 本模块由 ink.skill 在任何需要读写 truth files（character_matrix / worldbook / particle_ledger / chapter_summaries / current_state / foreshadow / timeline）时 Read。
```

- [ ] **Step 2: 书名泄漏检查**

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/reference/truth-schema.md
git commit -m "feat(ink-skill): port truth-schema reference"
```

---

## 阶段 3：PROGRESS.md 设计与协议

### Task 3.1: 设计 PROGRESS.md 模板

**Files:**
- Create: `ink-skill-dev/templates/PROGRESS.template.md`

- [ ] **Step 1: 写模板（含 5 段，明确覆盖/追加标识）**

```markdown
# 📖 {{book_name}} 进度

> 本文件由 ink.skill 自动维护。作者笔记段（最后一段）永不被覆盖。

## 🎯 当前状态  <!-- replace-on-update -->

- **最新已批准**：ch{{last_approved_chapter}}（{{word_count}} 字，{{approved_date}}）
- **下一章**：ch{{next_chapter}}
- **最近操作**：{{last_action_timestamp}} · {{last_action_summary}}
- **书根目录**：{{book_root_abs_path}}

## 📌 活跃 followup  <!-- replace-on-update; 从 story/audits/ 重算 -->

<每次 skill 动作后根据所有 audits/ch-*.md 里 severity=followup 的条目重建，已解决的移除>

- [ ] ch14 师门誓言伏笔需在 ch17-18 回收（来源：ch15 audit）
- [ ] 第二卷起点考虑 ch20

## 📚 真相文件索引（读取提示）  <!-- replace-on-update -->

> skill 每次激活必读本段，然后根据任务按需 Read 对应 truth file。

| 文件 | 位置 | 什么时候读 |
|------|------|------------|
| 角色档案 | `story/character_matrix.md` | 写章前、审计"人物一致性"维度 |
| 世界观设定 | `story/worldbook.md` | 写涉及设定的章节前 |
| 粒子账本 | `story/particle_ledger.md` | 写有物品/资源变动的场景前、审计"资源一致性" |
| 章节摘要 | `story/chapter_summaries.md` | 写章前检查前情 |
| 当前状态卡 | `story/current_state.md` | 每次激活 |
| 伏笔记录 | `story/foreshadow.md` | 写章前检查待回收伏笔 |
| 时间线 | `story/timeline.md` | 写涉及时间推进的场景前 |

## 📜 操作时间线  <!-- append-only; 最多保留 20 条，溢出归档到 story/progress-archive.md -->

- {{ts1}} · {{action1}}
- {{ts2}} · {{action2}}

## ✍️ 作者笔记（skill 不修改）  <!-- never-touched -->

<作者在此自由记笔记，skill 永不读写本段>
```

- [ ] **Step 2: commit**

```bash
git add ink-skill-dev/templates/PROGRESS.template.md
git commit -m "feat(ink-skill): add PROGRESS.md template with section-level update protocol"
```

### Task 3.2: 在 SKILL.md 中规定 PROGRESS.md 读写协议

**Files:**
- Modify: `ink-skill-dev/SKILL.md`

- [ ] **Step 1: 在 SKILL.md 加一段"PROGRESS.md 维护协议"**

```markdown
## PROGRESS.md 维护协议

**激活时**：先 Read `<book_root>/PROGRESS.md`。不存在 → 走 init 流程（见 reference/init.md）。

**更新时机**：每次 skill 动作完成后（写章 / 审计 / 修订 / 结算）。

**段级规则**：
- 🎯 当前状态：**每次完全重写**
- 📌 活跃 followup：**每次从 story/audits/ 重算**
- 📚 真相文件索引：**仅在 init 或作者手动要求刷新时重写**
- 📜 操作时间线：**追加一行**，超过 20 条时把最老一行移到 `story/progress-archive.md`
- ✍️ 作者笔记：**永不读写**（遇到本段标题后全部跳过）

**容错**：遇到缺段的旧版 PROGRESS.md，按缺段补默认值，**不报错**。
```

- [ ] **Step 2: commit**

```bash
git add ink-skill-dev/SKILL.md
git commit -m "feat(ink-skill): define PROGRESS.md update protocol in SKILL.md"
```

---

## 阶段 4：跨平台 init 文件生成（每平台 agent 自写）

### Task 4.1: 规定 init 文件生成规则

**Files:**
- Modify: `ink-skill-dev/SKILL.md`

- [ ] **Step 1: 在 SKILL.md 加"init 文件生成规则"段**

```markdown
## 跨平台 init 文件生成

**触发**：用户在某平台 agent 中首次对某本书说"ink 初始化"或 skill 检测到 init 文件缺失时。

**规则**：
- 当前平台是 Claude Code → skill 让当前 Claude 生成 `CLAUDE.md`（按 Claude Code 的 CLAUDE.md 约定）
- 当前平台是 Codex → 生成 `AGENTS.md`
- 当前平台是 Gemini CLI → 生成 `GEMINI.md`
- 当前平台是 Cursor → 生成 `.cursorrules`
- 不识别的平台 → 生成通用 `AGENT_INSTRUCTIONS.md`

**每平台 agent 自写**：由当前激活的 agent 用它熟悉的格式生成。**不跨平台预生成**。

**幂等性**：init 文件已存在 → **不覆盖**（作者可能有自定义内容）。只在缺失时生成。

**init 文件内容骨架**（各平台略有差异，但共同字段）：
- 本目录是 ink.skill 管理的小说书籍项目
- 书名：{{book_name}}
- 激活 ink skill 的触发词：写书 / 新建章节 / 审计章节 等
- PROGRESS.md 位置：`./PROGRESS.md`

**自动改名**：激活时检测 init 文件中记录的 `book_name` 或路径 vs 当前目录名/路径不一致 → 更新 init 文件 + PROGRESS.md，**不报错**。
```

- [ ] **Step 2: commit**

```bash
git add ink-skill-dev/SKILL.md
git commit -m "feat(ink-skill): spec cross-platform init file generation rules"
```

### Task 4.2: 各平台 init 文件模板

**Files:**
- Create: `ink-skill-dev/templates/init/CLAUDE.md.template`
- Create: `ink-skill-dev/templates/init/AGENTS.md.template`
- Create: `ink-skill-dev/templates/init/GEMINI.md.template`
- Create: `ink-skill-dev/templates/init/cursorrules.template`

- [ ] **Step 1: 写 CLAUDE.md 模板（含强制激活祈使句）**

内容（写入 `ink-skill-dev/templates/init/CLAUDE.md.template`）：

```markdown
# {{book_name}} · ink.skill 书籍项目

本目录由 ink.skill 管理。

**必须执行**：进入本目录的任何对话，在回应用户前，**先调用 ink skill**（即使用户消息不含显式触发词如"写书"、"ink"）。ink skill 内置所有小说创作流程、真相文件维护规则、PROGRESS.md 更新协议。

- 进度文件：`./PROGRESS.md`（每次 skill 动作后自动更新）
- 真相文件：`./story/`
- 章节：`./chapters/`
```

- [ ] **Step 2: 写 AGENTS.md 模板**（Codex CLI 读取 AGENTS.md 作项目 instruction）

内容（`ink-skill-dev/templates/init/AGENTS.md.template`）：

```markdown
# {{book_name}} — ink.skill 书籍项目

本目录是 ink.skill 管理的小说写作项目。

**必须执行**：在本目录的任何对话中，回应前**先调用 ink skill**（名为 `ink` 的 skill，应由当前 agent 平台从其 skills 目录加载，具体路径因平台而异），即使用户未提及显式触发词。ink skill 包含所有创作、审计、修订、结算流程。

- 进度：`./PROGRESS.md`
- 真相文件：`./story/{character_matrix,worldbook,particle_ledger,chapter_summaries,current_state,foreshadow,timeline}.md`
- 章节：`./chapters/`
```

- [ ] **Step 3: 写 GEMINI.md 模板**（Gemini CLI 读取 GEMINI.md）

内容（`ink-skill-dev/templates/init/GEMINI.md.template`）：

```markdown
# {{book_name}} — ink.skill 书籍项目

本目录由 ink.skill 管理的小说写作流程驱动。

**必须执行**：本目录的所有对话，回应前**先激活 ink skill**（不论用户是否使用显式触发词如"写书"、"ink"）。ink skill 定义了所有创作、审计、修订、结算规则。

- 进度与续接：`./PROGRESS.md`
- 真相文件（永远不要让正文与此冲突）：`./story/`
- 章节：`./chapters/`（4 位章号_标题.md 命名）
```

- [ ] **Step 4: 写 .cursorrules 模板**（Cursor 读取 .cursorrules）

内容（`ink-skill-dev/templates/init/cursorrules.template`）：

```
本目录是 ink.skill 管理的小说写作项目（书名：{{book_name}}）。

**必须**：所有对话回应前，先调用 ink skill（无论用户是否用显式触发词）。

步骤：
1. 先读 ./PROGRESS.md 获取当前进度和 followup
2. 按需读 ./story/ 下真相文件（character_matrix / worldbook / particle_ledger / chapter_summaries / current_state / foreshadow / timeline）
3. 章节写入 ./chapters/（命名：4 位章号_标题.md）
4. 每次动作后更新 ./PROGRESS.md（🎯当前状态 覆盖 / 📜操作时间线 追加）

ink.skill 完整说明：https://github.com/PapainTea/ink-skill
```

- [ ] **Step 5: commit**

```bash
git add ink-skill-dev/templates/init/
git commit -m "feat(ink-skill): add per-platform init file templates"
```

### Task 4.3: templates/ 下的新建书骨架

**Files:**
- Create: `ink-skill-dev/templates/book-skeleton/` （整个目录结构）

- [ ] **Step 1: 建骨架目录**

```bash
mkdir -p ink-skill-dev/templates/book-skeleton/{chapters,story/audits,snapshots/0}
```

- [ ] **Step 2: 拷贝 5 个基础文件模板 + 4 个空 truth file 模板**

从现有 `scripts/new-book.py` 逻辑里提取模板内容，放进 `templates/book-skeleton/story/`：
- `character_matrix.md`（含 3 子表头）
- `worldbook.md`（含章节占位）
- `particle_ledger.md`（含 7 列表头）
- `chapter_summaries.md`
- `current_state.md`（含 `# 当前状态` 标题）
- `foreshadow.md`
- `timeline.md`

- [ ] **Step 3: `book_rules.yaml` 模板（含 length/hardRules/pipeline 三块）**

```yaml
# book_rules.yaml 模板：从 src/03-foundation-files.md 和现有镜源书 rules 提取
```

- [ ] **Step 4: commit**

```bash
git add ink-skill-dev/templates/book-skeleton/
git commit -m "feat(ink-skill): add new-book skeleton templates (5 base + 7 truth + snapshots/0)"
```

---

## 阶段 5：scripts/ 移植 + 加 --book-root 参数

### Task 5.1: verify-chapter.py 直接移植（签名已书感知）

**Files:**
- Create: `ink-skill-dev/scripts/verify-chapter.py` ← 从 `scripts/verify-chapter.py` 移植

**说明**：原脚本签名已是 `verify-chapter.py [--allow-short] <books_root> <book_name> <N>`，本身支持书感知，**无需改造**，直接复制即可。

- [ ] **Step 1: 直接复制**

```bash
cp scripts/verify-chapter.py ink-skill-dev/scripts/verify-chapter.py
```

- [ ] **Step 2: 回归测试（用 tests/fixtures/test-book）**

```bash
python3 ink-skill-dev/scripts/verify-chapter.py tests/fixtures test-book 1
# 期望：exit=2 （fixture 章节 80 字 < softMin 90，这是预期的"偏短路径"测试）
# 12/13 环节应通过，唯字数检查失败
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/scripts/verify-chapter.py
git commit -m "feat(ink-skill): port verify-chapter.py (signature already book-aware)"
```

### Task 5.2: merge-truth.py 直接移植

**Files:**
- Create: `ink-skill-dev/scripts/merge-truth.py`

**说明**：原脚本签名 `merge-truth.py {ledger|hooks|...} <existing_path> <incoming_path> [--out PATH]`，直接接受文件路径，**不依赖 cwd 也不需要 --book-root**。直接复制即可。

- [ ] **Step 1: 直接复制**

```bash
cp scripts/merge-truth.py ink-skill-dev/scripts/merge-truth.py
```

- [ ] **Step 2: help 测试**

```bash
python3 ink-skill-dev/scripts/merge-truth.py --help
# 期望输出与原脚本一致
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/scripts/merge-truth.py
git commit -m "feat(ink-skill): port merge-truth.py (file-path based, no changes needed)"
```

### Task 5.3: 跨平台自部署脚本

**Files:**
- Create: `ink-skill-dev/scripts/bootstrap.py`

- [ ] **Step 1: 实现平台检测 + 软链（含 Windows fallback）**

```python
#!/usr/bin/env python3
"""
ink.skill 自部署脚本。用户第一次 git clone 后，或手动"ink 安装到 X 平台"时调用。

检测当前 AI agent 平台，把当前 skill 目录部署到该平台的 skills 路径。
Mac/Linux 用软链（节省空间 + git pull 全平台同步）；
Windows 优先软链，失败降级到 junction（目录软链）或复制。
"""
import argparse
import os
import platform as sysplatform
import shutil
import sys
from pathlib import Path

PLATFORM_SKILL_PATHS = {
    "claude-code": Path.home() / ".claude" / "skills" / "ink",
    "codex": Path.home() / ".agents" / "skills" / "ink",
    "gemini": Path.home() / ".gemini" / "extensions" / "skills" / "ink",
    "cursor": None,  # Cursor 无标准 skills 路径
}

def detect_platform() -> str:
    if os.environ.get("CLAUDECODE"):
        return "claude-code"
    if os.environ.get("CODEX_AGENT"):
        return "codex"
    if os.environ.get("GEMINI_CLI"):
        return "gemini"
    return "unknown"

def _link_or_copy(source: Path, target: Path) -> str:
    """
    返回实际用的方式："symlink" / "junction" / "copy"。
    Windows 上 symlink 需要 admin 或 Dev Mode；失败则 fallback。
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    # 尝试 1: 标准 symlink
    try:
        target.symlink_to(source, target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError) as e:
        if sysplatform.system() != "Windows":
            raise  # Mac/Linux 理论上不应失败

    # Windows fallback 1: directory junction (mklink /J，无需 admin)
    try:
        import subprocess
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            check=True, capture_output=True
        )
        return "junction"
    except Exception:
        pass

    # Windows fallback 2: 整目录复制（失去 git pull 同步，但能用）
    shutil.copytree(source, target)
    print(f"[warn] 创建了复制（非软链）。日后 git pull 需手动重跑 bootstrap 才能同步。", file=sys.stderr)
    return "copy"

def install(platform: str, source: Path):
    target = PLATFORM_SKILL_PATHS.get(platform)
    if target is None:
        print(f"[warn] {platform} 无标准 skills 路径，跳过自部署")
        return
    if target.exists() or target.is_symlink():
        print(f"[info] {target} 已存在，跳过（如要重装先删除）")
        return
    method = _link_or_copy(source, target)
    print(f"[ok] {method}：{target} → {source}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=list(PLATFORM_SKILL_PATHS.keys()) + ["auto"],
                        default="auto")
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    platform = detect_platform() if args.platform == "auto" else args.platform
    print(f"[info] 检测到平台：{platform}")
    install(platform, args.source.resolve())
```

- [ ] **Step 2: 本地测试（--platform=claude-code，应创建软链）**

```bash
python3 ink-skill-dev/scripts/bootstrap.py --platform claude-code --source $(pwd)/ink-skill-dev
ls -la ~/.claude/skills/ink  # 期望是 symlink 指向 ink-skill-dev
rm ~/.claude/skills/ink      # 清理测试
```

- [ ] **Step 3: commit**

```bash
git add ink-skill-dev/scripts/bootstrap.py
git commit -m "feat(ink-skill): add cross-platform bootstrap (auto-detect + symlink)"
```

---

## 阶段 6：老书迁移逻辑

### Task 6.1: 在 reference/init.md 中写迁移流程

**Files:**
- Modify: `ink-skill-dev/reference/init.md`

- [ ] **Step 1: 加"迁移老书"段**

```markdown
## 迁移老书到 ink.skill 形态

**触发词**：ink 迁移 / 迁移本书 / 升级到 skill 版本。

**幂等性检查（应对 R8）**：
- 若 `PROGRESS.md` **已存在**：仅补齐缺段，不全量重写；追加操作时间线前检测末 5 条中是否已有"迁移完成"事件，有则跳过追加
- 若对应平台 init 文件（CLAUDE.md / AGENTS.md 等）**已存在**：不覆盖，提示作者"init 文件已存在，保持不动"

**步骤**（skill 内置执行）：
1. Read `chapters/index.json` 获取章节清单 + status
2. Read `story/current_state.md` 获取最新章号 + 故事状态
3. 遍历 `story/audits/ch-*.md` 收集所有 severity=followup 条目
4. 生成/补齐 `PROGRESS.md`：
   - 当前状态段：`last_approved` 取 index.json 最后一条 status=approved 的章（**覆盖**）
   - 活跃 followup 段：聚合所有 audits 的 followup（**覆盖**）
   - 📋 迁移原始数据段（**首次迁移才加**）：把原 audits 的完整 severity 明细 dump 下来，作者核对无误后可手删此段（应对 R4 聚合错误）
   - 真相文件索引段：用模板（**覆盖**）
   - 操作时间线段：**检查是否已有迁移事件** → 无则追加 `<ts> · 迁移完成（原 markdown-instruction 形态 → ink.skill）`
5. 生成当前平台的 init 文件（按 §init 文件生成规则；已存在则跳过，应对 R8）
6. 提示作者（含 R11 场景）：
   "迁移完成，已生成 PROGRESS.md 和 `<platform>.md`。原 `<books 父目录>/CLAUDE.md`（v1.0.x 分发留下的）与新 init 不冲突，你可以：
   (a) 保留共存 — 老版本作备份，新版 init 优先级更高；
   (b) 删除老版本 — 若不再回滚到 v1.0.x。
   建议先保留 1-2 个会话验证无问题再决定删除。"

**不删除旧文件**：skill 永不主动删除 v1.0.x 分发的 `books/CLAUDE.md` 和 `.claude-modules/`（应对 R11）。
```

- [ ] **Step 2: commit**

```bash
git add ink-skill-dev/reference/init.md
git commit -m "feat(ink-skill): define migration flow for existing books"
```

---

## 阶段 7：集成 & 本地验证

### Task 7.1: 把 ink-skill-dev 软链到 ~/.claude/skills/ink 做真实测试

- [ ] **Step 1: 软链**

```bash
ln -sfn /Users/admin/Codex/Project/Own/ink_writer/ink-skill-dev ~/.claude/skills/ink
```

- [ ] **Step 2: 重启 Claude Code 会话或 /reload-plugins**

- [ ] **Step 3: 开新会话测 3 条触发**

```
1. "ink 测试"
2. "写第 17 章"
3. "审计第 15 章"
```

期望：每条都触发 ink skill。

### Task 7.2: 真实迁移测试（镜源逆刻）

- [ ] **Step 1: 在镜源逆刻书目录下说"ink 迁移"**

- [ ] **Step 2: 验证生成物**

- `books/镜源逆刻/PROGRESS.md` 存在，含 15 章已批准、followup 从 ch1-15 audits 聚合
- `books/镜源逆刻/CLAUDE.md` 存在（3-5 行版本），与旧的 v1 分发的 CLAUDE.md 不冲突（新文件更精简，旧文件在父目录）

- [ ] **Step 3: 跑写章测试：说"写第 17 章"，确认流程端到端通**（正文 ≥ hardMin、audits/ch-17.md 生成、PROGRESS.md 更新）

### Task 7.3: 新建书测试

- [ ] **Step 1: 开新会话："帮我新建一本叫《测试书》的小说"**

- [ ] **Step 2: 验证生成物完整**（基础 5 文件 + 4 truth + snapshots/0/ + 当前平台 init + PROGRESS.md）

---

## 阶段 8：Darwin-skill 优化（**v0.1.0 跳过，推迟到 v0.2.0**）

> 用户决定本版不跑 darwin。本阶段保留用作 v0.2.0 迭代。现在可直接跳到阶段 9。

### Task 8.1: 跑 darwin-skill 对 ink SKILL.md 打分

- [ ] **Step 1: 说"用 darwin 优化 ink skill"**

- [ ] **Step 2: 记录 8 维度得分，保留 > 50% 分差的建议改进**

- [ ] **Step 3: 手动评估 darwin 的改写建议**（自动改不一定符合项目语境）

- [ ] **Step 4: 采纳后 commit**

```bash
git add ink-skill-dev/SKILL.md
git commit -m "chore(ink-skill): iterate on SKILL.md per darwin-skill feedback (round 1)"
```

---

## 阶段 9：发布到独立仓库

### Task 9.1: 把 ink-skill-dev 内容 push 到 PapainTea/ink-skill

- [ ] **Step 1: 复制 ink-skill-dev 内容到临时仓库 clone**

```bash
cd /tmp
git clone git@github.com:PapainTea/ink-skill.git
cp -r /Users/admin/Codex/Project/Own/ink_writer/ink-skill-dev/* ink-skill/
cd ink-skill
```

- [ ] **Step 2: 写 README.md**

内容骨架（中文为主）：

```markdown
# ink.skill

> 跨平台小说写作 AI skill。一份 SKILL.md 同时支持 Claude Code / Codex / Gemini CLI / Cursor，跨设备 git 同步。

## 快速开始

1. **把 skill 克隆到你的 books 目录内**（和你每本书同级，方便整个 `books/` 跨设备同步一起搬）：

   ```bash
   cd <你的 books 目录>
   git clone https://github.com/PapainTea/ink-skill.git
   # 结果：
   #   books/
   #   ├── ink-skill/       ← 刚克隆
   #   ├── 你的书1/
   #   └── 你的书2/
   ```

   > 如果你还没有 books/ 目录，随便建一个（如 `~/novels/books/`）再 cd 进去。下一步会自动把当前 AI 平台链接到这里。

2. **部署到当前 AI 平台**：

   ```bash
   python3 ink-skill/scripts/bootstrap.py --platform auto
   ```

   脚本会检测当前 agent（Claude Code / Codex / Gemini CLI 等），在对应平台的 skills 目录创建指向本目录的软链。Mac/Linux 原生支持；Windows 自动降级为 junction 或复制（见下方 Windows 特别说明）。

   **切换到其他 AI 平台时重跑一次同样命令**即可把该平台也链过来。一次 `git pull ink-skill` 更新全平台。

3. **初始化或迁移一本书**：
   - 新建：对 agent 说"新建一本叫《XXX》的小说"
   - 迁移老书：进入书目录后说"ink 迁移"

## 核心功能

- ✅ 37 维度章节审计
- ✅ 5 种修订模式
- ✅ 7 个真相文件自动维护
- ✅ followup 伏笔回收提醒
- ✅ 跨会话续接（PROGRESS.md）
- ✅ 多平台 agent 兼容

## 触发词

任何含有以下关键词的消息都会激活本 skill：
`ink` / `写书` / `写小说` / `写第 N 章` / `续写` / `连写` / `审计章节` / `润色章节` / `新建书` / `新建章节` / `ink 初始化` / `ink 迁移` / `followup` / `伏笔` / `粒子账本` / `人物矩阵` ...

## 架构

详见 [SKILL.md](./SKILL.md)。

## License

Apache-2.0
```

写入：

```bash
cat > README.md <<'EOF'
<上述内容>
EOF
```


- [ ] **Step 3: 首次 push**

```bash
git add .
git commit -m "feat: initial ink.skill release v0.1.0"
git push origin main
```

- [ ] **Step 4: 打 tag**

```bash
git tag -a v0.1.0 -m "ink.skill v0.1.0 — skill 化首版"
git push --tags
```

### Task 9.2: 更新 ink_writer README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 顶部加导引**

```markdown
## 📢 ink.skill 已发布！

如果你用 Claude Code / Codex / Gemini CLI 等 AI agent，推荐使用 [skill 版本](https://github.com/PapainTea/ink-skill)，安装一次跨平台可用、自动迁移老书。

原 markdown instruction 分发（v1.0.x）继续维护，已有作者可继续使用。
```

- [ ] **Step 2: commit**

```bash
git add README.md
git commit -m "docs: link to ink.skill repo from ink_writer README"
```

---

## 阶段 10：回归 & 扫尾

### Task 10.1: 全部 golden-case 回归

- [ ] **Step 1: 镜源逆刻**：写 ch17（skill 形态） + 审计 + 修订各跑一次
- [ ] **Step 2: 长夜**：跑一次迁移 + 新写一章
- [ ] **Step 3: 新建书**：跑一次新建 + 第 1 章写作
- [ ] **Step 4: 回归 verify-chapter 脚本** (`tests/fixtures/test-book` 在新 `--book-root` 模式下仍通过)

### Task 10.2: 更新 CLAUDE.md（开发指引）

**Files:**
- Modify: `CLAUDE.md`（项目级开发指引）

- [ ] **Step 1: §2.1 核心目标更新**：加入"ink.skill 分发形态"
- [ ] **Step 2: §3.1 模块清单新增**：ink-skill-dev/ 子项
- [ ] **Step 3: §9 待办**：移除已做项，添加后续计划（Windows 符号链接、darwin 迭代轮数上限等）
- [ ] **Step 4: commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with ink.skill development status (阶段 1-10 done)"
```

---

## 风险点与缓解

| # | 风险 | 概率 | 影响 | 缓解 | 应对位置 |
|---|------|------|------|------|---------|
| R1 | skill 触发不可靠（"继续写"不带关键词时漏触发） | 中 | 用户以为 skill 没装好 | ① init 模板加**强制祈使句**"必须执行：回应前先调用 ink skill"，即使无触发词也必触发 ② 触发词密度轰炸 | Task 4.2 四个模板都加入 |
| R2 | reference/ 模块过大（>50k chars） | 中 | 加载慢 | 继续按需加载设计，每模块独立；单文件软上限 30k | Task 2.x 每 commit 后检查 `wc -c`，超限则拆分 |
| R3 | Windows 用户不能用软链（无 admin / 无 Dev Mode） | 中 | 跨平台自部署失败 | bootstrap.py 三级降级：symlink → junction（mklink /J）→ copytree | Task 5.3 Step 1 新代码 |
| R4 | 迁移老书时 audits 聚合逻辑错（severity 判错） | 低 | followup 丢失 | 迁移时把原 audits 内容全量 dump 到 PROGRESS.md 的"📋 迁移原始数据"暂存段，作者核对后可清理 | Task 6.1 |
| R5 | ink_writer 老用户看到 README 顶部导引困惑 | 低 | 支持负担 | README 明确"老用户可继续使用 v1.0.x，不强制升级" | Task 9.2 |
| R6 | darwin-skill 改写后 SKILL.md 语义偏移 | 中 | 触发或协议被破坏 | **本版不做 darwin**，推迟到 v0.2.0 | 阶段 8 标记为可选 |
| R7 | **【新】多本书在同一 workspace 的书识别**：在 `books/` 父目录（非某本书子目录）说"写第 17 章"时不知道是哪本 | 中 | skill 在错的书上写章 | ① SKILL.md 激活第一步：检测 cwd 不是某本书根时，**强制询问作者**"要写哪本书？"再继续 ② init 文件只在书子目录存在，父目录无 init = 不假设任何书 | Task 1.1 Step 2 (b) |
| R8 | **【新】迁移幂等性**：重复跑"ink 迁移"会不会覆盖 PROGRESS.md（丢作者笔记或追加重复）？ | 中 | 数据损坏 | PROGRESS.md 已存在时，迁移流程仅**补齐缺段**而非全量重写；追加时检测时间线末尾是否已有"迁移完成"事件避免重复追加 | Task 6.1 加"幂等性检查"子步 |
| R9 | **【新】SKILL.md 体积**：body 膨胀可能 >40k chars，拉慢加载 | 中 | 体感慢 | Task 1.1 完成后 `wc -c SKILL.md` 确保 <15k；核心协议放 SKILL.md，方法论压去 reference/ | Task 1.1 新增 Step 4 |
| R10 | **【新】test fixture 兼容性**：`tests/fixtures/test-book` 在新 `--book-root` 模式下是否仍能通过 | 低 | 阶段 5 验证失败 | 阶段 0 先跑一次验证，不兼容则 plan 加一个 fixture 修正任务 | Task 0.2（新增） |
| R11 | **【新】老的 `books/CLAUDE.md`（v1.0.x 分发）与新 per-book init 并存**：Claude Code 会同时读两份 | 低 | 轻微冗余但不破坏 | 迁移流程提示作者"老的 `books/CLAUDE.md` 可保留也可删除，两者不冲突但新 init 更精确"；不强制删 | Task 6.1 |

---

## 阶段依赖关系

```
阶段 0（前置）
  ↓
阶段 1（SKILL.md 骨架）
  ↓
阶段 2（reference/） ─┐
阶段 3（PROGRESS.md） ┼─→ 阶段 7（集成测试）
阶段 4（init 文件） ─┤        ↓
阶段 5（scripts/） ──┤    阶段 8（darwin 优化）
阶段 6（迁移流程） ──┘        ↓
                          阶段 9（发布）
                              ↓
                          阶段 10（回归 & 文档）
```

阶段 2-6 可**并行开发**（不同文件无冲突），阶段 7 之前必须全做完。

---

## 验收标准（每阶段）

- **阶段 1**：SKILL.md 能在本机 skills 列表里被识别（`/reload-plugins` 后可见）
- **阶段 2**：所有 reference/*.md 不含书名泄漏（grep 为空），skill-context 头齐全
- **阶段 3**：PROGRESS.md 模板完整 5 段，SKILL.md 内规定了每段读写规则
- **阶段 4**：4 平台 init 模板齐全，book-skeleton 完整（验证：cp -r templates/book-skeleton /tmp/test 后能通过 verify-chapter.py）
- **阶段 5**：两个 py 脚本都接受 `--book-root`，在 test-book fixture 上跑通
- **阶段 6**：镜源逆刻说"ink 迁移"后 PROGRESS.md 正确生成、15 章 followup 聚合正确
- **阶段 7**：3 条触发语、1 次迁移、1 次新建书、1 次完整写章 —— 全部端到端通
- **阶段 8**：darwin 给出 8 维评分，采纳 ≥1 条改进并验证未破坏触发
- **阶段 9**：ink-skill repo v0.1.0 tagged，README 中文完整，他人 clone + bootstrap 后可用
- **阶段 10**：CLAUDE.md v3 更新，所有 golden-case pass

---

## 执行方式建议

**推荐**：逐阶段执行（阶段 0 → 阶段 1 → ... → 阶段 10），每阶段末做 human review，决定是否进入下一阶段。

阶段 2-6 可在**同一会话**里并行（文件无冲突），但**阶段 7 必须单独会话跑端到端验证**（避免开发会话的 context 污染测试）。

阶段 8（darwin 优化）可以跳过到 v0.2.0 再做——先把 v0.1.0 能用版本发出去，收到反馈再迭代。

---

*Plan 版本：v1 · 2026-04-15*
