# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

个人工具集网站，用 Python + SQLite 构建，包含多个独立工具模块。

首个工具：**Skillset**——面向 Java Spring Boot 的技术栈积累系统。每个技术栈是一个分类（如 Spring MVC、MyBatis、JPA、Security 等），用户可以在每个技术栈下添加条目，记录知识点、代码片段、配置模板等，逐步积累技术资产。

## Tech Stack

- **后端**: Python + Flask + Jinja2 模板（SSR）
- **数据库**: SQLite（`toolset.db`）
- **前端**: 服务器渲染 HTML + CSS，无前端构建工具

## Architecture

### 数据模型（三层）

```
tool (工具) 1 ─── N stack (技术栈) 1 ─── N entry (条目)
```

- **tool**: 顶级分类（如"面试储备"），一个项目可以有多个工具
- **stack**: 技术栈（如"Spring Cloud Gateway"），属于某个 tool
- **entry**: 知识点条目，属于某个 stack，支持 Markdown 内容 + 标签

### 模块设计

项目按工具模块拆分，每个工具是一个 Flask Blueprint，注册在 `tools/` 下：

```
toolset/
├── app.py              # Flask 应用入口，注册 Blueprint
├── db.py               # SQLite 连接 + 建表（get_db, init_db）
├── seed.py             # 种子数据脚本，初始化工具和技术栈
├── tools/
│   └── skillset/
│       ├── __init__.py
│       ├── models.py   # Tool / Stack / Entry 静态 CRUD 方法
│       ├── routes.py   # Flask Blueprint，/skillset 前缀
│       templates/      # Jinja2 模板（每个工具一个子目录）
│       └── skillset/   # index.html, tool.html, stack.html, entry_form.html
└── static/
    └── style.css
```

### 路由结构

| 路径 | 页面 | 说明 |
|------|------|------|
| `/` | 重定向到 `/skillset/` | 主页（后续会有工具列表页） |
| `/skillset/` | 工具列表 | 列出所有工具（目前只有面试储备） |
| `/skillset/tool/<id>` | 技术栈列表 | 某个工具下的所有技术栈 |
| `/skillset/stack/<id>` | 条目列表 | 某个技术栈下的所有条目 |
| `/skillset/stack/<id>/entry/new` | 新建条目 | GET 表单 / POST 提交 |
| `/skillset/entry/<id>/edit` | 编辑条目 | GET 表单 / POST 提交 |
| `/skillset/entry/<id>/delete` | 删除条目 | POST 提交后重定向 |

## Commands

```bash
# 首次运行
pip install -r requirements.txt
python seed.py          # 初始化数据库 + 种子数据
python app.py           # 启动开发服务器 http://127.0.0.1:5000

# 后续运行（数据库已存在）
python app.py
```
