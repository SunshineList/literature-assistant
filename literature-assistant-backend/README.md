# Literature Assistant - FastAPI 后端

基于 FastAPI 的现代化文献管理后端服务，集成 AI 技术为用户提供智能文献阅读指南生成、文献管理和检索功能。

## ✨ 功能特性

- 📚 **文献上传与解析**: 支持 PDF、Word (.doc/.docx)、Markdown 格式文献的上传和内容解析
- 🤖 **AI 阅读指南生成**: 支持 Kimi AI 和 Ollama，基于文献内容自动生成结构化阅读指南
- 🏷️ **智能分类标签**: AI 自动从阅读指南中提取分类标签和描述，便于管理和检索
- 🔍 **多维度检索**: 支持关键词、标签、文件类型、时间范围等多种筛选条件
- ⚡ **实时流式响应**: 基于 SSE 技术，实时推送 AI 生成进度和结果
- 🔧 **完善的异常处理**: 统一异常处理机制，提供友好的错误信息
- 📖 **API 文档**: 集成 FastAPI 自动文档，提供完善的 API 接口文档
- 🎯 **提示词管理**: 文件化提示词系统，支持缓存和动态加载
- 🔌 **多 AI 提供商**: 支持 Kimi AI（云端）和 Ollama（本地），可灵活切换

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### 3. 运行服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8086

# 或者使用提供的启动脚本
python run.py
```

### 4. 访问验证

- **API 服务**: http://localhost:8086/api
- **API 文档**: http://localhost:8086/docs
- **健康检查**: http://localhost:8086/api/health

## 📁 项目结构

```
literature-assistant-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── config.py               # 配置管理
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── literature.py       # 文献模型
│   │   └── schemas.py          # Pydantic 模型
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   └── literature.py       # 文献相关接口
│   ├── services/               # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── literature_service.py    # 文献服务
│   │   ├── file_service.py          # 文件处理服务
│   │   └── ai_service.py            # AI 服务
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库配置
│   │   ├── response.py         # 统一响应格式
│   │   └── exceptions.py       # 异常处理
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── file_utils.py       # 文件工具
│       └── date_utils.py       # 日期工具
├── data/                       # 数据存储目录
├── uploads/                    # 文件上传目录
├── requirements.txt            # 依赖包
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
├── run.py                     # 启动脚本
└── README.md                  # 项目说明
```

## 🛠 技术栈

- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy (async)
- **文档处理**: PyPDF2 (PDF)、python-docx (Word)、markdown (Markdown)
- **AI 集成**: 
  - Kimi AI (OpenAI SDK)
  - Ollama (Ollama Python SDK)
- **异步支持**: aiofiles, aiosqlite
- **流式响应**: SSE (sse-starlette)

## 📖 API 接口

### 文献管理

- `POST /api/literature/page` - 分页查询文献列表
- `GET /api/literature/{id}` - 获取文献详情
- `GET /api/literature/{id}/download` - 下载文献文件
- `POST /api/literature/generate-guide` - 上传文献并生成阅读指南(SSE)
- `GET /api/literature/health` - 健康检查

### 详细文档

- 📘 [快速启动指南](./QUICKSTART.md)
- 📙 [项目结构说明](./PROJECT_STRUCTURE.md)
- 📗 [提示词使用指南](./PROMPT_USAGE.md)
- 📕 [AI 提供商配置](./AI_PROVIDERS.md)

## 🔧 开发指南

### 添加新的文件类型支持

1. 在 `file_service.py` 中添加新的解析方法
2. 更新 `ALLOWED_EXTENSIONS` 配置
3. 在 `extract_content` 方法中添加类型判断

### 扩展查询条件

1. 在 `schemas.py` 中的 `LiteratureQueryRequest` 添加新的查询字段
2. 更新 `literature_service.py` 中的查询逻辑
3. 确保数据库索引支持新的查询字段

## 📄 许可证

MIT License

