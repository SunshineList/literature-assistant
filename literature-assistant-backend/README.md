# Literature Assistant - FastAPI 后端

基于 FastAPI 的现代化文献管理后端服务，集成 AI 技术提供智能文献阅读指南生成、文献管理和检索功能。

## ✨ 功能特性

- 📚 **文献上传与解析**: 支持 PDF、Word、Markdown、TXT 格式
- 🎓 **多专家模型**: 6种专家模型（学术导师、通用总结、政府文件、商业、法律、技术）
- 🤖 **AI 阅读指南生成**: 支持任何 OpenAI 兼容 API
- 🏷️ **智能分类标签**: AI 自动提取分类标签和描述
- 🔍 **多维度检索**: 关键词、标签、文件类型、时间范围筛选
- ⚡ **实时流式响应**: 基于 SSE 技术实时推送生成进度
- 📦 **批量导入**: 支持多文件批量上传和处理
- 👥 **用户系统**: 完整的用户注册、登录、权限管理
- 🔧 **AI模型管理**: 支持多个AI模型配置和切换
- 🎨 **设计模式**: 使用策略、工厂、建造者等设计模式
- 🗄️ **数据库迁移**: 类似 Django 的迁移系统

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 AI 服务

AI 服务配置已迁移到数据库管理。首次使用时，请：

1. 启动后端服务
2. 注册用户账号
3. 在"AI模型管理"页面添加和配置您的 AI 模型
4. 设置一个默认模型

支持任何 OpenAI 兼容的 API，包括：
- OpenAI GPT 系列
- Kimi AI (月之暗面)
- Ollama (本地部署)
- DeepSeek
- 其他兼容 OpenAI API 格式的服务

### 3. 选择专家模型

系统提供6种专家模型，每种专家使用不同的分析视角：

- **🎓 学术导师**: 详细的学术文献阅读指南（默认）
- **📝 通用总结专家**: 适用于各类文章的快速总结
- **🏛️ 申论与政府文件分析专家**: 政府文件、政策文本分析
- **💼 商业分析专家**: 商业报告、市场分析
- **⚖️ 法律文件分析专家**: 法律文件、合同条款分析
- **💻 技术文档分析专家**: 技术文档、架构设计分析

在导入文献时，可以选择合适的专家模型生成阅读指南。

### 4. 运行服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8086

# 或使用启动脚本
python run.py

# Windows
start.bat

# Linux/Mac
./start.sh
```

### 5. 访问验证

- **API 服务**: http://localhost:8086/api
- **API 文档**: http://localhost:8086/docs
- **健康检查**: http://localhost:8086/api/health

## 📁 项目结构

```
literature-assistant-backend/
├── app/
│   ├── main.py                    # 应用入口
│   ├── config.py                  # 配置管理
│   ├── models/                    # 数据模型
│   │   ├── literature.py          # 文献 ORM 模型
│   │   └── schemas.py             # Pydantic 模型
│   ├── api/                       # API 路由
│   │   └── literature.py          # 文献接口
│   ├── services/                  # 业务逻辑层
│   │   ├── literature_service.py  # 文献服务
│   │   ├── file_service.py        # 文件处理
│   │   ├── ai_service.py          # AI 服务
│   │   ├── ai_providers/          # AI 提供商 (策略模式)
│   │   │   ├── base.py            # 抽象基类
│   │   │   ├── kimi_provider.py   # Kimi AI 实现
│   │   │   ├── ollama_provider.py # Ollama 实现
│   │   │   └── factory.py         # 工厂类
│   │   ├── file_parsers/          # 文件解析器 (策略模式)
│   │   │   ├── base.py
│   │   │   ├── pdf_parser.py
│   │   │   ├── word_parser.py
│   │   │   ├── markdown_parser.py
│   │   │   └── factory.py
│   │   └── query_builders/        # 查询构建器 (建造者模式)
│   │       └── literature_query_builder.py
│   ├── core/                      # 核心模块
│   │   ├── database.py            # 数据库配置
│   │   ├── response.py            # 统一响应格式
│   │   ├── response_builder.py    # 响应构建器 (建造者模式)
│   │   └── exceptions.py          # 异常处理
│   ├── utils/                     # 工具函数
│   │   ├── file_utils.py
│   │   ├── date_utils.py
│   │   └── prompt_loader.py       # 提示词加载器
│   ├── prompts/                   # AI 提示词
│   │   ├── literature-guide-system-prompt.txt
│   │   ├── literature-classification-system-prompt.txt
│   │   └── experts/               # 专家提示词
│   │       ├── general-summary.txt
│   │       ├── government-document-analyst.txt
│   │       ├── business-analyst.txt
│   │       ├── legal-analyst.txt
│   │       └── technology-analyst.txt
│   └── db_migrations/             # 数据库迁移
│       ├── base.py                # 迁移基类
│       ├── manager.py             # 迁移管理器
│       └── versions/              # 迁移版本
├── data/                          # 数据存储
├── uploads/                       # 文件上传
├── requirements.txt               # 依赖包
├── manage.py                      # 迁移命令行工具
├── run.py                         # 启动脚本
└── README.md
```

## 🛠 技术栈

- **框架**: FastAPI
- **数据库**: SQLite + SQLAlchemy (async)
- **文档处理**: PyPDF2、python-docx、markdown
- **AI 集成**: OpenAI SDK (Kimi AI)、Ollama SDK
- **异步支持**: aiofiles、aiosqlite
- **流式响应**: SSE (sse-starlette)
- **设计模式**: 策略、工厂、建造者、模板方法、命令模式

## 📖 API 接口

### 文献管理

- `POST /api/literature/page` - 分页查询文献列表
- `GET /api/literature/{id}` - 获取文献详情
- `GET /api/literature/{id}/download` - 下载文献文件
- `POST /api/literature/generate-guide` - 上传文献并生成阅读指南 (SSE)
- `POST /api/literature/batch-import` - 批量导入文献 (SSE)
- `GET /api/literature/health` - 健康检查

### 请求示例

#### 单文件导入

```bash
curl -X POST "http://localhost:8086/api/literature/generate-guide" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "aiProvider=kimi" \
  -F "apiKey=your-api-key"
