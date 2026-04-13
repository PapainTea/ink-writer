# 新建书流程

**触发**：用户说"新建一本书" / "建一本新书" / "我想写一本 XX"。

**核心思路**：直接对话产出，不用 Architect 那套重型 prompt。作者告诉 Claude 想写什么，Claude 边问边产出 5 个基础文件 + 初始化目录结构 + 创建 snapshots/0/。

---

## 1. 对话采集（边问边写，不一次性问完）

按需采集，不要一次性问太多。最少需要：

| 必问 | 用途 |
|------|------|
| **书名** | 决定目录名 `<父目录>/books/<书名>/` |
| **题材方向** | 玄幻 / 都市 / 科幻 / 同人 / ... 决定写作风格倾向 |
| **主角设定** | 一两句话即可：身份 + 核心优势 + 性格底色 |
| **故事梗概** | 一段话：起点 + 主线冲突 + 大致目标 |

可选（不要一次问完，作者愿意补就补）：
- 平台口味（起点 / 番茄 / 晋江 / ...）
- 目标卷数 / 每章字数
- 语言（默认中文）
- 是否有特殊禁忌 / 不写的元素

**对话原则**：
- 作者说"随便"或拒绝细化时，Claude 直接产出合理默认值，不强迫用户决策
- 不需要逐项填表——作者一段话讲完想法，Claude 自己提取 + 补全
- 给作者看草稿，让作者改（不要假装一次成）

---

## 2. 产出 5 个基础文件

收集到足够信息后，Claude 直接写出以下 5 个文件（写到 `<父目录>/books/<书名>/story/` 下）：

| 文件 | 内容 | schema 参考 |
|------|------|------------|
| `story_bible.md` | 世界观 / 主角 / 阵营与角色 / 地理环境 / 标题与梗概 | §03 基础文件规范 |
| `volume_outline.md` | 卷规划（至少第一卷）+ 黄金三章法则 | §03 |
| `book_rules.md` | YAML frontmatter（主角锁定 / 题材锁 / 禁忌 / 疲劳词）+ 正文（叙事视角 / 核心冲突驱动）| §03 |
| `current_state.md` | 第 0 章初始状态卡（7 个字段，全部填初始值）| §02 |
| `pending_hooks.md` | 伏笔池表头 + 初始伏笔（最近推进列填 `0`）| §02 |

**写法**：用 Write 工具一次写一个文件。每写完一个让作者看一眼（作者可以不看，但要给机会改）。

---

## 3. 自动初始化的 4 个空真相文件

5 个基础文件写完后，Claude 自动创建 4 个空表头的真相文件：

| 文件 | 初始内容 |
|------|---------|
| `particle_ledger.md` | 7 列表头 + `init-0` 行（`\| 0 \| - \| 0 \| 0 \| 0 \| 开书初始 \| init-0 \|`）|
| `subplot_board.md` | 9 列表头（无数据行）|
| `emotional_arcs.md` | 6 列表头（无数据行）|
| `character_matrix.md` | 3 子表骨架（### 角色档案 / ### 相遇记录 / ### 信息边界，每个子表只有表头）|

详细 schema 见 §02。

---

## 4. 初始化目录结构

```bash
BOOK_DIR=<父目录>/books/<书名>
mkdir -p "$BOOK_DIR/story/audits"
mkdir -p "$BOOK_DIR/story/snapshots"
mkdir -p "$BOOK_DIR/chapters"
```

---

## 5. 创建 snapshots/0/

5 个基础文件 + 4 个空真相文件全部就位后，立刻 cp 一份到 `snapshots/0/`，作为"第 0 章虚拟快照"——后续 rework 第 1 章时需要从这个快照恢复。

```bash
SNAP_DIR="$BOOK_DIR/story/snapshots/0"
mkdir -p "$SNAP_DIR"

cp "$BOOK_DIR/story/current_state.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/particle_ledger.md"     "$SNAP_DIR/"
cp "$BOOK_DIR/story/pending_hooks.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/chapter_summaries.md"   "$SNAP_DIR/" 2>/dev/null || echo "" > "$SNAP_DIR/chapter_summaries.md"
cp "$BOOK_DIR/story/subplot_board.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/emotional_arcs.md"      "$SNAP_DIR/"
cp "$BOOK_DIR/story/character_matrix.md"    "$SNAP_DIR/"
```

详细快照语义见 §10。

---

## 6. 创建空 chapters/index.json

```bash
echo "[]" > "$BOOK_DIR/chapters/index.json"
```

JSON 数组（不是 `{chapters: []}` 包裹），对齐原项目格式。

---

## 7. 完成后告诉作者下一步

Claude 完成上述全部步骤后，主动告诉作者：

> 「书已建好。下一步：
> 1. 看一眼 `story/story_bible.md` 和 `story/volume_outline.md`，不满意可以告诉我改
> 2. 准备好就说『写第 1 章』」

不要默认作者立刻开始写。给一个停下来审阅的窗口。

---

## 8. 与原项目的差异

| 原项目（Architect agent）| skill 模式 |
|------------------------|-----------|
| 单次 LLM call 一次性产出 5 个 section（temperature 0.8 / maxTokens 16384）| 多轮对话，按需问、按需产出 |
| 用 `=== SECTION: <name> ===` 切分输出 | 直接 Write 单个文件 |
| 严格 JSON schema 校验 | LLM 自己保证格式正确 + 作者审阅 |
| 必须收齐所有信息才开始 | 作者愿意省略的字段直接给默认值 |

skill 模式更轻——没有 Architect agent 的 system prompt 模板（节省几百行），靠对话自然推进。
