# ink_writer —— 项目上下文（给 Claude Code 的常驻记忆）

> 本文件是 ink_writer 项目本身的开发指引，给将来在这个目录工作的开发者/Claude 看。
>
> 如果你是为某本书写作而打开 Claude Code，你要的是 **`dist/CLAUDE.md`** 而不是这个文件——把那个文件复制到你的书籍项目根目录的 `.claude/CLAUDE.md` 即可。

---

## §0 维护约定（必读）

**每次施工结束，必须更新本文件**。具体：

1. 修改了 `src/` 模块 → 在 §3 进度记录下添加一条变更
2. 修改了 schema / merge 规则 → 在 §6 核心决策中补充一条决策记录
3. 修复了 bug 或验证了 golden-case → 在 §7 进度状态对应行打勾或加备注
4. 用户给出新的偏好/原则 → 写进 §5 维护原则
5. 完成新模块 → §3 模块清单更新行数和状态

**为什么**：这个项目的核心 IP 是 prompt 算法 + 设计决策。代码可以从 git diff 看出来，但**为什么这样设计**只能写在文档里。否则三个月后回来看，每条规则都要重新推一遍。

---

## §1 这是什么项目

**ink_writer 是一个用 markdown 表达的多 agent 小说写作系统**，可以安装在 Claude Code / Codex CLI / 任何支持 project instruction 的 AI CLI 工具上。

### 1.1 一句话定位

把"严肃长篇网络小说创作流水线"打包成一份 markdown instruction，配合任意 AI CLI 即可使用，零 npm 依赖、零桌面安装包、跨平台。

### 1.2 前身和动机

ink_writer 的前身是 **inkOS**（位于 `/Users/admin/Codex/Project/inkOS/`），一个 TypeScript monorepo，含：
- `packages/core/`（~21k 行）—— 12+ 个 LLM agent + pipeline runner + merge 工具
- `packages/cli/`（~3.7k 行）—— CLI 命令行工具
- `packages/studio/`（~10.8k 行）—— 本地 Web UI + Mac/Windows 打包

inkOS 由用户从 `Narcooo/inkos` fork 而来，做了大量独立改动（Studio Web UI、AIGC 检测、ledger 7 列 schema、character_matrix 3 子表、sentinel 系统等），与上游严重发散。

### 1.3 为什么要从 inkOS 转化为 ink_writer

**核心洞察**：inkOS 80% 的"承重逻辑"是 prompt 文本（writer-prompts.ts 的 25 条创作规则、settler-prompts.ts 的 9 个分析维度、continuity.ts 的 37 个审计维度、reviser.ts 的 5 种修订模式等）。TypeScript 代码只是这些 prompt 的"运输工具"。把 prompt 从 .ts 文件里解放出来，直接放到 CLAUDE.md 里，LLM 加载时就能看到全部规则。**运输成本显著降低**——从"改代码 → 构建 → 测试 → 打包"变成"改 markdown"。

**触发事件**：2026-04-12 晚，用户让 Claude 直接操作书籍文件（不通过 inkOS pipeline），在 2-3 小时内完成了：
- 全书 13 章通读润色
- 13 个章节标题全部重构
- 第 14 章完整写作
- 所有 truth files 同步更新

**对比**：inkOS 维护期 15 天修了约 20 个 bug、0 章新内容。这 2-3 小时的产出才是真正有价值的输出。用户原话：

> "我突然间意识到，可能对于这么一个项目来说，真正有价值的输出的内容才是最重要的，过程反而是其次的。"

### 1.4 困境清单（为什么必须转变）

| 困境 | 表现 |
|------|------|
| Bug 产生速度 > 修复速度 | 15 天内 ~20 个 UI bug，CLAUDE.md TODO 里 P-HOT/P2/P3-A/P3-B 长期未做 |
| Studio UI 重复发明 CLI 已有功能 | pipeline 实时进度、diff 显示、刷新恢复——CLI 工具天然具备 |
| Fork 后与上游严重发散 | schema 改动让上游新功能无法直接 merge |
| 架构导致 LLM 错误理解 | prompt 硬编码在 .ts，LLM 看不到全局；merge 黑箱导致 Bug E 类问题 |
| 单人维护不可持续 | core 21k 行 + studio 10.8k 行，bug 修不完又一直加新功能 |

---

## §2 要做什么（目标）

