# FastAPI 文献助手后端 - 快速启动指南

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

## 🚀 启动服务

### 方式一：使用启动脚本（推荐）

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

### 方式二：直接运行

```bash
# 方式1：使用 run.py
python run.py

# 方式2：使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8086
```

## 📋 环境配置

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `DATABASE_URL`: 数据库连接地址（默认使用 SQLite）
- `UPLOAD_DIR`: 文件上传目录
- `AI_BASE_URL`: Kimi AI API 地址
- `AI_MODEL`: AI 模型名称

## 🔍 访问服务

启动后可以访问：

- **API 服务**: http://localhost:8086/api
- **API 文档**: http://localhost:8086/docs
- **健康检查**: http://localhost:8086/api/health

## 📁 项目结构

```
literature-assistant-backend/
├── app/                        # 应用代码
│   ├── api/                   # API 路由
│   │   └── literature.py      # 文献管理接口
│   ├── core/                  # 核心模块
│   │   ├── database.py        # 数据库配置
│   │   ├── response.py        # 统一响应
│   │   └── exceptions.py      # 异常处理
│   ├── models/                # 数据模型
│   │   ├── literature.py      # 文献模型
│   │   └── schemas.py         # Pydantic 模型
│   ├── services/              # 业务服务
│   │   ├── literature_service.py  # 文献服务
│   │   ├── file_service.py        # 文件服务
│   │   └── ai_service.py          # AI 服务
│   ├── utils/                 # 工具函数
│   ├── config.py              # 配置管理
│   └── main.py                # 应用入口
├── data/                      # 数据存储（自动创建）
├── uploads/                   # 文件上传（自动创建）
├── requirements.txt           # Python 依赖
├── .env.example              # 环境变量示例
└── run.py                    # 启动脚本
```

## 🔌 API 接口

### 1. 分页查询文献列表
```
POST /api/literature/page
```

请求体：
```json
{
  "pageNum": 1,
  "pageSize": 10,
  "keyword": "关键词",
  "tags": ["标签1", "标签2"],
  "fileType": "pdf",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31"
}
```

### 2. 获取文献详情
```
GET /api/literature/{id}
```

### 3. 下载文献文件
```
GET /api/literature/{id}/download
```

### 4. 上传文献并生成阅读指南（SSE）
```
POST /api/literature/generate-guide
Content-Type: multipart/form-data

file: <文件>
apiKey: <Kimi API Key>
```

返回：Server-Sent Events (SSE) 流式响应

事件类型：
- `start`: 开始生成
- `progress`: 进度更新
- `content`: 内容片段
- `complete`: 完成
- `error`: 错误

## 🛠️ 开发调试

### 查看日志

应用日志会输出到控制台，包括：
- 数据库初始化信息
- 请求处理日志
- 错误堆栈信息

### 数据库管理

数据库文件位于 `data/literature_assistant.db`

可以使用 SQLite 客户端查看：
```bash
sqlite3 data/literature_assistant.db
```

常用命令：
```sql
-- 查看所有表
.tables

-- 查看文献表结构
.schema literature

-- 查询所有文献
SELECT * FROM literature;
```

## ⚠️ 常见问题

### 1. 端口被占用

修改 `.env` 文件中的 `PORT` 配置，或者在启动时指定：
```bash
PORT=8087 python run.py
```

### 2. 文件上传失败

检查：
- 文件大小是否超过限制（默认 50MB）
- 文件类型是否支持（pdf, doc, docx, md, markdown）
- `uploads` 目录是否有写权限

### 3. AI 服务调用失败

检查：
- API Key 是否正确
- 网络连接是否正常
- Kimi AI 服务是否可用

### 4. 数据库初始化失败

检查：
- `data` 目录是否有写权限
- 磁盘空间是否充足

## 📝 开发建议

1. **开发模式**: 设置 `DEBUG=True` 启用自动重载
2. **生产部署**: 使用 gunicorn 或其他 WSGI 服务器
3. **数据库**: 生产环境建议使用 PostgreSQL 或 MySQL
4. **文件存储**: 考虑使用 OSS 等对象存储服务

## 🔐 安全建议

1. 不要在代码中硬编码 API Key
2. 使用环境变量管理敏感配置
3. 生产环境设置合适的 CORS 策略
4. 定期备份数据库文件

## 📞 技术支持

如有问题，请查看：
- FastAPI 文档: https://fastapi.tiangolo.com/
- SQLAlchemy 文档: https://docs.sqlalchemy.org/
- Kimi AI 文档: https://platform.moonshot.cn/docs

