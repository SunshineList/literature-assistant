# 📚 Literature Assistant - 智能文献助手

> 基于 FastAPI + Vue 3 的现代化文献管理系统，集成 AI 技术提供智能阅读指南生成。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4+-blue.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能亮点

### 🎓 多专家模型系统
- **6种专业分析视角**：学术导师、通用总结、政府文件、商业分析、法律文档、技术文档
- **智能提示词管理**：每种专家使用独特的分析框架和输出格式
- **灵活切换**：导入时自由选择最适合的专家模型

### 🤖 强大的 AI 集成
- **多模型支持**：兼容所有 OpenAI API 格式的服务（GPT、Kimi、DeepSeek、Ollama等）
- **模型管理**：可配置多个 AI 模型，设置默认模型，随时切换
- **流式响应**：基于 SSE 技术，实时显示生成进度和内容
- **智能标签**：自动提取文献关键标签和摘要描述

### 📄 全格式支持
- **文件解析**：支持 PDF、Word (.docx)、Markdown、TXT 格式
- **批量导入**：一次上传多个文件，自动队列处理
- **内容提取**：智能提取文档内容，保持格式完整性

### 🎨 现代化 UI/UX
- **卡片式选择**：直观的专家和模型选择界面
- **实时反馈**：导入进度、生成状态实时更新
- **响应式设计**：适配各种屏幕尺寸
- **Markdown 渲染**：支持 Mermaid 图表、代码高亮、数学公式

### 🔍 强大的检索功能
- **多维度筛选**：关键词、标签、文件类型、时间范围
- **全文搜索**：快速定位所需文献
- **标签云**：可视化展示文献分类

### 👥 完整的用户系统
- **JWT 认证**：安全的用户身份验证
- **权限隔离**：每个用户独立的数据空间
- **配置管理**：个性化的 AI 模型配置

### 🏗️ 优秀的架构设计
- **设计模式**：策略模式、工厂模式、建造者模式
- **异步架构**：FastAPI + SQLAlchemy 2.0 async
- **数据库迁移**：类 Django 风格的迁移系统
- **代码质量**：清晰的分层架构，易于维护和扩展

## 🚀 快速开始

### 部署方式

#### 🐳 Docker 部署（推荐）

使用 Docker Compose 一键部署，包含 PostgreSQL + Nginx：

```bash
# 克隆项目
git clone https://github.com/yourusername/literature-assistant.git
cd literature-assistant

# 配置环境变量（重要！）
cp .env.example .env
vim .env  # 修改数据库密码和 JWT 密钥

# 启动服务
docker-compose up -d

# 访问 http://localhost
```

详细部署文档请查看：[DEPLOY.md](DEPLOY.md)

#### 💻 本地开发部署

### 环境要求

- Python 3.10+
- Node.js 18+
- SQLite 3 / PostgreSQL 12+

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/literature-assistant.git
cd literature-assistant
```

### 2. 启动后端

```bash
cd literature-assistant-backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
# 或
uvicorn app.main:app --reload --host 0.0.0.0 --port 8086
```

后端将运行在 `http://localhost:8086`

### 3. 启动前端

```bash
cd literature-assistant-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:5173`

### 4. 首次使用配置

1. 访问前端地址 `http://localhost:5173`
2. 注册一个用户账号
3. 进入"AI模型管理"页面
4. 添加你的 AI 模型配置（API Key、Base URL等）
5. 设置一个默认模型
6. 开始导入文献！

## 📖 使用指南

### 导入文献

1. 点击"单个导入"或"批量导入"按钮
2. 上传文件（支持 PDF、Word、Markdown、TXT）
3. **选择专家模型**：
   - 🎓 **学术导师**：适合学术论文、研究报告
   - 📝 **通用总结**：适合各类文章、资料
   - 🏛️ **政府文件专家**：适合政策文本、公文
   - 💼 **商业分析**：适合商业报告、市场分析
   - ⚖️ **法律文档**：适合合同、法律条文
   - 💻 **技术文档**：适合技术文档、代码文档
