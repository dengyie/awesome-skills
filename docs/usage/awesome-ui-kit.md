# awesome-ui-kit Usage Guide

The `awesome-ui-kit` skill guides AI coding assistants (Cursor, Claude Code, Codex, Pi) to assemble modern AI-native web pages (chat interfaces, RAG search engines, generative canvas, and agent consoles) using atomic, zero-blackbox single-file components from the `awesome-ui` repository.

## Core Capabilities

- **Multi-modal Prompt Inputs**: Auto-resizing textarea, multi-file attachments, and stop/generate switching (`ChatPromptInput`).
- **Smooth Streaming**: Jitter-free Markdown parsing with syntax highlighting and code copy (`StreamMarkdown`).
- **Reasoning Chains**: Collapsible DeepSeek R1 / OpenAI o1 thought processes with timers (`ThinkingBlock`).
- **Agent Tool Tracing**: Structured running, success, and error badges with drawer details (`ToolCallBadge`).
- **RAG & Search Sources**: Perplexity-style source citation grid with domain pills and snippets (`SourcesCitation`).
- **Live Preview Canvas**: Split-view sandboxed HTML/SVG/React preview (`ArtifactCanvas`).
- **Multi-Framework**: 1:1 parity across React (TSX), Vue 3 (SFC), and Vanilla Web Components.

## Quick Example

```tsx
import { ChatPromptInput } from "@/components/ai/ChatPromptInput";
import { StreamMarkdown } from "@/components/ai/StreamMarkdown";
import { ThinkingBlock } from "@/components/ai/ThinkingBlock";
import { AutoScrollAnchor } from "@/components/ai/AutoScrollAnchor";

## Related

- Back to [Skill Matrix](skill-matrix.md)
- Back to [Quickstart](quickstart.md)