### 2.1 核心目标

产出一套**模块化源文档**（`src/*.md`，14 个模块），通过生成器拼接为各平台适配版本（首要 `dist/CLAUDE.md`，由 Codex 后续做 `dist/AGENTS.md`），配合一个**轻量 Python 兜底脚本**（`scripts/merge-truth.py`）处理确定性合并。

### 2.2 设计原则

1. **能力级别描述，不绑定平台工具名**：源文档写"读取文件""定点修改"，生成时替换为具体工具
2. **零 npm 依赖**：除生成器和兜底脚本外，纯 markdown
3. **严格对齐原项目数据格式**：保证 ink_writer 和 inkOS 的书籍数据可以无缝切换
4. **NO 书籍内容泄漏**：`src/` 模块只能用通用占位符（主角/配角B/势力A/mentor-oath/lost-key/SL-01 等），严禁出现任何具体书籍的角色名/地名（顾悬/周巡事/镜源逆刻/长夜 等）
5. **prompt 95% + 脚本 5%**：日常写章/审计/修订全部 prompt 化；只有外部数据合并、批量 rebuild、schema 守卫等确定性操作走脚本

### 2.3 不做的事（明确边界）

| 不做 | 理由 |
|------|------|
| Plugin 壳（plugin.json + slash command）| Claude Code 专有，不跨平台；当前阶段优先做通用 instruction |
| Web UI / 桌面应用 | CLI 工具天然具备文件浏览、diff、实时输出能力；UI 是 bug 主要来源 |
| TypeScript pipeline 编排 | 与项目方向相反（这是要砍掉的部分） |
| 跨进程锁 / pipeline cache / SSE 推送 | 单用户 CLI 不需要 |
| Memory 检索（memory.db）| 1M context 放得下 truth files；如果未来 100+ 章撑不下再按需引入 |

---

## §3 已经完成什么（进度记录）

### 3.1 模块清单

| 模块 | 行数 | 状态 | 来源 |
|------|------|------|------|
| `src/00-system-role.md` | 37 | ✅ 完成 | 自写（系统角色定义）|
| `src/01-data-structure.md` | 135 | ✅ 完成 | 自写（数据目录约定 + index.json schema）|
| `src/02-truth-schema.md` | 398 | ✅ 完成 | 提取自 ledger-schema.ts / settler-prompts.ts / writer-prompts.ts |
| `src/03-foundation-files.md` | 175 | ✅ 完成 | 提取自 architect.ts |
| `src/04-write-pipeline.md` | 388 | ✅ 完成 | 提取自 runner.ts `_writeNextChapterLocked` |
| `src/05-writing-rules.md` | 430 | ✅ 完成（最大模块）| 提取自 writer-prompts.ts |
| `src/06-audit-system.md` | 198 | ✅ 完成 | 提取自 continuity.ts，审计存储改 audits/ch-N.md |
| `src/07-revision-modes.md` | 217 | ✅ 完成 | 提取自 reviser.ts |
| `src/08-settlement.md` | 144 | ✅ 完成 | 提取自 settler-prompts.ts |
| `src/09-post-write-validation.md` | 98 | ✅ 完成 | 提取自 post-write-validator.ts |
| `src/10-snapshot-rollback.md` | 135 | ✅ 完成 | 自写（基于 state/manager.ts 语义，含 audits/ 归档）|
| `src/11-hook-governance.md` | 80 | ✅ 完成 | 提取自 hook-governance.ts |
| `src/12-init-book.md` | 127 | ✅ 完成 | 自写（CC 对话式新建，不用 Architect 重型 prompt）|
| `src/13-commands.md` | 70 | ✅ 完成 | 自写（用户命令参考）|
| `scripts/merge-truth.py` | 345 | ✅ 完成 | 自写（确定性合并 + schema 守卫）|
| `scripts/verify-chapter.py` | 419 | ✅ 完成 | 自写（三层不变量验证，Step 12 强制调用）|
| `build/generate.py` | 115 | ✅ 完成 | 自写（拼接生成器）|
| `dist/CLAUDE.md` | 2691 | ✅ 已生成 | 自动生成 |
| `README.md` | 252 | ✅ 完成 | 给作者看的安装/使用指南 |
| `dist/AGENTS.md` | — | ⬜ 待 Codex 生成 | Codex CLI 版本 |
| `tests/` golden-case 样本 | — | ⬜ 待补充 | 3 个真实任务的预期输入输出 |

