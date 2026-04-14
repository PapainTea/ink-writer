#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make-release.py — 打包用户侧发行 zip（只含用户需要的文件）

产出：dist/ink-writer-vX.Y.Z.zip（X.Y.Z 从 VERSION 读）

包含：
  - README.md
  - VERSION
  - scripts/{install.py, new-book.py, verify-chapter.py, merge-truth.py}
  - dist/CLAUDE.md
  - dist/.claude-modules/*.md

不包含（开发文件）：
  - src/*.md
  - build/*.py
  - tests/
  - CLAUDE.md（私有开发指引，已 gitignored）
  - .gitignore / .git/

用法：
    python3 build/make-release.py

依赖：Python stdlib 的 zipfile，零第三方。
"""

import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"

# 要打包的文件（相对于仓库根）
USER_FILES = [
    "README.md",
    "VERSION",
    "scripts/install.py",
    "scripts/new-book.py",
    "scripts/verify-chapter.py",
    "scripts/merge-truth.py",
    "dist/CLAUDE.md",
]

# 要打包的目录（递归）
USER_DIRS = [
    "dist/.claude-modules",
]


def main() -> int:
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    release_name = f"ink-writer-v{version}"
    out_zip = REPO_ROOT / "dist" / f"{release_name}.zip"
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    if out_zip.exists():
        out_zip.unlink()

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 单文件
        for rel in USER_FILES:
            src = REPO_ROOT / rel
            if not src.is_file():
                print(f"⚠️  缺失：{rel}，跳过", file=sys.stderr)
                continue
            arcname = f"{release_name}/{rel}"
            zf.write(src, arcname)

        # 目录递归
        for rel_dir in USER_DIRS:
            src_dir = REPO_ROOT / rel_dir
            if not src_dir.is_dir():
                print(f"⚠️  缺失目录：{rel_dir}，跳过", file=sys.stderr)
                continue
            for path in sorted(src_dir.rglob("*")):
                if path.is_file():
                    rel_path = path.relative_to(REPO_ROOT)
                    arcname = f"{release_name}/{rel_path}"
                    zf.write(path, arcname)

    total_files = len(zf.namelist()) if False else 0  # 可忽略
    size_kb = out_zip.stat().st_size / 1024
    print(f"✅ 打包完成：{out_zip.relative_to(REPO_ROOT)} ({size_kb:.1f} KB)")

    # 打印清单
    with zipfile.ZipFile(out_zip) as zf:
        print("\n清单：")
        for name in sorted(zf.namelist()):
            info = zf.getinfo(name)
            print(f"  {info.file_size:>6} B  {name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
