# awesome-ui-builder 使用指南

`awesome-ui-builder` 专门指导 AI 编程助手（Cursor、Claude Code、Codex、Pi 等）使用 `awesome-ui` 标准组件库快速装配现代 AI 原生页面（包括对话助手、RAG 搜索结果页、分屏实时画布、Agent 调用控制台等）。

## 核心能力

- **多模态输入框**：自适应高度输入框、多文件图片附件列表、生成/中断状态切换（`ChatPromptInput`）。
- **流畅流式打字**：防抖局部 Markdown 渲染、语法高亮与一键复制代码（`StreamMarkdown`）。
- **深度思考折叠条**：R1 / o1 推理模型思维链折叠展示与耗时计时（`ThinkingBlock`）。
- **工具调用卡片**：Agent 工具执行状态（运行/成功/失败）与入参返回值抽屉（`ToolCallBadge`）。
- **搜索引文网格**：Perplexity 风格来源引文卡片（`SourcesCitation`）。
- **分屏即席预览画布**：Claude Artifacts 风格沙盒即时预览（`ArtifactCanvas`）。
- **跨框架支持**：React (TSX)、Vue 3 (SFC)、Vanilla Web Components 三端 100% 对齐。
