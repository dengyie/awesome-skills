# vX.Y.Z：Release Title

## 摘要

用一到两段简短文字说明这个版本对用户或维护者的价值。

重点写为什么发布，而不是逐文件罗列。

## 具体变化

### 领域一

- 说明行为或文档变化。
- 说明对用户或维护者的影响。

### 领域二

- 只记录真正值得发布说明强调的变化。

## 验证

验证命令：

```bash
python3 -m unittest discover production-code-quality-review/tests -v
bash production-code-quality-review/scripts/verify-release.sh
```

## 备注

如有兼容性、迁移或后续事项，在这里说明。
