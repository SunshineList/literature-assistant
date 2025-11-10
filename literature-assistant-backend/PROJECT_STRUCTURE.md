# FastAPI 文献助手后端 - 项目结构说明

## 📁 完整目录结构

```
literature-assistant-backend/
├── app/                                    # 应用主目录
│   ├── __init__.py                        # 应用包初始化
│   ├── main.py                            # FastAPI 应用入口
│   ├── config.py                          # 配置管理（Settings）
│   │
│   ├── api/                               # API 路由层
│   │   ├── __init__.py
│   │   └── literature.py                  # 文献管理接口
│   │       ├── GET  /health               # 健康检查
│   │       ├── POST /page                 # 分页查询文献
│   │       ├── GET  /{id}                 # 获取文献详情
│   │       ├── GET  /{id}/download        # 下载文献
│   │       └── POST /generate-guide       # 生成阅读指南(SSE)
│   │
│   ├── core/                              # 核心模块
│   │   ├── __init__.py
│   │   ├── database.py                    # 数据库配置和会话管理
│   │   ├── response.py                    # 统一响应格式 (Response, PageData)
│   │   └── exceptions.py                  # 自定义异常类
│   │
│   ├── models/                            # 数据模型层
│   │   ├── __init__.py
│   │   ├── literature.py                  # SQLAlchemy ORM 模型
│   │   └── schemas.py                     # Pydantic 请求/响应模型
│   │       ├── LiteratureQueryRequest     # 查询请求
│   │       ├── LiteratureResponse         # 文献响应
│   │       ├── LiteratureDetailResponse   # 文献详情响应
│   │       └── HealthResponse             # 健康检查响应
│   │
│   ├── services/                          # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── literature_service.py          # 文献业务服务
│   │   │   ├── create_literature()        # 创建文献
│   │   │   ├── update_literature()        # 更新文献
│   │   │   ├── get_literature_by_id()     # 获取文献
│   │   │   └── page_query()               # 分页查询
│   │   │
│   │   ├── file_service.py                # 文件处理服务
│   │   │   ├── save_file()                # 保存文件
│   │   │   ├── extract_content()          # 提取文件内容
│   │   │   ├── _extract_pdf()             # 解析 PDF
│   │   │   ├── _extract_word()            # 解析 Word
│   │   │   └── _extract_markdown()        # 解析 Markdown
│   │   │
│   │   └── ai_service.py                  # AI 服务（Kimi AI）
│   │       ├── generate_reading_guide_stream()    # 流式生成阅读指南
│   │       └── extract_tags_and_description()     # 提取标签和描述
│   │
│   └── utils/                             # 工具函数
│       ├── __init__.py
│       ├── file_utils.py                  # 文件处理工具
│       │   ├── generate_file_path()       # 生成文件路径
│       │   ├── get_file_extension()       # 获取扩展名
│       │   ├── format_file_size()         # 格式化文件大小
│       │   └── is_allowed_file()          # 验证文件类型
│       │
│       └── date_utils.py                  # 日期处理工具
│           ├── parse_date()               # 解析日期
│           └── format_datetime()          # 格式化日期
│
├── data/                                   # 数据存储目录（自动创建）
│   └── literature_assistant.db            # SQLite 数据库文件
│
├── uploads/                                # 文件上传目录（自动创建）
│   └── documents/                         # 文档存储
│       └── YYYYMMDD/                      # 按日期分目录
│           └── timestamp_hash.ext         # 文件命名格式
│
├── requirements.txt                        # Python 依赖列表
├── .env.example                           # 环境变量示例
├── .gitignore                             # Git 忽略文件
├── README.md                              # 项目说明
├── QUICKSTART.md                          # 快速启动指南
├── PROJECT_STRUCTURE.md                   # 项目结构说明（本文件）
├── run.py                                 # 启动脚本
├── start.sh                               # Linux/macOS 启动脚本
└── start.bat                              # Windows 启动脚本
```

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────────┐
│           API Layer (api/)              │  ← FastAPI 路由和控制器
│          literature.py                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Service Layer (services/)         │  ← 业务逻辑层
│  literature_service.py                  │
│  file_service.py                        │
│  ai_service.py                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Model Layer (models/)             │  ← 数据模型层
│  literature.py (ORM)                    │
│  schemas.py (Pydantic)                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Database Layer (core/)            │  ← 数据访问层
│  database.py (SQLAlchemy)               │
└─────────────────────────────────────────┘
```

### 模块职责

#### 1. API Layer (`app/api/`)
- **职责**: 处理 HTTP 请求和响应
- **功能**: 
  - 路由定义
  - 请求参数验证
  - 调用 Service 层
  - 返回统一格式响应

#### 2. Service Layer (`app/services/`)
- **职责**: 实现核心业务逻辑
- **功能**:
  - 文献管理业务逻辑
  - 文件上传和解析
  - AI 服务调用
  - 事务管理

#### 3. Model Layer (`app/models/`)
- **职责**: 定义数据结构
- **功能**:
  - ORM 模型（数据库表结构）
  - Pydantic 模型（请求/响应验证）

#### 4. Core Layer (`app/core/`)
- **职责**: 提供核心基础设施
- **功能**:
  - 数据库连接管理
  - 统一响应格式
  - 异常处理机制

#### 5. Utils Layer (`app/utils/`)
- **职责**: 提供通用工具函数
- **功能**:
  - 文件处理工具
  - 日期处理工具
  - 其他辅助函数

## 🔄 数据流转

### 文献上传流程

```
1. 客户端上传文件
        ↓
