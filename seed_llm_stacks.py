"""LLM 技术栈组 - 中文版"""
from db import get_db

STACKS = [
    ("Transformer 架构", "Attention Is All You Need (2017)，所有现代大模型的基石。Self-Attention / Multi-Head Attention / 位置编码原理", 0, 0),
    ("Attention 机制", "从 Seq2Seq 到 Attention 再到 Self-Attention 的演进。QKV 计算、缩放点积、多头注意力的设计哲学", 1, 0),
    ("大模型训练流程", "Pre-training -> SFT -> RLHF/DPO 三阶段训练范式。数据配比、Scaling Law、评估方法", 2, 0),
    ("LoRA 与高效微调", "Low-Rank Adaptation：冻结原权重，只训练低秩矩阵。QLoRA、AdaLoRA、DoRA 等变体", 3, 0),
    ("Prompt Engineering", "Zero-shot、Few-shot、Chain-of-Thought、ReAct 等提示词范式。结构化输出与模板管理", 4, 0),
    ("RAG 检索增强生成", "向量检索 + 大模型生成。文档切分、Embedding、检索、重排序、生成的完整链路", 5, 0),
    ("Agent 与 Function Calling", "LLM Agent 架构：思考-行动-观察循环。ReAct、Plan-Execute、多 Agent 协作", 6, 0),
    ("向量数据库", "Milvus / Pinecone / Weaviate / Chroma。HNSW/IVF 索引算法，相似度搜索与混合检索", 7, 0),
    ("LangChain 与 LlamaIndex", "LLM 应用开发框架对比。Chain/Agent/Tool/Retriever/Memory 核心抽象", 8, 0),
    ("模型部署与推理优化", "vLLM (PagedAttention) / TensorRT-LLM / llama.cpp。量化(GPTQ/AWQ/GGUF)、KV Cache", 9, 0),
    ("Embedding 与语义搜索", "BGE/GTE/E5/OpenAI Embedding 模型对比。语义相似度、Reranker 重排序、混合检索", 10, 0),
    ("LLM 评估体系", "MMLU/HumanEval/C-Eval 基准。自动化评估 vs 人工评估。RAGAS 评估框架", 11, 0),
    ("多模态大模型", "CLIP 视觉语言对齐、LLaVA/Qwen-VL/GPT-4V 架构。Sora/可灵视频生成原理", 12, 0),
    ("大模型安全与对齐", "RLHF/DPO 偏好对齐。Red-teaming 红队测试、越狱攻击与防御、内容安全", 13, 0),
]

def seed():
    db = get_db()
    tool = db.execute("SELECT id FROM tool WHERE name='面试储备'").fetchone()
    if not tool: print("Tool not found!"); return
    tid = tool["id"]

    for name, desc, order, deprecated in STACKS:
        db.execute(
            "INSERT INTO stack (tool_id, name, description, sort_order, is_deprecated, group_name) VALUES (?,?,?,?,?,'LLM')",
            (tid, name, desc, order, deprecated),
        )
    db.commit()
    db.close()
    print(f"LLM: {len(STACKS)} 个技术栈已创建")

if __name__ == "__main__":
    seed()
