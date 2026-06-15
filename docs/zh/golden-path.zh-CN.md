# 黄金路径

如果你只想走最短路径，按下面这套做就够了。

## 1. 安装

```bash
bash production-code-quality-review/scripts/install-local-skill.sh
```

默认会安装到 `~/.agents/skills`。如果你明确需要第二份旧路径副本，再设置 `INSTALL_LEGACY_CODEX_COPY=1`。
安装后的副本会记录来源 checkout，后续 `update-local-skill.sh` 可以安全回源更新。

## 2. 收集上下文

```bash
python3 production-code-quality-review/scripts/collect-review-context.py --repo .
```

## 3. 查看紧凑简报

```bash
python3 production-code-quality-review/scripts/review-entrypoint.py --repo . --format compact
```

## 4. 让 Codex 开始审查

```text
Use $production-code-quality-review to review this change for production correctness and merge readiness.
```

## 5. 验证

```bash
python3 -m unittest discover production-code-quality-review/tests -v
```
