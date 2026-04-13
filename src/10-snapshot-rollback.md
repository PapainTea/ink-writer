# 快照与回滚

快照是 inkOS 的"时间机器"，用于回滚错误章节、支持 rework、数据恢复。搞错快照语义会造成不可逆的数据污染，本章必读必守。

---

## 1. 快照语义（关键约定）

**`story/snapshots/N/` = 写完第 N 章之后当时的累积状态**

- 不是"最终结果的副本"
- 不是"第 N 章这一章的内容"
- 是"写完 ch N 这一刻，7 个真相文件应有的全貌"

例如：`snapshots/5/particle_ledger.md` 应该包含 ch0 初始化行 + ch1 ~ ch5 所有资源变动行，但绝不能包含 ch6+ 的数据。

---

## 2. 四条硬约束（任何操作/脚本必守）

1. **绝不向 `snapshots/N/` 写入第 N 章之后才出现的数据**
2. **绝不批量用一个最终结果覆盖所有快照**（所有快照会全部退化成"最终态"，历史丢失）
3. **绝不修改 `snapshots/N/` 下的任何已有文件**（它是当时的真实状态，不是可编辑的工作区）
4. **恢复 / 重建时必须逐章"递增生成"每个快照**（从 ch1 开始，按正文 diff 累积到 ch N）

违反任一条 = 快照系统作废 = 回滚不可信 = 未来 bug 调查无据可依。

---

## 3. 每章写完后的快照命令

Writer 流程末尾会自动调用 `state.snapshotState(bookId, N)`。手动执行等价命令：

```bash
BOOK_DIR=~/.inkos/data/books/<书名>
CHAPTER_NUM=<N>
SNAP_DIR="$BOOK_DIR/story/snapshots/$CHAPTER_NUM"
mkdir -p "$SNAP_DIR"

cp "$BOOK_DIR/story/current_state.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/particle_ledger.md"     "$SNAP_DIR/"
cp "$BOOK_DIR/story/pending_hooks.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/chapter_summaries.md"   "$SNAP_DIR/"
cp "$BOOK_DIR/story/subplot_board.md"       "$SNAP_DIR/"
cp "$BOOK_DIR/story/emotional_arcs.md"      "$SNAP_DIR/"
cp "$BOOK_DIR/story/character_matrix.md"    "$SNAP_DIR/"

# 审计 md 一并归档（如果 audits/ 目录存在）
if [ -d "$BOOK_DIR/story/audits" ]; then
  mkdir -p "$SNAP_DIR/audits"
  cp "$BOOK_DIR/story/audits/"*.md "$SNAP_DIR/audits/" 2>/dev/null || true
fi

# 注：skill 模式不创建 story/state/ 目录（原项目 pipeline 产物，已废弃）
```

---

## 4. 回滚到第 N 章的命令

**回滚前先做安全备份**：

```bash
BOOK_DIR=~/.inkos/data/books/<书名>
TS=$(date +%Y%m%d%H%M%S)
cp -R "$BOOK_DIR/story" "$BOOK_DIR/story.backup-$TS"
```

**反向 cp（从 snapshot 覆盖 current）**：

```bash
TARGET=<N>
SNAP_DIR="$BOOK_DIR/story/snapshots/$TARGET"

cp "$SNAP_DIR/current_state.md"       "$BOOK_DIR/story/"
cp "$SNAP_DIR/particle_ledger.md"     "$BOOK_DIR/story/"
cp "$SNAP_DIR/pending_hooks.md"       "$BOOK_DIR/story/"
cp "$SNAP_DIR/chapter_summaries.md"   "$BOOK_DIR/story/"
cp "$SNAP_DIR/subplot_board.md"       "$BOOK_DIR/story/"
cp "$SNAP_DIR/emotional_arcs.md"      "$BOOK_DIR/story/"
cp "$SNAP_DIR/character_matrix.md"    "$BOOK_DIR/story/"

# 审计 md 也一并恢复（覆盖现有 audits/）
if [ -d "$SNAP_DIR/audits" ]; then
  rm -rf "$BOOK_DIR/story/audits"
  cp -R "$SNAP_DIR/audits" "$BOOK_DIR/story/"
fi
```

**回滚后的章节清理**（回滚到 ch N 意味着 ch N+1 及之后作废）：

```bash
# 删除 > N 的正文
for f in "$BOOK_DIR/chapters/"*.md; do
  num=$(basename "$f" | cut -d_ -f1 | sed 's/^0*//')
  if [ "$num" -gt "$TARGET" ]; then
    rm "$f"
  fi
done

# 从 chapters/index.json 里删除 > N 的条目（用 jq 或手动编辑）
jq --argjson N "$TARGET" '.chapters |= map(select(.number <= $N))' \
   "$BOOK_DIR/chapters/index.json" > /tmp/idx.json \
   && mv /tmp/idx.json "$BOOK_DIR/chapters/index.json"

# 删除 > N 的快照
for d in "$BOOK_DIR/story/snapshots/"*/; do
  num=$(basename "$d")
  if [ "$num" -gt "$TARGET" ]; then
    rm -rf "$d"
  fi
done

# 清理 pipeline-cache/（可选，避免 stale）
rm -rf "$BOOK_DIR/story/runtime/pipeline-cache"

# 重建 memory.db（从恢复后的 markdown）
# 通过 CLI 或 runner.refreshMemoryFromRestoredState 完成
```

---

## 5. Rework 模式的 7 步完整流程

触发："重写第 N 章"。这是"回滚 + 重生成"的组合操作，由 `runner.reworkChapterFromPreviousSnapshot` 封装。

1. **预校验**：确认 `snapshots/(N-1)/` 存在且包含 `current_state.md` + `pending_hooks.md`（否则拒绝执行）
2. **restoreState(N-1)**：从 `snapshots/(N-1)/` 反向 cp 7 个真相文件到 `story/`
3. **删除章节正文**：删除 `chapters/000N_*.md` 以及所有 > N 的章节文件
4. **更新 index.json**：从 chapter index 删除 ch ≥ N 的条目
5. **清理 pipeline-cache**：`rm -rf story/runtime/pipeline-cache/N/` 避免 stale cache 干扰
6. **refreshMemoryFromRestoredState(N-1)**：重建 `memory.db`，让 SQLite 事实索引回到 ch N-1 的状态
7. **调 `_writeNextChapterLocked`**：跑完整 Writer pipeline 生成新的第 N 章（book lock 已持有，走 locked 版本避免死锁）

详细写章流程见 [04-write-pipeline.md](./04-write-pipeline.md)。
