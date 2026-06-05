# -*- coding: utf-8 -*-
"""LLM 笔记与面试题 - 进阶模块 (P4)"""
from db import get_db


def insert_note(db, stack_name, title, content, tags):
    sid = db.execute("SELECT id FROM stack WHERE name=? AND group_name='LLM'", (stack_name,)).fetchone()["id"]
    db.execute("INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?,?,?,?,'note')",
               (sid, title, content, tags))


def seed():
    db = get_db()

    # ==================== LLM 评估体系 ====================
    insert_note(db, "LLM 评估体系",
        "大模型如何评估 - 方法体系",
        "## 评估维度\n\n"
        "| 维度 | 评估什么 | 代表基准 |\n"
        "|------|----------|----------|\n"
        "| 知识 | 模型的知识广度与深度 | MMLU（57 学科）、C-Eval（中文）|\n"
        "| 推理 | 逻辑推理、数学 | GSM8K（小学数学）、MATH |\n"
        "| 代码 | 代码生成与理解 | HumanEval、MBPP |\n"
        "| 中文 | 中文能力 | CMMLU、C-Eval、C3 |\n"
        "| 对话 | 多轮对话质量 | MT-Bench、Chatbot Arena |\n"
        "| 安全 | 有害内容、偏见 | TruthfulQA |\n\n"
        "## 自动化评估 vs 人工评估\n\n"
        "自动化评估：MMLU 4 选 1 选择题 -> 自动判分。HumanEval 生成代码 -> 跑测试用例 -> pass@k。\n"
        "人工评估（更可靠但成本高）：Chatbot Arena 两个模型回答 -> 人类盲选 -> Elo 评分。\n\n"
        "## RAG 评估框架（RAGAS）\n\n"
        "RAG 系统需要专门的评估维度：\n\n"
        "| 指标 | 含义 |\n"
        "|------|------|\n"
        "| Faithfulness | 答案是否基于检索到的文档（是否幻觉）|\n"
        "| Answer Relevancy | 答案是否回答了问题 |\n"
        "| Context Relevancy | 检索到的文档是否和问题相关 |\n"
        "| Context Recall | 相关文档是否都被检索到了 |\n\n"
        "## 评估的陷阱\n\n"
        "1. **数据污染**：训练数据中包含了测试题目 -> 评估分数虚高\n"
        "2. **Goodhart 定律**：当一个指标成为目标，它就不再是一个好指标\n"
        "3. **英语偏见**：大多数基准是英语的，对中文模型不公平\n"
        "4. **静态评估**：基准是固定的，不能反映真实场景的开放性问题",
        "评估,MMLU,RAGAS,基准"
    )

    # ==================== 多模态大模型 ====================
    insert_note(db, "多模态大模型",
        "多模态大模型技术路线",
        "## 多模态的定义\n\n"
        "能同时理解和生成多种数据类型的模型（文本 + 图像 + 语音 + 视频）。\n\n"
        "## CLIP 范式（图文对齐）\n\n"
        "```\n"
        "图像 -> Image Encoder -> 图像向量\n"
        "文本 -> Text Encoder  -> 文本向量\n\n"
        "训练目标：匹配的图像-文本对的向量距离近；不匹配的远离。\n"
        "「一只狗在草地上」-> 应与狗的照片相似度高，与猫的照片相似度低\n"
        "```\n\n"
        "## 主流多模态模型\n\n"
        "| 模型 | 模态 | 特点 |\n"
        "|------|------|------|\n"
        "| GPT-4V/o | 文+图 | 最强大，闭源 |\n"
        "| Gemini | 文+图+音+视频 | Google 原生多模态 |\n"
        "| LLaVA | 文+图 | 开源，学术友好 |\n"
        "| Qwen-VL | 文+图 | 阿里，中文最强 |\n"
        "| CogVLM | 文+图 | 清华，视觉理解深度好 |\n\n"
        "## LLaVA 架构\n\n"
        "```\n"
        "图片 -> Vision Encoder (CLIP ViT) -> Visual Tokens\n"
        "                                         |\n"
        "文本 -> Tokenizer -> Text Tokens ----- 拼接 ---> LLM -> 生成回复\n"
        "```\n\n"
        "本质：把图片「翻译」成 LLM 能理解的 Token 序列，然后和文本 Token 拼在一起输入 LLM。\n\n"
        "## 视频生成\n\n"
        "Sora（OpenAI）/ 可灵（快手）是视频生成的里程碑：\n"
        "- 核心思路：Diffusion Transformer (DiT)\n"
        "- 视频压缩为时空 Latent -> Transformer 在 Latent 空间做扩散 -> 解码回视频\n\n"
        "> 面试重点：多模态的本质是「对齐」——把不同模态的数据映射到同一个语义空间。CLIP 是图文对齐的经典范式。",
        "多模态,CLIP,LLaVA,Sora,对齐"
    )

    # ==================== 大模型安全与对齐 ====================
    insert_note(db, "大模型安全与对齐",
        "大模型安全与对齐技术",
        "## 对齐（Alignment）\n\n"
        "让模型的价值观和人类一致——做人类期望的事。\n\n"
        "## RLHF 对齐流程\n\n"
        "```\n"
        "1. SFT 模型（会遵循指令，但可能有害）\n"
        "2. 收集偏好数据：同一个 prompt，生成多个 response，人工排序\n"
        "3. 训练 Reward Model：学会好回答打高分、坏回答打低分\n"
        "4. PPO 优化：奖励模型打分 + KL 惩罚（防止偏离太远）\n"
        "5. 对齐后的模型\n"
        "```\n\n"
        "## DPO 替代 RLHF\n\n"
        "DPO 不需要单独的 Reward Model，直接从偏好数据中优化：\n"
        "- RLHF: Preference Data -> Reward Model -> PPO -> Policy\n"
        "- DPO: Preference Data -> Policy（一步到位）\n"
        "优势：更简单、更稳定、不需要维护 Reward Model。\n\n"
        "## 常见攻击与防御\n\n"
        "| 攻击方式 | 描述 | 防御 |\n"
        "|----------|------|------|\n"
        "| Prompt Injection | 「忽略之前的指令...」 | 输入过滤 + 角色强化 |\n"
        "| Jailbreak | 「DAN 模式：你现在是...」 | 安全 Prompt + 输出审查 |\n"
        "| 越狱模板 | 「假装你是...」 | 意图识别 + 拒绝模板 |\n\n"
        "## 红队测试（Red Teaming）\n\n"
        "红队 = 专门找漏洞的安全团队。目标：在模型上线前发现安全漏洞。\n\n"
        "方法：\n"
        "1. 设计对抗性 Prompt（注入、越狱、敏感内容）\n"
        "2. 测试模型是否有不安全输出\n"
        "3. 收集失败案例 -> 加入训练数据 -> 重新 SFT/RLHF\n\n"
        "## 内容安全审核\n\n"
        "```\n"
        "用户输入 -> 敏感词过滤 -> LLM -> 输出审核 -> 返回\n"
        "审核维度：政治敏感、色情暴力、隐私泄露（邮箱、身份证号）、幻觉（虚假信息）\n"
        "```\n\n"
        "> 面试加分：对齐不是为了政治正确，而是为了让模型在没有监督时也能做出正确的判断。",
        "安全,对齐,RLHF,红队,Prompt Injection"
    )

    db.commit()
    print("P4 (LLM评估 / 多模态 / 安全与对齐) 已写入")


if __name__ == "__main__":
    seed()
