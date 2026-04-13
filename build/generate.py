#!/usr/bin/env python3
"""
generate.py — 拼接 src/ 模块生成平台适配版本

首要目标：生成 dist/CLAUDE.md（Claude Code 版）
后续：可按需生成 AGENTS.md（Codex CLI）或其他平台版本

用法：
    python3 generate.py                    # 默认生成 dist/CLAUDE.md
    python3 generate.py --platform codex   # 生成 dist/AGENTS.md
"""

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MODULE_ORDER = [
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
]

# 平台能力映射表（源文档用能力描述，生成时替换）
CAPABILITY_MAP = {
    "claude-code": {
        "读取文件内容": "使用 Read 工具",
        "定点修改文件": "使用 Edit 工具",
        "整体写入文件": "使用 Write 工具",
        "在文件中搜索内容": "使用 Grep 工具",
        "按模式查找文件": "使用 Glob 工具",
        "执行 shell 命令": "使用 Bash 工具",
        "列出目录内容": "使用 Bash 工具运行 `ls`",
    },
    "codex": {
        # 留空，由 Codex 自己填充
    },
}

PLATFORM_HEADERS = {
    "claude-code": """<!-- inkOS Writing System — Claude Code 版 -->
<!-- 本文件由 inkos-kit/build/generate.py 从 src/ 源模块生成 -->
<!-- 不要直接编辑此文件；请编辑 src/ 对应模块后重新生成 -->

""",
    "codex": """<!-- inkOS Writing System — Codex CLI 版 -->
<!-- 本文件由 inkos-kit/build/generate.py 从 src/ 源模块生成 -->

""",
}

PLATFORM_OUTPUT = {
    "claude-code": "dist/CLAUDE.md",
    "codex": "dist/AGENTS.md",
}


def apply_capability_map(text: str, mapping: dict) -> str:
    """把源文档中的能力级别描述替换为平台具体工具名（如需要）。"""
    for abstract, concrete in mapping.items():
        # 保守的替换：只替换明显引用工具的上下文
        # 当前源文档大部分已经是平台无关描述，此函数预留给未来使用
        pass
    return text


def generate(platform: str) -> str:
    src_dir = REPO_ROOT / "src"
    parts = [PLATFORM_HEADERS[platform]]

    mapping = CAPABILITY_MAP.get(platform, {})

    for module_name in MODULE_ORDER:
        module_path = src_dir / module_name
        if not module_path.exists():
            print(f"警告：模块缺失 {module_name}")
            continue
        text = module_path.read_text(encoding="utf-8")
        text = apply_capability_map(text, mapping)
        parts.append(text)
        parts.append("\n\n---\n\n")

    return "".join(parts).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="生成平台适配版本")
    parser.add_argument(
        "--platform",
        choices=["claude-code", "codex"],
        default="claude-code",
        help="目标平台（默认 claude-code）",
    )
    args = parser.parse_args()

    content = generate(args.platform)
    out_path = REPO_ROOT / PLATFORM_OUTPUT[args.platform]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"生成完成：{out_path} ({len(content.splitlines())} 行)")


if __name__ == "__main__":
    main()
