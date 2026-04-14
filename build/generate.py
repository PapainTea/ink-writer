#!/usr/bin/env python3
"""
generate.py — 从 src/ 模块拼接生成 dist/ 下的平台适配版本

Claude Code 版（默认）：
  dist/CLAUDE.md                 核心（§00 + §01 + §09 + core-hard-bans + §13，~8-10k chars）
  dist/.claude-modules/
    write.md                     §02+§03+§04+§05+§08+§11（写章流程）
    audit.md                     §02+§06
    revise.md                    §02+§07
    init.md                      §12
    snapshot.md                  §10

Codex CLI 版：
  dist/AGENTS.md                 单文件（拼接所有 src/*.md，维持原行为，由 Codex 自行改造）

用法：
    python3 generate.py                          # 默认生成 Claude Code 版（多文件）
    python3 generate.py --platform codex         # 生成 Codex 单文件
"""

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
DIST_DIR = REPO_ROOT / "dist"

# Claude Code 核心 CLAUDE.md（常驻加载）
CORE_MODULES = [
    "00-system-role.md",
    "01-data-structure.md",
    "09-post-write-validation.md",
    "core-hard-bans.md",
    "13-commands.md",
]

# Claude Code 按需加载模块（LLM 在触发对应意图时 Read）
ON_DEMAND_BUNDLES = {
    "write.md": [
        "02-truth-schema.md",
        "03-foundation-files.md",
        "04-write-pipeline.md",
        "05-writing-rules.md",
        "08-settlement.md",
        "11-hook-governance.md",
    ],
    "batch-write.md": [
        "14-batch-write.md",
    ],
    "audit.md": [
        "02-truth-schema.md",
        "06-audit-system.md",
    ],
    "revise.md": [
        "02-truth-schema.md",
        "07-revision-modes.md",
    ],
    "init.md": [
        "12-init-book.md",
    ],
    "snapshot.md": [
        "10-snapshot-rollback.md",
    ],
}

# Codex 单文件模式的完整模块顺序（不拆分）
CODEX_MODULE_ORDER = [
    "00-system-role.md",
    "01-data-structure.md",
    "02-truth-schema.md",
    "03-foundation-files.md",
    "04-write-pipeline.md",
    "05-writing-rules.md",
    "06-audit-system.md",
    "07-revision-modes.md",
    "08-settlement.md",
    "09-post-write-validation.md",
    "10-snapshot-rollback.md",
    "11-hook-governance.md",
    "12-init-book.md",
    "13-commands.md",
    "14-batch-write.md",
]

CLAUDE_CORE_HEADER = """<!-- inkOS Writing System — Claude Code 版（核心 CLAUDE.md）-->
<!-- 本文件由 build/generate.py 从 src/ 源模块生成 -->
<!-- 不要直接编辑此文件；请编辑 src/ 对应模块后重新生成 -->
<!-- 按需模块位于 .claude-modules/ 目录下，LLM 触发对应意图时自动 Read -->

"""

CLAUDE_MODULE_HEADER_TEMPLATE = """<!-- inkOS 按需加载模块：{name} -->
<!-- 当你读到这份文件时，说明用户触发了 {name} 对应的意图 -->
<!-- 请严格按本文件定义的流程执行 -->

"""

CODEX_HEADER = """<!-- inkOS Writing System — Codex CLI 版 -->
<!-- 本文件由 build/generate.py 从 src/ 源模块生成 -->

"""


def concat_modules(module_names: list[str]) -> str:
    parts: list[str] = []
    for name in module_names:
        path = SRC_DIR / name
        if not path.exists():
            print(f"警告：模块缺失 {name}")
            continue
        parts.append(path.read_text(encoding="utf-8"))
        parts.append("\n\n---\n\n")
    return "".join(parts).rstrip() + "\n"


def generate_claude_code() -> None:
    # 清理旧的 .claude-modules/ 避免遗留 stale 文件
    modules_dir = DIST_DIR / ".claude-modules"
    if modules_dir.exists():
        shutil.rmtree(modules_dir)
    modules_dir.mkdir(parents=True)

    # 核心 CLAUDE.md
    core = CLAUDE_CORE_HEADER + concat_modules(CORE_MODULES)
    core_path = DIST_DIR / "CLAUDE.md"
    core_path.parent.mkdir(parents=True, exist_ok=True)
    core_path.write_text(core, encoding="utf-8")
    print(f"生成完成：{core_path.relative_to(REPO_ROOT)} "
          f"({len(core):,} chars, {len(core.splitlines())} 行)")

    # 按需模块
    total_modules_size = 0
    for module_file, src_modules in ON_DEMAND_BUNDLES.items():
        header = CLAUDE_MODULE_HEADER_TEMPLATE.format(name=module_file)
        content = header + concat_modules(src_modules)
        out_path = modules_dir / module_file
        out_path.write_text(content, encoding="utf-8")
        total_modules_size += len(content)
        print(f"  按需模块：{out_path.relative_to(REPO_ROOT)} "
              f"({len(content):,} chars)")
    print(f"按需模块合计：{total_modules_size:,} chars")


def generate_codex() -> None:
    content = CODEX_HEADER + concat_modules(CODEX_MODULE_ORDER)
    out_path = DIST_DIR / "AGENTS.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"生成完成：{out_path.relative_to(REPO_ROOT)} "
          f"({len(content):,} chars, {len(content.splitlines())} 行)")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 dist/ 下的平台适配版本")
    parser.add_argument(
        "--platform",
        choices=["claude-code", "codex"],
        default="claude-code",
        help="目标平台（默认 claude-code）",
    )
    args = parser.parse_args()

    if args.platform == "claude-code":
        generate_claude_code()
    else:
        generate_codex()


if __name__ == "__main__":
    main()
