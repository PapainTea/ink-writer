#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
new-book.py — 新建书目录骨架（跨平台）

行为：
  1. 定位 books root：优先 --books-root；否则向上查找 .ink-writer.yaml
  2. 在 books-root/<书名>/ 下创建 story/audits/、story/snapshots/、chapters/
  3. 写入空 chapters/index.json = []

不做：
  - 不写 story/*.md（交给 LLM 按 src/12-init-book.md 流程）
  - 不做交互式向导
  - 不 cp CLAUDE.md 到 <书名>/.claude/（books/ 共享一份即可）

用法：
    python new-book.py <书名> [--books-root PATH]

退出码：
    0  = 成功
    1  = 目录 / 文件操作失败
    2  = 未找到 .ink-writer.yaml
    3  = .ink-writer.yaml 解析失败 / booksRoot 不合法
    99 = 用法错误（书名非法等）
"""

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


FORBIDDEN_CHARS = set('/\\:*?"<>|')


def err(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def validate_name(name: str) -> str | None:
    if not name:
        return "书名不能为空"
    if name in (".", ".."):
        return f"书名不能是 {name!r}（路径穿越）"
    bad = [c for c in name if c in FORBIDDEN_CHARS]
    if bad:
        return f"书名含非法字符 {sorted(set(bad))!r}（Windows 禁用 / \\ : * ? \" < > |）"
    return None


def read_books_root_from_yaml(yaml_path: Path) -> str:
    """从 .ink-writer.yaml 抽取 booksRoot 字段（不依赖 PyYAML）。失败抛 ValueError。"""
    try:
        text = yaml_path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise ValueError(f"读取 {yaml_path} 失败：{e}")

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^booksRoot\s*:\s*(.+?)\s*$', line)
        if m:
            val = m.group(1).strip()
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            if not val:
                raise ValueError(f"{yaml_path} 的 booksRoot 字段为空")
            return val
    raise ValueError(f"{yaml_path} 缺少 booksRoot 字段")


def find_books_root(cwd: Path) -> Path | None:
    """沿 cwd 向上查找 .ink-writer.yaml。返回 yaml 文件路径（而非 booksRoot 字段值），找不到返 None。"""
    for p in [cwd, *cwd.parents]:
        candidate_a = p / "books" / ".ink-writer.yaml"
        if candidate_a.is_file():
            return candidate_a
        if p.name == "books":
            candidate_b = p / ".ink-writer.yaml"
            if candidate_b.is_file():
                return candidate_b
    return None


def resolve_books_root(books_root_arg: str | None) -> Path:
    """返回已校验的 books_root 绝对路径。失败时 SystemExit。"""
    if books_root_arg:
        books_root = Path(books_root_arg).expanduser().resolve()
    else:
        cwd = Path.cwd().resolve()
        yaml_path = find_books_root(cwd)
        if yaml_path is None:
            err(
                "未找到 .ink-writer.yaml。"
                "请先在目标父目录跑 `python <ink_writer>/scripts/install.py`，"
                "或用 --books-root <绝对路径> 显式指定。"
            )
            raise SystemExit(2)
        try:
            books_root_str = read_books_root_from_yaml(yaml_path)
        except ValueError as e:
            err(str(e))
            raise SystemExit(3)
        books_root = Path(books_root_str).expanduser().resolve()

    if not books_root.is_absolute():
        err(f"booksRoot 必须是绝对路径：{books_root}")
        raise SystemExit(3)
    if books_root.name != "books":
        err(f"booksRoot 目录名必须是 'books'（实际：{books_root.name}）")
        raise SystemExit(3)
    if not books_root.is_dir():
        err(f"booksRoot 目录不存在：{books_root}（可能被删了但 yaml 还在？）")
        raise SystemExit(3)
    return books_root


def main() -> int:
    parser = argparse.ArgumentParser(description="新建一本书的目录骨架")
    parser.add_argument("name", help="书名（作为目录名）")
    parser.add_argument(
        "--books-root",
        default=None,
        help="显式指定 books/ 目录的绝对路径；不传则从 cwd 向上找 .ink-writer.yaml",
    )
    args = parser.parse_args()

    name_err = validate_name(args.name)
    if name_err:
        err(name_err)
        return 99

    books_root = resolve_books_root(args.books_root)

    book_dir = books_root / args.name
    if book_dir.exists():
        err(f"书目录已存在：{book_dir}（拒绝覆盖）")
        return 1

    try:
        (book_dir / "story" / "audits").mkdir(parents=True)
        (book_dir / "story" / "snapshots").mkdir(parents=True)
        (book_dir / "chapters").mkdir(parents=True)
        (book_dir / "chapters" / "index.json").write_text("[]\n", encoding="utf-8")
    except OSError as e:
        err(f"创建目录骨架失败：{e}")
        return 1

    ok(f"书目录已创建：{book_dir}")
    print("下一步：")
    print(f'  cd "{book_dir}"')
    print("  claude")
    print('  # 然后在 claude 里说："新建书，我想写一本 XX"')
    print("  # LLM 会按 src/12 流程产出 5 个基础文件 + 4 个空真相文件 + snapshots/0/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
