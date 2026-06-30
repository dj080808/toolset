# 个人工具集

一个用 Python + Flask + SQLite 构建的个人工具集网站，核心功能是**面试储备**——技术栈积累与面试练习系统。

## 功能

### 面试储备

涵盖 **8 个技术分组**，共 140+ 个技术栈，300+ 篇笔记，300+ 道面试题：

| 分组 | 内容 |
|------|------|
| ☁️ Spring Cloud | 微服务全家桶：Nacos、Gateway、Sentinel、Seata、Feign... |
| ⚡ Dubbo | RPC 框架：Triple 协议、SPI 机制、集群容错、服务路由... |
| 🤖 LLM | 大模型：Transformer、RAG、Agent、Prompt Engineering、LoRA... |
| 📦 中间件 | Kafka、Redis、RabbitMQ、MySQL、ES、Docker、Nginx... |
| ☕ Java | JVM、并发、集合源码、Spring Framework、Java 8-21... |
| 🔧 C++ | 智能指针、STL、Move 语义、多线程、C++20 Coroutines... |
| 🐍 Python | 装饰器、asyncio、FastAPI、Pandas、pytest... |
| 💻 嵌入式 | ARM Cortex-M、FreeRTOS、嵌入式 Linux、I2C/SPI/UART... |

### 每日练习

- 选择技术栈 → 随机出 10 道面试题 → 答题 → 自评打分
- 🤖 AI 出题：集成 DeepSeek，混合内部题库和实时生成的题目
- 难度选择：简单 / 中等 / 冷酷
- 收藏功能：好题一键收藏，按技术栈筛选复习

### 其他工具

- 📻 B站音频下载：跳转 GitHub

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python seed.py

# 3. 启动
python app.py
```

打开 http://127.0.0.1:5000

## AI 出题（可选）

```bash
cp .env.example .env
# 编辑 .env，填入 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-xxxxxxxx
```

注册地址：[platform.deepseek.com](https://platform.deepseek.com)，新用户有免费额度。

## 技术栈

- 后端：Python + Flask + Jinja2（SSR）
- 数据库：SQLite
- AI：DeepSeek API（OpenAI 兼容）
- 前端：服务器渲染 HTML + 少量 vanilla JS

## 项目结构

```
toolset/
├── app.py              # Flask 入口
├── db.py               # 数据库连接与建表
├── llm_utils.py        # DeepSeek API 调用
├── seed.py             # 种子数据
├── .env                # API Key（不提交）
├── .env.example        # .env 模板
├── tools/
│   └── skillset/       # 核心模块
│       ├── models.py   # 数据模型
│       └── routes.py   # 路由
├── templates/          # Jinja2 模板
│   └── skillset/
└── static/
    └── style.css
```
