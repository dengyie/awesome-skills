# AI Page Assembly Recipes (典型页面装配配方)

本文件提供 4 大高频 AI 原生页面的标准组装代码结构。

---

## 1. 经典对话流 (React / Next.js 示例)

```tsx
import React, { useState } from "react";
import { ChatPromptInput } from "@/components/ai/ChatPromptInput";
import { StreamMarkdown } from "@/components/ai/StreamMarkdown";
import { ThinkingBlock } from "@/components/ai/ThinkingBlock";
import { ToolCallBadge } from "@/components/ai/ToolCallBadge";
import { AutoScrollAnchor } from "@/components/ai/AutoScrollAnchor";
import { MessageActionToolbar } from "@/components/ai/MessageActionToolbar";
import { PromptChips } from "@/components/ai/PromptChips";

export function ChatView() {
  const [input, setInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);

  const handleSend = () => {
    // 1. 追加用户消息
    // 2. 触发流式后端 API
  };

  return (
    <div className="flex flex-col min-h-screen bg-zinc-950 text-zinc-100">
      {/* 消息历史流 */}
      <div className="flex-1 max-w-3xl w-full mx-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className="space-y-2">
            {msg.thinking && (
              <ThinkingBlock content={msg.thinking} isThinking={msg.isThinking} durationSeconds={msg.thinkingDuration} />
            )}
            {msg.tools?.map((t: any, i: number) => (
              <ToolCallBadge key={i} name={t.name} status={t.status} args={t.args} output={t.output} />
            ))}
            <StreamMarkdown content={msg.content} isStreaming={msg.isStreaming} />
            <MessageActionToolbar content={msg.content} role={msg.role} onRetry={handleSend} />
          </div>
        ))}
        <AutoScrollAnchor isStreaming={isGenerating} />
      </div>

      {/* 底部固定输入区 */}
      <div className="sticky bottom-0 bg-zinc-950/80 backdrop-blur border-t border-zinc-800 p-4">
        <PromptChips suggestions={["总结核心要点", "生成测试用例", "优化性能"]} onSelect={(p) => setInput(p)} />
        <ChatPromptInput value={input} onChange={setInput} onSubmit={handleSend} isGenerating={isGenerating} />
      </div>
    </div>
  );
}
```

---

## 2. Perplexity 风格 RAG 搜索问答 (Vue 3 示例)

```vue
<template>
  <div class="max-w-4xl mx-auto p-6 space-y-6 bg-zinc-950 text-zinc-100 min-h-screen">
    <!-- 1. 搜索引文网格 -->
    <SourcesCitation :sources="sources" />

    <!-- 2. 思考过程 -->
    <ThinkingBlock :content="reasoning" :is-thinking="isSearching" :duration-seconds="3.5" />

    <!-- 3. 正文流式解析 -->
    <div class="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-800">
      <StreamMarkdown :content="answer" :is-streaming="isStreaming" />
      <MessageActionToolbar :content="answer" role="assistant" @retry="fetchRAG" />
    </div>

    <!-- 4. 追问建议与输入 -->
    <PromptChips :suggestions="followUps" @select="(p) => query = p" />
    <ChatPromptInput v-model="query" :is-generating="isStreaming" @submit="fetchRAG" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import SourcesCitation from '@/components/ai/SourcesCitation.vue';
import ThinkingBlock from '@/components/ai/ThinkingBlock.vue';
import StreamMarkdown from '@/components/ai/StreamMarkdown.vue';
import MessageActionToolbar from '@/components/ai/MessageActionToolbar.vue';
import PromptChips from '@/components/ai/PromptChips.vue';
import ChatPromptInput from '@/components/ai/ChatPromptInput.vue';

const sources = ref([]);
const reasoning = ref("");
const answer = ref("");
const query = ref("");
const isSearching = ref(false);
const isStreaming = ref(false);
const followUps = ref(["来源可信度分析", "查看原始引用段落"]);

const fetchRAG = async () => {
  // RAG API 调用...
};
</script>
```

---

## 3. 分屏即席生成画布 (Canvas / Artifacts)

```tsx
import { useState } from "react";
import { ArtifactCanvas } from "@/components/ai/ArtifactCanvas";

export function StudioPage() {
  const [artifact, setArtifact] = useState<{ title: string; code: string; lang: string } | null>(null);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* 左侧对话区 */}
      <div className="flex-1 overflow-y-auto">
        {/* 对话与按钮触发打开 Artifact */}
        <button
          onClick={() => setArtifact({ title: "GeneratedCard.tsx", code: "export default () => <div>Hello</div>", lang: "react" })}
          className="p-2 bg-zinc-800 rounded-lg text-xs"
        >
          查看生成结果 ↗
        </button>
      </div>

      {/* 右侧 Artifact 分屏沙盒 */}
      {artifact && (
        <ArtifactCanvas
          title={artifact.title}
          code={artifact.code}
          language={artifact.lang}
          isOpen={Boolean(artifact)}
          onClose={() => setArtifact(null)}
        />
      )}
    </div>
  );
}
```
