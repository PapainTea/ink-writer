#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install.py — ink_writer 用户侧一键安装脚本（跨平台）

行为：
  1. 在作者指定的父目录下创建 books/ 子目录
  2. 把 ink_writer 仓库的 dist/CLAUDE.md 复制到 books/CLAUDE.md
  3. 写入 books/.ink-writer.yaml 记录 booksRoot 绝对路径（若已存在则不动）

用法：
    python install.py [PARENT_DIR]

  PARENT_DIR 缺省 = cwd。作者 `cd ~/novels && python <ink>/scripts/install.py`
  或显式 `python <ink>/scripts/install.py ~/novels`。
  支持 `~` 展开（Windows cmd 下 shell 不展开，脚本自己 expanduser()）。

退出码：
    0  = 成功
    1  = 目录 / 文件操作失败
    2  = ink_writer 仓库损坏（dist/CLAUDE.md 不存在）
    99 = 用法错误
"""

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def err(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"⚠️  {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="在指定父目录下安装 ink_writer（创建 books/ + CLAUDE.md + .ink-writer.yaml）"
    )
    parser.add_argument(
        "parent_dir",
        nargs="?",
        default=None,
        help="books/ 的父目录（缺省 = cwd）",
    )
    args = parser.parse_args()

    ink_root = Path(__file__).resolve().parent.parent
    dist_claude = ink_root / "dist" / "CLAUDE.md"
    if not dist_claude.is_file():
        err(f"ink_writer 仓库损坏：{dist_claude} 不存在")
        return 2

    parent_dir_raw = args.parent_dir if args.parent_dir else str(Path.cwd())
    parent_dir = Path(parent_dir_raw).expanduser().resolve()

    books_dir = parent_dir / "books"
    try:
        books_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        err(f"创建 {books_dir} 失败：{e}")
        return 1

    target_claude = books_dir / "CLAUDE.md"
    if target_claude.exists():
        try:
            same = target_claude.read_bytes() == dist_claude.read_bytes()
        except OSError:
            same = False
        if not same:
            warn(
                f"将覆盖 {target_claude}"
                f"（此文件是 dist/CLAUDE.md 的副本，会在每次 install 时刷新为最新）"
            )
    try:
        shutil.copyfile(dist_claude, target_claude)
    except OSError as e:
        err(f"复制 CLAUDE.md 失败：{e}")
        return 1

    yaml_path = books_dir / ".ink-writer.yaml"
    if not yaml_path.exists():
        books_root_posix = books_dir.as_posix()
        created_at = datetime.now(timezone.utc).isoformat()
        yaml_content = (
            "# ink_writer books 根目录配置\n"
            "# LLM 和 new-book.py 通过此文件定位 books 根\n"
            f'booksRoot: "{books_root_posix}"\n'
            f'createdAt: "{created_at}"\n'
        )
        try:
            yaml_path.write_text(yaml_content, encoding="utf-8")
        except OSError as e:
            err(f"写入 {yaml_path} 失败：{e}")
            return 1

    ok(f"ink_writer 已安装到 {books_dir}")
    new_book_path = (ink_root / "scripts" / "new-book.py").as_posix()
    print("下一步：")
    print(f'  cd "{parent_dir}"')
    print(f'  python "{new_book_path}" 你的书名')
    return 0


if __name__ == "__main__":
    sys.exit(main())