```

#### 批量导入

```bash
curl -X POST "http://localhost:8086/api/literature/batch-import" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "aiProvider=ollama"
```

#### 分页查询

```bash
curl -X POST "http://localhost:8086/api/literature/page" \
  -H "Content-Type: application/json" \
  -d '{
    "pageNum": 1,
    "pageSize": 10,
    "keyword": "机器学习",
    "tags": ["AI", "深度学习"],
    "fileType": "pdf"
  }'
```

## 🗄️ 数据库迁移

本项目实现了类似 Django 的数据库迁移系统，支持版本管理和回滚。

### 基本命令

```bash
# 查看迁移状态
python manage.py showmigrations

# 创建新迁移
python manage.py makemigrations "添加新字段"

# 执行迁移
python manage.py migrate

# 回滚到上一个版本
python manage.py rollback
```

### 创建迁移示例

```python
# app/db_migrations/versions/20241111000000_add_author_field.py
from app.db_migrations.base import Migration

class AddAuthorFieldMigration(Migration):
    name = "20241111000000_add_author_field"
    description = "添加作者字段"
    
    async def upgrade(self, db):
        await db.execute("""
            ALTER TABLE literature ADD COLUMN author VARCHAR(200)
        """)
    
    async def downgrade(self, db):
        # SQLite 不支持 DROP COLUMN，需要重建表
        pass
```

## 🎨 设计模式应用

### 策略模式 (Strategy Pattern)

**AI 提供商**: 不同的 AI 服务商实现相同的接口

```python
# 使用示例
provider = AIProviderFactory.create(provider="kimi", api_key="xxx")
async for chunk in provider.generate_stream(content, prompt):
    print(chunk)
```

**文件解析器**: 不同文件格式使用不同的解析策略

```python
# 使用示例
parser = FileParserFactory.create(file_type="pdf")
content = await parser.parse(file_path)
```

### 工厂模式 (Factory Pattern)

**AIProviderFactory**: 根据配置创建对应的 AI 提供商实例

**FileParserFactory**: 根据文件类型创建对应的解析器实例

### 建造者模式 (Builder Pattern)

**LiteratureQueryBuilder**: 构建复杂的数据库查询

```python
query = (LiteratureQueryBuilder()
    .with_keyword("机器学习")
    .with_tags(["AI", "深度学习"])
    .with_file_type("pdf")
    .with_date_range("2024-01-01", "2024-12-31")
    .build())
```

**ResponseBuilder**: 构建统一的 API 响应

```python
return ResponseBuilder.ok(data=result, message="查询成功")
```

### 模板方法模式 (Template Method Pattern)

**Migration 基类**: 定义迁移的标准流程，子类实现具体的 upgrade/downgrade 方法

### 命令模式 (Command Pattern)

**manage.py**: 将迁移操作封装为命令，支持 makemigrations、migrate、rollback 等

## 🔧 开发指南

### 添加新的 AI 提供商

1. 在 `app/services/ai_providers/` 创建新的提供商类，继承 `AIProvider`
2. 实现 `generate_stream` 和 `generate` 方法
3. 在 `AIProviderFactory` 中注册新提供商
4. 更新 `app/config.py` 添加相关配置

### 添加新的文件类型支持

1. 在 `app/services/file_parsers/` 创建新的解析器类，继承 `FileParser`
2. 实现 `parse` 方法
3. 在 `FileParserFactory` 中注册新解析器
4. 更新配置中的 `ALLOWED_EXTENSIONS`

### 扩展查询条件

1. 在 `app/models/schemas.py` 的 `LiteratureQueryRequest` 添加新字段
2. 在 `LiteratureQueryBuilder` 中添加对应的构建方法
3. 确保数据库索引支持新的查询字段

## 📝 提示词管理

提示词文件位于 `app/prompts/` 目录：

- `literature-guide-system-prompt.txt`: 阅读指南生成提示词
- `literature-classification-system-prompt.txt`: 分类标签提取提示词

提示词会被自动加载和缓存，支持热更新（重启服务后生效）。

## 🐛 常见问题

### 1. greenlet 模块错误

```bash
pip install greenlet
```

### 2. AI 服务连接失败

请检查：
- AI 模型配置中的 Base URL 是否正确
- API Key 是否有效
- 网络连接是否正常
- 对于本地部署的服务（如 Ollama），确保服务已启动

### 3. 文件上传大小限制

在 `app/config.py` 中调整 `MAX_FILE_SIZE`：

```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### 4. 数据库锁定错误

SQLite 在高并发下可能出现锁定，考虑切换到 PostgreSQL 或 MySQL。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

如有问题或建议，请通过 Issue 联系我们。