4. 可选：选择特定的 AI 模型（否则使用默认）
5. 点击"开始生成"，等待 AI 生成阅读指南

### 查看文献

- **列表视图**：浏览所有文献，支持筛选和搜索
- **详情视图**：查看完整的阅读指南，支持全屏阅读
- **下载文件**：随时下载原始文献文件

### AI 模型管理

- 添加多个 AI 模型配置
- 设置默认模型
- 启用/禁用特定模型
- 更新 API Key 和配置

## 🏗️ 技术栈

### 后端

- **FastAPI**: 现代、快速的 Python Web 框架
- **SQLAlchemy 2.0**: 异步 ORM
- **Pydantic**: 数据验证和序列化
- **SQLite**: 轻量级数据库
- **SSE**: Server-Sent Events 实时推送

### 前端

- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Pinia**: Vue 3 状态管理
- **Element Plus**: Vue 3 组件库
- **Vue Router**: 路由管理
- **Marked**: Markdown 渲染
- **Mermaid**: 图表渲染

## 📁 项目结构

```
literature-assistant/
├── docker-compose.yml              # Docker 编排配置
├── DEPLOY.md                       # Docker 部署文档
├── .dockerignore                   # Docker 忽略文件
├── literature-assistant-backend/   # 后端服务
│   ├── Dockerfile                  # 后端 Docker 镜像
│   ├── .env.example                # 环境变量示例
│   ├── app/
│   │   ├── main.py                 # FastAPI 应用入口
│   │   ├── config.py               # 配置管理
│   │   ├── models/                 # 数据模型
│   │   ├── api/                    # API 路由
│   │   ├── services/               # 业务逻辑
│   │   ├── core/                   # 核心模块
│   │   ├── utils/                  # 工具函数
│   │   ├── prompts/                # AI 提示词
│   │   │   └── experts/            # 专家提示词
│   │   └── db_migrations/          # 数据库迁移
│   ├── data/                       # 数据存储
│   └── uploads/                    # 上传文件
│
└── literature-assistant-frontend/  # 前端应用
    ├── Dockerfile                  # 前端 Docker 镜像
    ├── nginx.conf                  # Nginx 配置
    ├── src/
    │   ├── main.js                 # 应用入口
    │   ├── App.vue                 # 根组件
    │   ├── router/                 # 路由配置
    │   ├── stores/                 # Pinia 状态管理
    │   ├── views/                  # 页面组件
    │   ├── components/             # 可复用组件
    │   └── utils/                  # 工具函数
    └── public/                     # 静态资源
```

## 🎯 核心特性详解

### 专家模型系统

每种专家模型都经过精心设计，针对不同类型的文档提供专业的分析视角：

- **学术导师**：提供论文结构分析、研究方法论解读、关键术语解释、思维导图等
- **通用总结**：快速提炼核心要点，适合日常阅读材料
- **政府文件专家**：解读政策背景、核心精神、实施要点
- **商业分析**：分析商业逻辑、市场机会、竞争态势
- **法律文档**：解读法律条款、权利义务、风险提示
- **技术文档**：技术架构分析、实现细节、最佳实践

### 提示词管理

所有专家提示词都以文件形式管理，便于：
- 版本控制和协作
- 快速迭代优化
- 自定义和扩展
- 多语言支持

### 流式生成体验

采用 SSE 技术实现真正的流式响应：
- 逐字逐句显示生成内容
- 实时显示处理进度
- 可随时查看部分结果
- 提升用户体验

## 🤝 致谢

本项目灵感来源于 [liyupi/literature-assistant](https://github.com/liyupi/literature-assistant)，感谢原作者的开源贡献！

在原项目基础上，我们进行了以下增强：
- ✅ 新增6种专业分析专家模型
- ✅ 重构为用户系统，支持多用户使用
- ✅ 新增AI模型管理功能
- ✅ 优化UI/UX，采用卡片式交互
- ✅ 新增TXT格式支持
- ✅ 完善错误处理和用户反馈
- ✅ 改进代码架构和可维护性


## 📄 License

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🌟 Star History

如果这个项目对你有帮助，欢迎 Star ⭐️


