# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

个人工具集网站，用 Python + SQLite 构建，包含多个独立工具模块。

核心工具：**面试储备**——技术栈积累与面试练习系统。涵盖 8 个技术分组（Spring Cloud、Dubbo、LLM、中间件、Java、C++、Python、嵌入式），支持知识笔记、面试题条目、每日随机练习、AI 出题、收藏功能。

## Tech Stack

- **后端**: Python + Flask + Jinja2 模板（SSR）
- **数据库**: SQLite（`toolset.db`）
- **AI 集成**: DeepSeek API（OpenAI 兼容），通过 `.env` 配置 key
- **前端**: 服务器渲染 HTML + 少量 vanilla JS，无前端构建工具

## Project Layout

```
toolset/
├── app.py                  # Flask 入口，load_dotenv()、注册 Blueprint
├── db.py                   # SQLite 连接 + init_db()（含 schema 迁移）
├── llm_utils.py            # DeepSeek API 调用：出题 + token 统计
├── seed.py                 # 种子数据（Spring Cloud 技术栈）
├── seed_*.py               # 各模块种子脚本（一次性使用后可删除）
├── .env                    # DEEPSEEK_API_KEY=sk-xxx（不提交 git）
├── .env.example            # .env 模板
├── .gitignore              # .env, __pycache__, *.db
├── requirements.txt        # flask, markdown, python-dotenv
├── tools/
│   └── skillset/
│       ├── __init__.py
│       ├── models.py       # Tool/Stack/Entry/Favorite CRUD
│       ├── routes.py       # 全部路由（skillset/practice/favorites）
├── templates/
│   ├── base.html           # 导航栏（每日练习/收藏链接）
│   └── skillset/           # 页面模板
│       ├── index.html      # 工具列表
│       ├── tool_groups.html # 分组卡片（含练习按钮）
│       ├── group_detail.html # 分组详情（含学习路线）
│       ├── stack.html      # 技术栈详情（笔记+面试题）
│       ├── entry_form.html # 新建/编辑条目
│       ├── practice_select.html # 每日练习-选择页（AI开关+难度+localStorage）
│       ├── practice_quiz.html   # 每日练习-答题页（含 token 显示）
│       ├── practice_review.html # 每日练习-对照页（自评打分）
│       └── favorites.html  # 收藏列表（按栈筛选）
└── static/
    └── style.css           # 全部样式（含 @media print）
```

## Database Schema

```
tool (id, name, description, external_url, created_at)
  │ 1:N
stack (id, tool_id, name, description, sort_order, is_deprecated, group_name, created_at)
  │ 1:N
entry (id, stack_id, title, content, tags, entry_type['note'|'interview'], created_at, updated_at)
  │ 1:N
favorite (id, entry_id UNIQUE, created_at)
```

- `tool.external_url`: 非空时工具卡片直接链到外部 URL（如 B站音频下载）
- `stack.group_name`: 用于分组展示（Spring Cloud / Dubbo / LLM / Java / C++ / Python / 中间件 / 嵌入式）
- `entry.entry_type`: `note`=知识笔记, `interview`=面试题

## Key Routes

| 路径 | 说明 |
|------|------|
| `/` → `/skillset/` | 首页工具列表 |
| `/skillset/tool/<id>` | 工具详情（分组卡片） |
| `/skillset/tool/<id>/group/<name>` | 分组详情（技术栈列表+学习路线） |
| `/skillset/stack/<id>` | 技术栈详情（笔记+面试题+导出PDF按钮） |
| `/skillset/practice` | 每日练习选择页（AI出题/难度/记住选择） |
| `/skillset/practice/start` | 生成题目（POST，混合内部题库+AI） |
| `/skillset/practice/review` | 对照答案自评（POST） |
| `/skillset/favorites` | 收藏列表（可按技术栈筛选） |
| `/skillset/favorite/<id>/toggle` | 收藏/取消（AJAX JSON 响应） |

## Convention

- **添加新分组**: 在 `seed_xxx.py` 中创建 stacks + notes + interviews，更新 `group_detail.html` 的路线图和 `tool_groups.html` 的图标
- **添加内容**: 用 `add_note()`/`add_iv()` 模式直接写 DB，用 LIKE 匹配栈名避免编码问题
- **样式**: 全部在 `static/style.css`，模板内联 `<style>` 仅用于页面特定样式
- **AI 出题**: 依赖 `llm_utils.py`，key 优先级：OS 环境变量 > `.env` 文件 > 直接读 `.env` 内容
- **PDF 导出**: 纯 CSS `@media print` + `window.print()`，无服务端依赖

## Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 AI（可选，用于每日练习 AI 出题）
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 启动
python app.py           # http://127.0.0.1:5000
```