### 3.2 关键变更日志

| 日期 | 变更 |
|------|------|
| 2026-04-13 | 项目从 inkOS 提取，14 个 src 模块 + merge-truth.py + generate.py 完成 |
| 2026-04-13 | 第一轮 golden-case 验证：用 dist/CLAUDE.md 对镜源逆刻 ch14 做审计，命中 15 处破折号（critical），audit 流程跑通 |
| 2026-04-13 | 对齐原项目 schema：index.json 4 种 status 枚举、createdAt/updatedAt/wordCount/lengthWarnings 字段；明确不创建 state/ runtime/ memory.db；砍掉 lengthTelemetry |
| 2026-04-13 | 项目从 `/Users/admin/Codex/Project/inkOS/inkos-kit/` 迁移到 `/Users/admin/Codex/Project/Own/ink_writer/` |
| 2026-04-13 | **审计存储改造**：删 `index.json.auditIssues` 字段，改成 `story/audits/ch-N.md`（Obsidian callout 格式），加入 snapshots/N/audits/ 一并归档 |
| 2026-04-13 | **简化新建书流程**：删除 Architect 重型 prompt，改成 CC 多轮对话产出 5 个基础文件 + 4 个空真相文件 + snapshots/0/ |
| 2026-04-13 | **章节文件命名约定**：4 位章节号（不足补 0）+ 下划线 + 标题，例 `0014_收网.md`；正文第一行也写 `# 第 14 章 收网`（双重携带，便于阅读）|
| 2026-04-13 | **README.md** 完成（给作者看的安装/使用文档，252 行）|
| 2026-04-13 | status 4 种枚举的解释修正：用于"判断章节是否过审"，不是"作者管理写作进度" |
| 2026-04-13 | **书籍数据迁移 + 路径解耦**：books 数据 cp 到 `/Users/admin/Codex/Project/Own/ink_writer/books/`（git ignored）；skill 文档所有硬编码 `~/.inkos/data/books/` 替换为 `<父目录>/books/<书名>/` 占位符；新增 `.ink-writer.yaml` 配置文件（books 根目录下一级，持久化 booksRoot），LLM 启动时先读配置再问作者；`00-system-role.md` + `01-data-structure.md` 大改 |
| 2026-04-14 | **加规则 12：禁止 markdown 结构化标记泄漏正文**（commit 676bbe1）。从 ch15 golden-case 的 6 处 `---` 污染中发现 |
| 2026-04-14 | **B1 修 Step 7 审计"可选"→"默认必跑"**：src/04 与 src/06/src/13 对齐，消除文档自相矛盾。作者可说"这章先不审计"或配置 `autoRunAudit=false` 显式 opt-out |
| 2026-04-14 | **A1 字数 schema 统一**：废弃 `chapterWordCount` 和 `lengthSpec`，canonical = `book_rules.yaml.length.*` 对象（target / softMin/MaxPct / hardMin/MaxPct / countingMode / enforceSoftMin / enforceHardMin）；同时新增 `hardRules.*` 和 `pipeline.*` 配置块。全文替换 src/04 + src/07 + src/03 |
| 2026-04-14 | **A2 PRE_WRITE_CHECK 加场景级字数预算**：要求把 target 拆成 3-6 个场景预算，总和 ≈ target ± 5%。同时加入"允许偏短声明"机制，转场章/动作章可显式 opt-out 扩写 |
| 2026-04-14 | **A3 字数分层处理**：`< hardMin` 硬 block / `softMin~hardMin` 默认一次扩写（可声明例外跳过）/ `> hardMax` 触发压缩。src/04 Step 6 完全重写 |
| 2026-04-14 | **B2 写 scripts/verify-chapter.py**：三层不变量检查（强制不变量 / 机械规则 / 条件性副作用按审计声明驱动）。主动发现 ch15 chapter_summaries 行粘连 bug |
| 2026-04-14 | **B3 加 Step 12 强制 verify**：src/04 新增 Step 12，章节完成最终门槛，不通过不算完成 |
| 2026-04-14 | **A4 镜源逆刻 book_rules.md 落地 length/hardRules/pipeline 配置**（target=4500 / softMin=4050 / hardMin=3600）|

### 3.3 Golden-case 验证状态