2. API Layer 接收请求 (literature.py)
        ↓
3. File Service 保存文件 (file_service.py)
        ↓
4. File Service 提取内容 (file_service.py)
        ↓
5. Literature Service 创建记录 (literature_service.py)
        ↓
6. AI Service 提取标签和描述 (ai_service.py)
        ↓
7. AI Service 流式生成阅读指南 (ai_service.py)
        ↓
8. Literature Service 更新记录 (literature_service.py)
        ↓
9. 返回 SSE 流式响应给客户端
```

### 文献查询流程

```
1. 客户端发送查询请求
        ↓
2. API Layer 接收请求 (literature.py)
        ↓
3. Literature Service 构建查询条件 (literature_service.py)
        ↓
4. Database Layer 执行查询 (database.py)
        ↓
5. 转换为响应模型 (schemas.py)
        ↓
6. 返回统一格式响应 (response.py)
```

## 📊 数据库设计

### Literature 表结构

```sql
CREATE TABLE literature (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    original_name   VARCHAR(255) NOT NULL,
    file_path       VARCHAR(500) NOT NULL,
    file_size       BIGINT NOT NULL,
    file_type       VARCHAR(10) NOT NULL,
    content_length  INT DEFAULT 0,
    tags            VARCHAR(2000),           -- JSON 数组
    description     VARCHAR(2000),
    reading_guide   TEXT,
    status          TINYINT DEFAULT 1,       -- 0:处理中, 1:已完成, 2:失败
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted         TINYINT DEFAULT 0
);
```

## 🔌 API 接口详情

### 1. 健康检查
```
GET /api/literature/health

Response:
{
  "success": true,
  "message": "服务正常运行",
  "data": {
    "status": "ok",
    "message": "服务正常运行"
  },
  "code": 200
}
```

### 2. 分页查询文献
```
POST /api/literature/page

Request:
{
  "pageNum": 1,
  "pageSize": 10,
  "keyword": "关键词",
  "tags": ["标签1"],
  "fileType": "pdf",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31"
}

Response:
{
  "success": true,
  "message": "查询成功",
  "data": {
    "records": [...],
    "total": 100,
    "pageNum": 1,
    "pageSize": 10
  },
  "code": 200
}
```

### 3. 获取文献详情
```
GET /api/literature/{id}

Response:
{
  "success": true,
  "message": "查询成功",
  "data": {
    "id": 1,
    "originalName": "文献.pdf",
    "fileType": "pdf",
    "fileSize": 1024000,
    "tags": ["AI", "机器学习"],
    "description": "文献描述",
    "readingGuideSummary": "# 阅读指南...",
    "status": 1,
    "createTime": "2024-11-10T10:00:00",
    "updateTime": "2024-11-10T10:00:00"
  },
  "code": 200
}
```

### 4. 下载文献
```
GET /api/literature/{id}/download

