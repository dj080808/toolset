# -*- coding: utf-8 -*-
"""LLM 中文笔记与面试题 - 核心模块 (P0-P1)"""
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

    # ==================== Transformer 架构 ====================
    insert_note(db, "Transformer 架构",
        "Transformer 架构详解",
        "## 起源\n\n"
        "2017 年 Google 发表《Attention Is All You Need》，提出 Transformer 架构。"
        "这个架构完全摒弃了 RNN/LSTM，仅依赖 Attention 机制来处理序列数据。\n\n"
        "## 整体架构\n\n"
        "```\n"
        "Encoder: Input -> Embedding + 位置编码 -> [多头自注意力 + 前馈网络] x N 层 -> 输出\n"
        "Decoder: Output(右移) -> Embedding + 位置编码 -> [掩码MHA + 交叉注意力 + FFN] x N -> Linear + Softmax\n"
        "```\n\n"
        "## 三大核心组件\n\n"
        "| 组件 | 作用 | 面试重点 |\n"
        "|------|------|----------|\n"
        "| Self-Attention | 序列中每个 token 关注所有其他 token | QKV 计算、缩放点积 |\n"
        "| Multi-Head Attention | 多个注意力头并行，捕捉不同子空间信息 | 为什么多头比单头好？ |\n"
        "| Positional Encoding | 给模型注入位置信息（Transformer 本身感知不到顺序）| 正弦编码 vs 可学习编码 |\n\n"
        "## Self-Attention 计算公式\n\n"
        "```\n"
        "Q = X * W_Q    (Query: 我要找什么)\n"
        "K = X * W_K    (Key: 我能提供什么)\n"
        "V = X * W_V    (Value: 我的实际内容)\n\n"
        "Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V\n"
        "```\n\n"
        "为什么要除以 sqrt(d_k)？d_k 过大会导致点积值过大 -> softmax 梯度消失 -> 除以 sqrt(d_k) 做缩放。\n\n"
        "## Transformer 为什么比 RNN 好\n\n"
        "| 维度 | RNN/LSTM | Transformer |\n"
        "|------|----------|-------------|\n"
        "| 并行计算 | 否（必须等上一个时间步）| 是（全部 token 同时算）|\n"
        "| 长距离依赖 | 差（梯度消失）| 好（直接 Attention 到任意位置）|\n"
        "| 训练速度 | 慢 | 快（GPU 并行友好）|\n"
        "| 序列长度 | O(N) 串行 | O(N^2) Attention 矩阵（长序列耗显存）|\n\n"
        "> 面试金句：Transformer 的核心创新是用 Self-Attention 替代 RNN 的循环结构——"
        "序列中任意两个位置之间只需要 O(1) 步就能交互，不再需要 O(N) 的循环传播。",
        "Transformer,Self-Attention,架构,Attention"
    )

    insert_iv(db, "Transformer 架构",
        "Transformer 的 Self-Attention 和 RNN 有什么区别？为什么 Transformer 现在一统天下？",
        "## 核心区别\n\n"
        "| 维度 | RNN/LSTM | Transformer |\n"
        "|------|----------|-------------|\n"
        "| 计算方式 | 串行（等上一个时间步）| 并行（所有 token 同时算）|\n"
        "| 长距离依赖 | 梯度消失 | Self-Attention 直接到任意位置 |\n"
        "| 训练速度 | 慢 | 快（GPU 友好）|\n\n"
        "## 为什么一统天下\n\n"
        "1. **并行计算**：RNN 必须 t->t+1->t+2，Transformer 所有位置一起算\n"
        "2. **Scaling Law**：Transformer 扩大规模后能力线性增长，RNN 没有这个特性\n"
        "3. **多模态通用**：文本（GPT）、图像（ViT）、视频（Sora）都可以用 Transformer\n\n"
        "> 一句话：Transformer 用 Self-Attention 替代了 RNN 的循环——任意两位置 O(1) 交互，不再需要 O(N) 传播。",
        "Transformer,Self-Attention,RNN,高频"
    )

    # ==================== Attention 机制 ====================
    insert_note(db, "Attention 机制",
        "Attention 机制从入门到理解",
        "## 从 Seq2Seq 到 Attention\n\n"
        "### 传统 Seq2Seq 的瓶颈\n\n"
        "Encoder 把整个输入句子压缩成一个固定长度的向量 C。Decoder 每次从这个固定向量中解码。\n\n"
        "问题：「I love China」和「This is a very very long sentence...」"
        "都被压成同一个长度的向量 -> 信息丢失。\n\n"
        "### Attention 的解法\n\n"
        "Decoder 每生成一个词时，动态地关注 Encoder 输出的不同部分：\n"
        "- 生成第 1 个词 -> 主要看 Encoder 第 1 个词\n"
        "- 生成第 2 个词 -> 主要看 Encoder 第 2 个词\n\n"
        "## Self-Attention（自注意力）\n\n"
        "普通 Attention 是 Decoder -> Encoder（跨模块），Self-Attention 是序列内部自己关注自己。\n\n"
        "句子：「The cat sat on the mat」\n\n"
        "对「sat」做 Self-Attention：The(0.1), cat(0.4) <- 谁 sat？cat sat！高权重, "
        "sat(0.1), on(0.1), the(0.1), mat(0.2) <- sat 在哪？on the mat\n\n"
        "## Multi-Head Attention\n\n"
        "单头：一组 QKV 投影 -> 只能捕捉一种关系（如主语-谓语）\n"
        "多头：多组 QKV 投影 -> 同时捕捉多种关系\n"
        "  Head 1: 主语-谓语关系\n"
        "  Head 2: 形容词-名词关系\n"
        "  Head 3: 指代关系\n"
        "8 个头各有各的关注点 -> 拼接 -> Linear 融合\n\n"
        "## QKV 的直观理解\n\n"
        "| 概念 | 数据库类比 | 在 Attention 中 |\n"
        "|------|-----------|----------------|\n"
        "| Q（Query）| SQL 的 WHERE 条件 | 我想找什么信息 |\n"
        "| K（Key）| 索引列 | 每个 token 的索引标签 |\n"
        "| V（Value）| 实际数据 | 每个 token 的实际内容 |\n\n"
        "Attention = 根据 Query 和 Key 的相似度 -> 从 Value 中提取信息。",
        "Attention,Self-Attention,Multi-Head,QKV"
    )

    # ==================== 大模型训练流程 ====================
    insert_note(db, "大模型训练流程",
        "大模型三阶段训练范式",
        "## 训练全景图\n\n"
        "**第一阶段：Pre-training（预训练）**\n"
        "- 海量无标注数据，Next Token Prediction\n"
        "- 让模型学会语言本身（语法、知识、推理）\n"
        "- 成本最高（千卡 GPU 集群，数月）\n\n"
        "**第二阶段：SFT（Supervised Fine-Tuning，监督微调）**\n"
        "- 高质量人工标注的指令-回答对（1万~10万条）\n"
        "- 让模型学会遵循指令\n"
        "- 成本中等\n\n"
        "**第三阶段：RLHF / DPO（对齐阶段）**\n"
        "- RLHF：偏好排序 -> 训练 Reward Model -> PPO 强化学习\n"
        "- DPO：直接用偏好对优化，不需要单独的 Reward Model\n"
        "- 让模型做到有用、诚实、无害\n\n"
        "## RLHF 三步\n\n"
        "```\n"
        "Step 1: 收集偏好数据 - 同一个 prompt 生成多个 response，人工排序 (A > B > C)\n"
        "Step 2: 训练 Reward Model - 输入(prompt, response) -> 输出分数\n"
        "Step 3: PPO 优化 - 用 Reward Model 打分 -> 优化策略(LLM本身) + KL 散度惩罚\n"
        "```\n\n"
        "## DPO（Direct Preference Optimization）\n\n"
        "DPO 是 RLHF 的简化版，不需要单独的 Reward Model：\n"
        "- RLHF: 数据 -> Reward Model -> PPO -> 优化模型（三个组件）\n"
        "- DPO: 数据 -> 直接优化模型（一个组件）\n\n"
        "## 数据配比\n\n"
        "| 数据类型 | 比例 | 作用 |\n"
        "|----------|------|------|\n"
        "| 网页/文本 | ~80% | 基础知识 |\n"
        "| 代码 | ~10% | 逻辑推理能力 |\n"
        "| 书籍/论文 | ~5% | 深度知识 |\n"
        "| 多语言 | ~5% | 中文等能力 |\n\n"
        "> 面试金句：预训练决定了模型的上限，SFT 决定了模型的下限，RLHF 决定模型是不是人类喜欢的。",
        "预训练,SFT,RLHF,DPO,训练"
    )

    insert_iv(db, "大模型训练流程",
        "GPT 类模型的训练流程是怎样的？Pretrain、SFT、RLHF 分别做什么？",
        "## 三阶段\n\n"
        "**Pretrain（预训练）**：海量无标注文本 -> Next Token Prediction -> 学会语言本身。"
        "成本最高，决定模型上限。\n\n"
        "**SFT（监督微调）**：人工标注的指令-回答对（万级数据）-> 学会遵循指令。"
        "成本中等，决定模型下限。\n\n"
        "**RLHF（人类反馈强化学习）**：偏好数据排序 -> Reward Model -> PPO 优化 -> 对齐人类价值观。"
        "让模型有用、诚实、无害。DPO 是其简化版，不需要 Reward Model。\n\n"
        "> 一句话：预训练决定上限，SFT 决定下限，RLHF 决定是否合人心意。",
        "训练,Pretrain,SFT,RLHF,高频"
    )

    # ==================== LoRA 与高效微调 ====================
    insert_note(db, "LoRA 与高效微调",
        "LoRA 低秩微调原理",
        "## 问题\n\n"
        "全参数微调（Full Fine-Tuning）：70B 模型 -> 更新全部 700 亿参数 -> 需要多张 A100/H100。\n\n"
        "LoRA 的核心思想：**冻结原始权重，只训练一小部分新增参数。**\n\n"
        "## LoRA 原理\n\n"
        "```\n"
        "原始权重矩阵 W（冻结，不训练）\n\n"
        "旁路注入：delta_W = A * B\n"
        "  A: (d * r)   <- 降维矩阵\n"
        "  B: (r * d)   <- 升维矩阵\n"
        "  r << d       <- 秩远小于原始维度（r=8, 16, 64）\n\n"
        "输出 = W*x + delta_W*x = W*x + A*B*x\n"
        "       ^原始输出     ^LoRA 微调增量\n"
        "```\n\n"
        "## 参数量对比\n\n"
        "- GPT-3 175B 全参数微调：175B 参数\n"
        "- GPT-3 175B LoRA (r=16)：约几千万参数（不到全量的 0.1%）\n"
        "- 训练显存：全参数 >800GB（4*A100-80G），LoRA <48GB（单张消费级显卡）\n\n"
        "## LoRA 变体\n\n"
        "| 变体 | 改进 |\n"
        "|------|------|\n"
        "| QLoRA | 原始权重 4-bit 量化 + LoRA -> 单卡 48GB 微调 65B 模型 |\n"
        "| AdaLoRA | 自适应秩分配——重要的层用高秩，不重要的用低秩 |\n"
        "| DoRA | 把权重分解为幅度+方向，只微调方向 |\n\n"
        "> 面试加分：LoRA 的本质是用低秩矩阵近似参数更新——全参数微调的梯度变化矩阵 delta_W "
        "可以用 A*B 的低秩形式表达，因为微调对权重的修改本身是低秩的。",
        "LoRA,QLoRA,微调,参数高效"
    )

    db.commit()
    print("P0-P1 (Transformer / Attention / Training / LoRA) 内容已写入")


if __name__ == "__main__":
    seed()