成功标准：3 个真实任务在 2 本书（镜源逆刻 14 章 + 长夜 1 章）上连续跑稳。

| 任务 | 镜源逆刻 | 长夜 | 备注 |
|------|----------|------|------|
| **写下一章** | ⬜ 未跑 | ⬜ 未跑 | 需要写 ch15（必须包含转场 + 镜核首触发） |
| **审计某一章** | ✅ ch14 已跑通 | ⬜ 未跑 | ch14 命中 15 处破折号 critical，建议规则有效 |
| **修订某一章** | ⬜ 未跑 | ⬜ 未跑 | 等用户决定先修破折号还是先写 ch15 |

---

## §4 仓库布局

```
ink_writer/
├── CLAUDE.md              # 本文件（项目级开发指引）
├── src/                   # 模块化源文档（维护层，14 个 markdown 模块）
├── scripts/
│   └── merge-truth.py     # 确定性合并脚本
├── build/
│   └── generate.py        # 拼接生成器（src/ → dist/CLAUDE.md）
├── dist/                  # 平台适配版本（生成物，不要手改）
│   └── CLAUDE.md          # Claude Code 版（首要目标）
└── tests/                 # Golden-case 验证（待补充）
```

---

## §5 维护原则（用户偏好沉淀）

### 5.1 单一事实源

**`src/` 是源，`dist/` 是生成物**。日常修改在 `src/`，然后跑 `python3 build/generate.py` 重新生成 `dist/`。**不要手改 `dist/`**（下次生成会被覆盖）。

### 5.2 NO 书籍内容泄漏

**严禁在 `src/` 里出现任何具体书籍的角色名/地名/世界观元素**。这是产品，要给所有用户用。

示例统一用通用占位符：
- 角色：主角 / 配角B / 配角C
- 势力：势力 A / 势力 B
- ID 示例：mentor-oath / lost-key / SL-01
- 资源示例：情报权 / 金币（通用资源类型可以用，注意区分通用 vs 专属）

如果发现泄漏，立刻清理。曾经有过几次错误：
- 02-truth-schema.md 早期示例用了顾悬/周巡事，已清理
- 05-writing-rules.md 提取时带过一个角色名"陆焚"，已替换为"某人"

### 5.3 严格对齐原项目数据格式

skill 设计上**严格对齐**原项目的数据格式约定（`/Users/admin/Codex/Project/inkOS/`），保证数据可在两套系统间无缝切换：

| 对齐项 | 状态 |
|--------|------|
| chapters/index.json 是 JSON 数组（不是 `{chapters: [...]}` 包裹） | ✅ 已对齐 |
| index.json 字段：number/title/status/wordCount/createdAt/updatedAt/auditIssues/lengthWarnings | ✅ 已对齐 |
| status 4 种枚举：draft/audited/approved/needs_revision | ✅ 已对齐 |
| auditIssues 格式：`["[severity] description", ...]` 字符串数组 | ✅ 已对齐 |
| Truth file 表头列数和列名（原项目源码为准）| ✅ 已对齐 |
| character_matrix 3 子表结构（角色档案/相遇记录/信息边界）| ✅ 已对齐 |
| ledger 7 列含事件ID | ✅ 已对齐 |
| snapshots/N/ 语义和文件清单 | ✅ 已对齐 |
| Sentinel 字符串（"☆ X 无变动 ☆"）| ✅ 已对齐 |
| current_state.md 的标题是 `# 当前状态`（不是"当前状态卡"）| ✅ 已对齐 |

### 5.4 平台无关源 + 平台特定生成

`src/` 模块用**能力级别描述**（"读取文件""定点修改""执行 shell 命令"），不绑定具体工具名。生成步骤把能力描述替换为平台具体工具：

- Claude Code → Read / Edit / Write / Grep / Glob / Bash
- Codex CLI → 由 Codex 自己映射

`build/generate.py` 中有 `CAPABILITY_MAP` 占位，待具体接入。

### 5.5 用户协作偏好

- **语言**：主要中文，技术术语可混 English
- **偏好讨论**：产品和架构层面，**不爱看大段 code diff**
- **决策风格**：**先问清楚再动手**。不要一上来就大改，先给方案让他选
- **批判性反馈**：用户会拿 Codex 做交叉审查（"我让 Codex 看了一下你的方案"），要做好被指出"过于乐观/伪精确数字/内部矛盾"的准备
- **数据洁癖**：对真相文件一致性要求极高，宁可 token 多也要保证一致
- **不爱发明新格式**：能用原项目格式就用，不要自己造（曾经犯过的错误：自建 `story/audits/` 而不是用 `index.json.auditIssues`）
- **追求轻量**：UI/打包/复杂架构都是负担，能砍就砍