Response: 文件流 (application/octet-stream)
```

### 5. 生成阅读指南（SSE）
```
POST /api/literature/generate-guide
Content-Type: multipart/form-data

Form Data:
- file: <文件>
- apiKey: <Kimi API Key>

Response: Server-Sent Events

event: progress
data: 正在保存文件...

event: progress
data: 正在解析文件内容...

event: start
data: 开始生成阅读指南...

event: content
data: # 文献阅读指南

event: content
data: ## 概述

event: complete
data: 阅读指南生成完成！
```

## 🔧 配置说明

### 环境变量 (.env)

```env
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/literature_assistant.db

# 文件上传配置
UPLOAD_DIR=./uploads/documents
MAX_FILE_SIZE=52428800
ALLOWED_EXTENSIONS=pdf,doc,docx,md,markdown

# AI 服务配置
AI_BASE_URL=https://api.moonshot.cn/v1
AI_MODEL=kimi-k2-turbo-preview
AI_MAX_TOKENS=20480
AI_TEMPERATURE=0.7
AI_TIMEOUT=60000

# 服务配置
HOST=0.0.0.0
PORT=8086
DEBUG=True
```

## 🎯 设计模式

### 1. 依赖注入
使用 FastAPI 的依赖注入系统管理数据库会话：
```python
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

### 2. 服务单例
所有服务类创建全局实例供复用：
```python
literature_service = LiteratureService()
file_service = FileService()
ai_service = AIService()
```

### 3. 统一响应格式
使用泛型类封装所有 API 响应：
```python
class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T]
    code: int
```

### 4. 异常处理链
自定义异常层次结构：
```
LiteratureException (基础异常)
    ├── FileException (文件异常)
    ├── AIException (AI服务异常)
    ├── DatabaseException (数据库异常)
    └── NotFoundException (未找到异常)
```

## 📚 技术栈

| 组件 | 技术 | 版本要求 |
|------|------|---------|
| Web 框架 | FastAPI | Latest |
| ASGI 服务器 | Uvicorn | Latest |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | SQLite (aiosqlite) | - |
| 数据验证 | Pydantic | 2.0+ |
| 异步 IO | aiofiles | Latest |
| HTTP 客户端 | httpx | Latest |
| PDF 解析 | PyPDF2 | Latest |
| Word 解析 | python-docx | Latest |
| SSE | sse-starlette | Latest |

## 🚀 部署建议

### 开发环境
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8086
```

### 生产环境
```bash
# 使用 gunicorn + uvicorn workers
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8086 \
    --access-logfile - \
    --error-logfile -
```

### Docker 部署
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]
```

## 📖 扩展指南

### 添加新的 API 接口

1. 在 `app/api/literature.py` 添加路由函数
2. 在 `app/services/` 添加业务逻辑
3. 在 `app/models/schemas.py` 添加请求/响应模型
4. 更新文档

### 添加新的文件类型支持

1. 在 `file_service.py` 添加解析方法
2. 更新 `ALLOWED_EXTENSIONS` 配置
3. 在 `extract_content()` 添加类型判断

### 集成其他 AI 服务

1. 创建新的服务类（如 `openai_service.py`）
2. 实现相同的接口方法
3. 在配置中添加切换选项

## ⚡ 性能优化

1. **数据库优化**
   - 添加索引（create_time, file_type, tags）
   - 使用数据库连接池
   - 查询结果缓存

2. **文件处理优化**
   - 使用流式读取大文件
   - 异步处理文件上传
   - 压缩存储

3. **AI 调用优化**
   - 限制内容长度
   - 缓存频繁请求
   - 设置合理超时

## 🔒 安全建议

1. **输入验证**: 使用 Pydantic 严格验证所有输入
2. **文件安全**: 验证文件类型和大小
3. **SQL 注入**: 使用 ORM 参数化查询
4. **密钥管理**: 使用环境变量，不在代码中硬编码
5. **CORS 配置**: 生产环境限制允许的域名
6. **日志脱敏**: 不记录敏感信息（API Key 等）

---

**最后更新**: 2024-11-10
**维护者**: Literature Assistant Team

