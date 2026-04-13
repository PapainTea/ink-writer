# 测试 fixture 书

这个目录下的"书"**不是作者的真实作品**，只是用来测试 `scripts/verify-chapter.py` 和未来其他脚本/功能的假书籍数据。

## 使用约定

- **任何自动化测试只能操作这里的 fixture 书，绝不能碰真实书籍**（镜源逆刻 / 长夜 / 作者其他作品）
- 真实书籍数据在 `books/`（gitignored，本地测试可读不可改）
- fixture 书可以自由修改、重建、删除

## 当前 fixtures

### test-book/

极简假书，章节只有 80 个 CJK 字符，target=100 / hardMin=80 / softMin=90。用于测字数分层检查的临界值：

| 测试场景 | 命令 | 期望 |
|---------|------|------|
| 字数 = hardMin 80，未 --allow-short | `verify-chapter.py ... test-book 1` | Layer 2 FAIL，提示用 --allow-short |
| 字数 = hardMin 80 + --allow-short | `verify-chapter.py ... test-book 1 --allow-short` | 全部通过 |

## 添加新 fixture 的规范

- 每个 fixture 目录下用极简内容（避免 fixture 本身占用大量仓库空间）
- 角色名/地名用通用占位符（不要 copy 真实作品内容）
- README 里说明该 fixture 测试什么场景
