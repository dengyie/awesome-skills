# 发布检查清单

在为 `production-code-quality-review` 创建新版本前，先按这份清单检查一遍。

## 1. 验证核心行为

运行：

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```

确认：

- 所有测试通过
- fixture 风格场景仍然符合预期

## 2. 验证主要入口

运行：

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
python3 production-code-quality-review/scripts/run-safe-checks.py --repo .
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format markdown
bash production-code-quality-review/scripts/verify-release.sh
```

确认：

- JSON 输出结构合理
- safe check 建议存在
- markdown 简报仍然可读且有用
- 一体化验证脚本可以顺利执行

## 3. 验证文档

检查：

- `README.md`
- `docs/usage/quickstart.md`
- `docs/usage/review-workflows.md`
- `docs/usage/examples.md`
- `docs/usage/faq.md`
- `docs/usage/troubleshooting.md`
- `docs/zh/README.zh-CN.md`
- `docs/zh/releases/README.zh-CN.md`

确认：

- 路径仍是最新的
- 命令可以实际运行
- 文案与真实仓库结构一致

## 4. 更新发布说明

更新：

- `CHANGELOG.md`
- `docs/releases/<version>.md`
- 如果有中文同步需求，也更新 `docs/zh/CHANGELOG.zh-CN.md`
- 如果有中文同步需求，也更新 `docs/zh/releases/<version>.zh-CN.md`

确认：

- 重点内容与真实 diff 一致
- breaking 或 notable change 已明确写出

## 5. 验证 Git 状态

运行：

```bash
git status --short
git log --oneline -1
```

确认：

- 只有预期内变更
- 最终提交信息是有意的

## 6. 发布

运行：

```bash
git push origin <branch>
gh release create <tag> --repo dengyie/awesome-skills --title "<title>" --notes-file docs/releases/<version>.md
```

发布后确认：

- release 页面渲染正常
- 远端分支已经同步