---

## §6 核心决策记录

### 6.1 为什么不做 plugin 壳，做 markdown instruction

Claude Code 的 plugin 格式（plugin.json + slash commands + hooks）是 Claude Code 专有的，不跨平台。当前阶段优先做 markdown instruction 形式：

- 跨平台通用（Claude Code → CLAUDE.md / Codex → AGENTS.md / Cursor → .cursorrules）
- 自然语言触发不需要 slash command 封装
- 不被任何一个平台绑定

如果未来用户量大需要安装体验/分发市场，再做 Claude Code plugin 壳。**不要在 golden-case 验证通过前做 plugin 壳**——那是锦上添花，不是核心价值。

### 6.2 为什么不做 UI

老 inkOS 的 Studio Web UI 在 skill 模式下基本被 CLI 取代：

| Studio 功能 | skill 替代 |
|------------|-----------|
| 写章按钮 / pipeline 可视化 | "写第 N 章" + Terminal 实时输出 |
| 审计面板 | "审计第 N 章" → 输出到 index.json |
| 章节浏览 | VSCode / Obsidian / 文本编辑器 |
| Truth files 浏览 | 同上，markdown 任何编辑器都能看 |

Studio 历史 bug 集中在 UI 层（race / 状态丢失 / 按钮消失 / CSS）。不做 UI 等于消除整个 bug 面。如果未来真的非 UI 不可，应该是**纯只读的极简浏览面板**（不做写操作 = 不引入新 bug）。

**测试反而更简单**：测试对象从"UI 行为"变成"文件内容"。文件是确定性的——行数对不对、schema 对不对、数据有没有丢，一眼就能看出来。不像 UI 那样有 race condition、浏览器差异、CSS 渲染问题。

### 6.3 为什么保留 merge-truth.py

prompt 模式覆盖 95% 的日常写作流程（写章、审计、修订、结算），但**确定性表格合并 + schema 守卫**这部分代码比 prompt 更稳定。保留 ~280 行 Python 兜底，处理：

- 从快照恢复后重建
- 批量 rebuild（ledger / hooks）
- 导入外部章节

**判定边界**（不是按行数，而是按操作类型）：
- LLM 自己产出的变更 → LLM 自己更新（read → modify → write）
- 外部来源或批量操作 → 调脚本

### 6.4 砍掉的原项目功能（决策依据：用户 + Codex 独立判断一致）

| 砍掉 | 决策 | 依据 |
|------|------|------|
| `story/state/`（结构化 JSON 索引）| ❌ 砍 | Markdown truth files 已是事实层 |
| `story/runtime/`（pipeline 中间产物）| ❌ 砍 | skill 无 planner/composer 分阶段 |
| `story/memory.db`（SQLite）| 🟡 可选 | 1M context 放得下；超长项目可加 |
| `story/logs/`（pipeline ndjson）| 🟡 可选 | CLI 直接看实时输出；审计可归档 |
| `index.json.lengthTelemetry`（10+ 字段）| ❌ 砍 | 无独立 normalize/revise 阶段 |

### 6.5 保留的原项目功能（不能砍）

- `snapshots/N/`：rework 流程依赖，必须保留
- `index.json` 4 种 status 枚举：用户明确要求保留全部
- `auditIssues` 字段：标准审计结果位置
- 7 个 truth file schema：核心数据模型

### 6.6 平台支持优先级

- **首要**：Claude Code（生成 `dist/CLAUDE.md`）
- **次要**：Codex CLI（由 Codex 自己生成 `dist/AGENTS.md`）
- **后期按需**：Cursor（`.cursorrules`）/ Windsurf（`.windsurfrules`）/ 其他

不同平台的工具命名/权限/上下文行为不一样，不是"复制改名"就能通用。需要 generate.py 的能力映射表来做适配。

### 6.8 数据路径解耦 + 配置文件（2026-04-13）

**问题**：早期 skill 文档里硬编码 `~/.inkos/data/books/<书名>/`，这是从原 inkOS 项目继承的约定，作者换位置不灵活。

