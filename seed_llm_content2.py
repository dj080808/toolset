# -*- coding: utf-8 -*-
"""LLM 笔记与面试题 - 应用层模块 (P2-P3)"""
from db import get_db


def insert_note(db, stack_name, title, content, tags):
    sid = db.execute("SELECT id FROM stack WHERE name=? AND group_name='LLM'", (stack_name,)).fetchone()["id"]
    db.execute("INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'note')",
               (sid, title, content, tags))


def insert_iv(db, stack_name, title, content, tags):
    sid = db.execute("SELECT id FROM stack WHERE name=? AND group_name='LLM'", (stack_name,)).fetchone()["id"]
    db.execute("INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'interview')",
               (sid, title, content, tags))


def seed():
    db = get_db()

    # ==================== Prompt Engineering ====================
    insert_note(db, "Prompt Engineering",
        "Prompt Engineering 核心技巧",
        "## 基础范式\n\n"
        "| 范式 | 说明 | 示例 |\n"
        "|------|------|------|\n"
        "| Zero-shot | 不给例子，直接问 | 翻译：Hello -> |\n"
        "| Few-shot | 给 2~5 个例子 | 英->中: Hello->你好, World->世界, AI-> |\n"
        "| Chain-of-Thought | 加一句「让我们一步一步思考」| 引导模型逐步推理 |\n"
        "| ReAct | Reason + Act 交替 | 思考->行动->观察->思考...|\n\n"
        "## Chain-of-Thought (CoT)\n\n"
        "不加 CoT：「5 个苹果，买 3 个，吃 2 个，剩几个？」模型可能猜错\n"
        "加 CoT：「让我们一步步思考。一开始 5 个，买 3 个后 8 个，吃 2 个剩 6 个。答案：6 个。」\n\n"
        "CoT 在 GSM8K 数学题上把准确率从约 18% 提到了约 58%。\n\n"
        "## 结构化输出\n\n"
        "```python\n"
        "response_format={'type': 'json_object'}  # 强制 JSON 输出\n"
        "```\n\n"
        "## 面试重点\n\n"
        "1. CoT 能显著提升推理任务准确率\n"
        "2. Few-shot 例子要高质量 + 多样性\n"
        "3. Prompt 不是写得越详细越好，而是给足够的信息约束但不给错误引导\n"
        "4. 实际项目中用 Prompt Template 管理，配合 A/B 测试调优",
        "Prompt,Few-shot,CoT,ReAct,结构化输出"
    )

    # ==================== RAG 检索增强生成 ====================
    insert_note(db, "RAG 检索增强生成",
        "RAG 原理与架构",
        "## RAG 解决的核心问题\n\n"
        "大模型的三个局限：\n"
        "1. **知识截止日期**：GPT-4 的知识到 2023 年 4 月\n"
        "2. **幻觉**：模型会编造不存在的事实\n"
        "3. **私有知识**：模型不知道公司内部文档\n\n"
        "RAG 的解法：**先检索相关信息，再让大模型基于这些信息回答。**\n\n"
        "## RAG 架构\n\n"
        "```\n"
        "用户提问 -> Embedding -> 向量检索 -> Top-K 相关文档片段 -> LLM 基于文档生成答案\n"
        "```\n\n"
        "## 关键环节\n\n"
        "| 环节 | 技术 | 难点 |\n"
        "|------|------|------|\n"
        "| 文档解析 | PDF/Word/HTML -> 纯文本 | 表格、图片、复杂排版 |\n"
        "| 文本切分 | 固定长度/语义切分/递归切分 | 切分粒度的权衡 |\n"
        "| Embedding | BGE/GTE/OpenAI Embedding | 不同领域需要不同模型 |\n"
        "| 向量检索 | HNSW/IVF | 精度 vs 速度 |\n"
        "| 重排序 | Reranker | 第一步召回不够精确 |\n"
        "| 生成 | LLM + 引用溯源 | 幻觉/不相关答案 |\n\n"
        "## 提高 RAG 效果的实践\n\n"
        "1. **HyDE（假设性文档嵌入）**：先让 LLM 生成一个假设性答案，用这个答案去检索（而非用问题直接检索）\n"
        "2. **多路召回**：Embedding 检索 + BM25 关键词检索 -> RRF 融合\n"
        "3. **Reranker 重排序**：粗召回 100 条 -> Reranker 精排 Top 5\n"
        "4. **引用溯源**：生成的答案中标注每句话引用了哪个文档片段",
        "RAG,检索,向量,Embedding,幻觉"
    )

    insert_iv(db, "RAG 检索增强生成",
        "RAG 的原理是什么？如何优化 RAG 的检索效果？",
        "## RAG 原理\n\n"
        "用户问题 -> Embedding -> 向量检索 -> Top-K 相关文档 -> LLM 基于文档生成答案\n\n"
        "## 优化手段\n\n"
        "1. **切分策略**：递归切分 + Chunk 重叠（10%），保证语义完整\n"
        "2. **Embedding 选型**：中文用 BGE/GTE，不用 OpenAI（延迟和成本高）\n"
        "3. **多路召回**：向量检索 + BM25 关键词检索 -> RRF 融合\n"
        "4. **Reranker**：粗排 Top 100 -> 精排 Top 5\n"
        "5. **HyDE**：先让 LLM 生成假设答案，用假设答案检索（而非问题）\n"
        "6. **Query 改写**：让 LLM 把用户口语问题改写为正式检索查询",
        "RAG,检索,优化,高频"
    )

    # ==================== Agent 与 Function Calling ====================
    insert_note(db, "Agent 与 Function Calling",
        "LLM Agent 架构与 Function Calling",
        "## Agent 的核心循环\n\n"
        "```\n"
        "思考(Thought) -> 行动(Action) -> 观察(Observation) -> 思考 -> ... -> 最终答案\n"
        "```\n\n"
        "LLM 是大脑（决定下一步做什么），Tools 是手（执行具体操作）。\n\n"
        "## ReAct 模式\n\n"
        "ReAct（Reasoning + Acting）是当前 Agent 的主流范式。模型在推理和行动之间交替，"
        "观察结果后进行下一步推理。\n\n"
        "## Function Calling\n\n"
        "LLM 输出结构化的函数调用意图（函数名 + JSON 参数），而非文本。"
        "框架解析意图 -> 执行函数 -> 把结果返回 LLM -> 继续对话。\n\n"
        "```python\n"
        "tools = [{\n"
        "    \"type\": \"function\",\n"
        "    \"function\": {\n"
        "        \"name\": \"get_weather\",\n"
        "        \"description\": \"获取指定城市的天气\",\n"
        "        \"parameters\": {\n"
        "            \"properties\": {\"city\": {\"type\": \"string\"}},\n"
        "            \"required\": [\"city\"]\n"
        "        }\n"
        "    }\n"
        "}]\n\n"
        "response = client.chat.completions.create(\n"
        "    model=\"gpt-4\", messages=[...], tools=tools, tool_choice=\"auto\"\n"
        ")\n"
        "```\n\n"
        "## Agent 的挑战\n\n"
        "1. **幻觉放大**：Agent 的每一步都可能出错 -> 多步后错误累积\n"
        "2. **无限循环**：模型在 Think-Act-Observe 中打转，消耗大量 Token\n"
        "3. **安全风险**：工具调用的参数可能被 Prompt Injection 操控",
        "Agent,ReAct,Function Calling,工具调用"
    )

    insert_iv(db, "Agent 与 Function Calling",
        "AI Agent 和传统 ChatBot 有什么区别？Agent 的核心架构是什么？",
        "## 核心区别\n\n"
        "**ChatBot**：接收消息 -> 思考 -> 回复。一轮交互。\n\n"
        "**Agent**：接收目标 -> 思考 -> 行动 -> 观察结果 -> 再思考 -> 再行动 -> ... -> 达成目标。多轮自主循环。\n\n"
        "## Agent 核心架构\n\n"
        "```\n"
        "Thought -> Action -> Observation -> Thought -> ... -> Final Answer\n"
        "```\n\n"
        "LLM 是大脑，Tools 是手。\n"
        "- 大脑决定下一步做什么\n"
        "- 手执行具体操作（搜索、调 API、读文件...）\n\n"
        "## 关键机制\n\n"
        "**Function Calling**：LLM 输出结构化的函数调用意图（函数名 + JSON 参数），"
        "而非文本——框架解析意图->执行函数->把结果返回 LLM->继续对话。",
        "Agent,ChatBot,Function Calling,高频"
    )

    # ==================== 向量数据库 ====================
    insert_note(db, "向量数据库",
        "向量数据库原理与选型",
        "## 为什么需要向量数据库\n\n"
        "传统数据库：WHERE name = 'John'（精确匹配）\n"
        "向量数据库：找出与 [0.1, 0.3, ...] 最相似的 Top-10 个向量（语义相似度搜索）\n\n"
        "## HNSW 索引（最常用）\n\n"
        "HNSW = Hierarchical Navigable Small World：\n"
        "- 高层（跳表）：节点少 -> 快速跳到目标区域\n"
        "- 低层（稠密图）：节点多 -> 在目标区域内精确搜索\n\n"
        "## 主流向量数据库对比\n\n"
        "| 数据库 | 类型 | 特点 |\n"
        "|--------|------|------|\n"
        "| Milvus | 分布式 | 国产，性能强，功能全面 |\n"
        "| Pinecone | 云服务 | 免运维，按量付费 |\n"
        "| Weaviate | 开源+云 | GraphQL API，Hybrid Search |\n"
        "| Chroma | 嵌入式 | 轻量，适合原型开发 |\n"
        "| Elasticsearch 8.x+ | 搜索引擎 | 已有 ES 可用，不用新引入 |\n\n"
        "## 选型建议\n\n"
        "- 原型开发 -> Chroma（pip install 就能用）\n"
        "- 生产级、大规模 -> Milvus（分布式、持久化）\n"
        "- 不想运维 -> Pinecone / Zilliz Cloud\n"
        "- 已经有 ES -> ES 8.x+ 的向量检索够用中等规模",
        "向量数据库,Milvus,HNSW,索引,选型"
    )

    # ==================== LangChain 与 LlamaIndex ====================
    insert_note(db, "LangChain 与 LlamaIndex",
        "LLM 应用开发框架对比",
        "## LangChain\n\n"
        "LLM 应用开发的事实标准框架，提供一套标准化抽象：\n\n"
        "| 组件 | 说明 |\n"
        "|------|------|\n"
        "| Model | LLM/ChatModel/Embedding 的统一接口 |\n"
        "| Prompt | Prompt Template 管理 |\n"
        "| Chain | 串联多个组件的管道 |\n"
        "| Retriever | 文档检索器 |\n"
        "| Tool | 工具（搜索、计算器、API 调用）|\n"
        "| Agent | 决策-行动循环 |\n"
        "| Memory | 对话记忆 |\n\n"
        "## LlamaIndex\n\n"
        "LlamaIndex 专注数据索引和检索：数据加载 -> 索引构建 -> 查询。"
        "RAG 能力更强（递归检索、子问题分解）。\n\n"
        "## 对比\n\n"
        "| 维度 | LangChain | LlamaIndex |\n"
        "|------|-----------|------------|\n"
        "| 定位 | 通用 LLM 应用框架 | 数据索引和检索 |\n"
        "| 核心能力 | Chain/Agent/Tool/Memory | 数据->索引->查询 |\n"
        "| Agent | 核心能力 | 基础支持 |\n"
        "| 学习曲线 | 陡（抽象多）| 平缓 |\n"
        "| 适合场景 | 复杂 Agent 应用 | RAG 知识库应用 |\n\n"
        "> 两者可混用：用 LlamaIndex 做检索，用 LangChain 做 Agent 和 Chain 编排。",
        "LangChain,LlamaIndex,框架,对比"
    )

    # ==================== 模型部署与推理优化 ====================
    insert_note(db, "模型部署与推理优化",
        "大模型推理优化技术",
        "## 推理框架\n\n"
        "| 框架 | 特点 | 适用场景 |\n"
        "|------|------|----------|\n"
        "| vLLM | PagedAttention，高吞吐 | 在线 API 服务 |\n"
        "| TensorRT-LLM | NVIDIA 官方，极致优化 | GPU 集群推理 |\n"
        "| llama.cpp | C++ 实现，CPU/GPU 混合 | 消费级硬件部署 |\n"
        "| Ollama | llama.cpp 封装，一键部署 | 本地开发/测试 |\n\n"
        "## vLLM 的 PagedAttention\n\n"
        "传统方式：每个请求预留固定长度的 KV Cache -> 碎片化浪费显存。\n"
        "PagedAttention：把 KV Cache 分成 page（类似 OS 虚拟内存分页），多个请求共享物理 page。\n"
        "效果：显存利用率从 20-40% -> 接近 100%，吞吐量提升 2-4 倍。\n\n"
        "## 量化技术\n\n"
        "| 方法 | 精度 | 模型大小 | 推理速度 |\n"
        "|------|------|----------|----------|\n"
        "| FP16 | 最高 | 100%（基线）| 基线 |\n"
        "| GPTQ | 很高 | ~25% | 快 |\n"
        "| AWQ | 很高 | ~25% | 快 |\n"
        "| GGUF (llama.cpp) | 较好 | 25-50% | CPU 友好 |\n"
        "| bitsandbytes 8-bit | 高 | ~50% | 中 |\n\n"
        "## 推理优化 Checklist\n\n"
        "| 技术 | 作用 |\n"
        "|------|------|\n"
        "| KV Cache | 避免重复计算历史 token 的 Key/Value |\n"
        "| Continuous Batching | 请求到达就处理，不等凑够 batch |\n"
        "| FlashAttention | IO-aware 算法，减少显存读写 |\n"
        "| 量化 | 减少显存占用，加速推理 |\n"
        "| 投机采样 | 小模型生成 draft -> 大模型验证，加速 2-3x |\n\n"
        "> 面试加分：vLLM 相比 HuggingFace 的吞吐量优势来自 PagedAttention + Continuous Batching。",
        "推理,vLLM,量化,PagedAttention,KV Cache"
    )

    insert_iv(db, "模型部署与推理优化",
        "大模型部署有哪些优化手段？vLLM 为什么比 HuggingFace 快？",
        "## 关键优化技术\n\n"
        "1. **量化**：FP16 -> 4-bit，模型缩小 75%，推理加速 2-4x\n"
        "2. **KV Cache**：缓存历史 token 的 Key/Value，避免重复计算\n"
        "3. **FlashAttention**：用 SRAM 替代 HBM 做中间计算，减少显存 IO\n"
        "4. **Continuous Batching**：请求到达就处理，不等 batch 凑满\n\n"
        "## vLLM 为什么快\n\n"
        "**PagedAttention**：把 KV Cache 按 page 管理（类似 OS 虚拟内存）。"
        "多个请求共享物理 page，显存利用率从 ~30% 提升到接近 100%，吞吐量提升 2-4 倍。\n\n"
        "**Continuous Batching**：传统方式是等一个 batch 的所有请求都完成才处理下一批。"
        "vLLM 有请求完成就腾出位置给新请求。",
        "部署,vLLM,PagedAttention,量化,高频"
    )

    # ==================== Embedding 与语义搜索 ====================
    insert_note(db, "Embedding 与语义搜索",
        "Embedding 模型与语义搜索实战",
        "## Embedding 是什么\n\n"
        "将文本转换为固定维度的浮点数向量，语义相近的文本向量距离近。\n\n"
        "## 主流 Embedding 模型\n\n"
        "| 模型 | 维度 | 中文能力 | 特点 |\n"
        "|------|------|----------|------|\n"
        "| BGE (BAAI) | 768/1024 | 极好 | 中文最强开源，各种尺寸 |\n"
        "| GTE (Alibaba) | 768/1024 | 极好 | 阿里开源，中英文均衡 |\n"
        "| E5 (Microsoft) | 768/1024 | 一般 | 英文为主 |\n"
        "| OpenAI text-embedding | 1536/3072 | 好 | 商业 API，通用性强 |\n\n"
        "## 语义搜索流程\n\n"
        "```\n"
        "离线建库：文档 -> Embedding 模型 -> 向量 -> 存入向量数据库\n"
        "在线查询：用户提问 -> Embedding -> 向量库 Top-K 检索 -> 返回相关文档\n"
        "重排序：Top-K 候选 -> Reranker -> 精排 Top-N -> 给 LLM 生成\n"
        "```\n\n"
        "## Reranker 的作用\n\n"
        "Embedding 检索是双塔模型（问题和文档分别编码），精度不够高。"
        "Reranker 是交叉编码器（问题和文档一起输入），精度高但速度慢。\n\n"
        "粗排（Embedding，速度快）：10000 个文档 -> Top 100\n"
        "精排（Reranker，精度高）：100 个候选 -> Top 5",
        "Embedding,BGE,Reranker,语义搜索"
    )

    db.commit()
    print("P2-P3 (Prompt / RAG / Agent / VectorDB / LangChain / Deployment / Embedding) 已写入")


if __name__ == "__main__":
    seed()