**决策**：
- 所有 skill 文档里的硬编码路径替换为占位符 `<父目录>/books/<书名>/`（`books` 是固定命名，父目录作者自选）
- 引入配置文件 `<父目录>/books/.ink-writer.yaml` 持久化 `booksRoot`
- LLM 启动流程：先读配置 → 读到就用 → 没读到就问作者 + 自动写入配置
- 作者第一次告诉 LLM 绝对路径后，下次对话不用重复问

**实施位置**：`src/00-system-role.md` 新增"数据位置"章节 + `src/01-data-structure.md` 目录布局更新

### 6.9 LLM 漏环节防御 — 已实施（2026-04-14 完整落地）

**2026-04-13 ch15 golden-case 暴露的 3 类漏环节**，到 2026-04-14 全部有系统性防御：

| 漏环节 | 防御层 | 实施位置 |
|--------|-------|---------|
| 跳过 Step 7 审计 | Step 7 默认必跑 + autoRunAudit 配置 | src/04 Step 7 重写 + src/03 pipeline.autoRunAudit |
| 字数不达标不扩写 | Step 6 字数分层处理 + PRE_WRITE_CHECK 场景预算 | src/04 Step 4 + Step 6 |
| 正文违反硬性禁令 | Step 12 verify-chapter.py 强制兜底 + 规则 12 禁止 markdown 泄漏 | scripts/verify-chapter.py + src/09 规则 12 |

**配置开关**（作者可关闭某项，自担风险）：`book_rules.yaml.pipeline` 块下的 `autoRunAudit` / `autoRunVerify` / `autoExpandIfShort` 都默认 `true`。

**B4 全局 Claude Code hook 仍不做**（成本高于收益，verify 脚本已够）。

### 6.7 LLM 漏环节防御（待定方案，2026-04-13 ch15 golden-case 发现）

**触发事件**：ch15 golden-case 验证时，Claude 写完正文后直接跑机械校验（Step 6），跳过 37 维度审计（Step 7），用户指出才补。证明**纯 prompt 指引不足以保证 LLM 100% 遵守 11 步流程**。

**已识别的漏环节场景**：
- 写完正文就去结算，跳过 Step 7 审计
- 结算时只更新部分 truth files（比如 current_state 更新了但 character_matrix 漏了）
- 忘记 Step 10 快照
- 写后校验只查 1-2 条规则，没跑完整 11 条

**3 层防御方案（待决策）**：

**层 1 - Prompt 强约束**（已在 04-write-pipeline.md，但有限）
- 11 步 checklist 已列出
- 末尾加"关键不变量"5 条
- 问题：LLM 仍可能"读而不执行"

**层 2 - 验证脚本**（推荐立即做）
- 新增 `scripts/verify-chapter.py N`，检查一章完成后所有副作用：
  - `chapters/000N_*.md` 存在 + 字数达标
  - `story/audits/ch-N.md` 存在
  - `story/snapshots/N/` 含 7 个 truth files
  - `chapter_summaries.md` 最后一行是 ch N
  - `current_state.md` 的"当前章节"= N
  - `particle_ledger.md` 有 ch N 行 + 期初+变动=期末
  - `index.json` 有 ch N 条目 + status != draft
  - 机械规则：破折号 / 不是而是 / 分析术语 = 0
- 在 04-write-pipeline.md 末尾加硬约束 "Step 12: 运行 `python3 scripts/verify-chapter.py N`，不通过不算完成"
- 成本：~100 行 Python，一次性写

**层 3 - Claude Code Hook**（最硬，需用户配置）
- PostToolUse hook 监听 Write / Edit 工具
- 每次写文件后自动 verify，不通过 block Claude 停止
- 成本：settings.json 配置，用户侧工作

**当前状态**：方案 1 已有，方案 2/3 **待用户决策**。ch15 golden-case 先按当前 prompt 流程走，验证后根据结果决定是否做方案 2。

**关联任务**：见 §9 待办。

---

## §7 上游 inkOS 的关系

- 上游：`/Users/admin/Codex/Project/inkOS/`（TypeScript monorepo）
- 关系：ink_writer 是 inkOS 的核心 IP 提取版，**不再同步上游代码**
- 上游的 prompt 文件是 ink_writer 的 prompt 来源参考，如果需要查证某条规则的原始定义，可以回去翻：
  - `packages/core/src/agents/writer-prompts.ts` — 创作规则源头
  - `packages/core/src/agents/settler-prompts.ts` — 结算规则源头
  - `packages/core/src/agents/continuity.ts` — 37 维度审计源头
  - `packages/core/src/agents/reviser.ts` — 5 种修订模式源头
  - `packages/core/src/agents/post-write-validator.ts` — 11 条校验源头
  - `packages/core/src/utils/ledger-schema.ts` — ledger 7 列 + 事件ID 规则
  - `packages/core/src/utils/hook-governance.ts` — 伏笔治理源头
  - `packages/core/src/agents/architect.ts` — 新建书流程源头
- 上游数据目录格式：ink_writer **严格对齐**，保证两套系统的书籍数据可以共用
- 上游 inkOS 不删除，作为代码归档保留

---

## §8 常用操作

### 8.1 修改源模块

```bash
cd /Users/admin/Codex/Project/Own/ink_writer

# 1. 编辑 src/ 下的某个模块
$EDITOR src/05-writing-rules.md

# 2. 重新生成 dist/CLAUDE.md
python3 build/generate.py

# 3. 验证生成是否成功
wc -l dist/CLAUDE.md

# 4. 更新本 CLAUDE.md 的 §3.2 变更日志
```

### 8.2 测试 merge-truth.py

```bash
python3 scripts/merge-truth.py --help

# 合并某个 truth file（外部数据/批量恢复场景）
python3 scripts/merge-truth.py ledger \
    <父目录>/books/<书名>/story/particle_ledger.md \
    /tmp/new_ledger.md \
    --out /tmp/merged.md
```

### 8.3 Golden-case 验证

把 `dist/CLAUDE.md` 复制到某本测试书的 `.claude/CLAUDE.md`，跑以下 3 个真实任务：

1. "写第 N 章" → 完整 11 步流程
2. "审计第 N 章" → 37 维度独立审计
3. "润色第 N 章" → 5 种修订模式之一

每个任务在 2 本书上各跑 1 次。truth files 行数不减少 + index.json 字段对齐 = 通过。

跑完后更新本 CLAUDE.md 的 §3.3 进度表。

### 8.4 检查是否有书籍内容泄漏

```bash
# 任何时候运行这个，输出应该为空
grep -rl "顾悬\|周巡事\|镜源\|长夜\|西角\|乙九\|候潮人\|锁符\|顾家" src/ scripts/ build/
```

---

## §9 待办

- [ ] Golden-case 测试样本（`tests/` 下补充 3 个真实任务的预期输入输出）
- [ ] AGENTS.md（Codex CLI 版本，由 Codex 自己生成）
- [ ] generate.py 的能力映射表实际接入（当前 CAPABILITY_MAP 是占位）
- [ ] 用户使用文档（README.md，给作者看的安装/使用指南）
- [ ] 在镜源逆刻上跑通 3 个真实任务（写章 / 审计 / 修订），全部通过后宣布转型成功

---

## §10 禁忌（不要做的事）

- ❌ 不要在 `src/` 任何模块里出现具体书籍的角色名/地名（顾悬、周巡事、镜源逆刻 等）
- ❌ 不要手改 `dist/`（下次生成会覆盖）
- ❌ 不要 reintroduce TypeScript pipeline 编排（与项目方向冲突）
- ❌ 不要在没读过 `src/02-truth-schema.md` 的情况下改动 truth file 相关逻辑（合并语义复杂）
- ❌ 不要扩展 `merge-truth.py` 去做 LLM 能做的事（脚本只做确定性合并）
- ❌ 不要让 skill 依赖任何 npm/node 包（保持零依赖）
- ❌ 不要自己发明数据格式（先看原项目怎么做，照搬）
- ❌ 不要在 plan / 文档里写"100% 替代""零 bug""轻而易举"等过满表述（用户会用 Codex 审查，会被打脸）
- ❌ 不要施工完不更新本文件（这是核心约定，见 §0）

---

*版本：v2.1 | 2026-04-13*
*v1.0：初始迁移版本，开发指引为主*
*v2.0：补充项目动机/进度记录/核心决策/用户协作偏好/施工后更新约定*
*v2.1：审计存储改造（audits/ch-N.md + Obsidian callout）；简化新建书；章节文件命名约定明确；README 完成；status 解释修正*
