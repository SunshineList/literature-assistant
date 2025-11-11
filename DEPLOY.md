# 🐳 Docker 部署指南

使用 Docker Compose 一键部署 Literature Assistant，包含 PostgreSQL 数据库和 Nginx 反向代理。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+

## 🚀 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/literature-assistant.git
cd literature-assistant
```

### 2. 配置环境变量（重要！）

**⚠️ 必须完成此步骤才能安全运行！**

#### 创建项目根目录的 .env 文件

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
vim .env  # 或使用其他编辑器
```

#### 可选：创建后端独立的 .env 文件（本地开发）

如果你要本地开发运行后端，也可以为后端创建独立的配置：

```bash
# 进入后端目录
cd literature-assistant-backend

# 创建后端 .env 文件（如果没有 .env.example，手动创建）
cat > .env << 'EOF'
# 应用配置
APP_NAME=Literature Assistant
VERSION=1.0.0
DEBUG=true

# 数据库配置（开发环境使用 SQLite）
DATABASE_URL=sqlite+aiosqlite:///./data/literature_assistant.db

# JWT 配置（开发环境可以使用简单密钥）
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 文件上传配置
UPLOAD_DIR=./uploads/documents
MAX_FILE_SIZE=52428800
EOF

# 返回项目根目录
cd ..
```

**必须修改以下配置**：

1. **数据库密码**：
   ```bash
   POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
   DATABASE_URL=postgresql+asyncpg://literature_user:YOUR_STRONG_PASSWORD_HERE@postgres:5432/literature_assistant
   ```

2. **JWT 密钥**（用于用户认证）：
   ```bash
   # 生成随机密钥
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # 将生成的密钥填入 .env
   SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
   ```

3. **生产环境配置**：
   ```bash
   DEBUG=false
   ```

> 💡 提示：.env 文件已添加到 .gitignore，不会被提交到版本控制

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 4. 访问应用

- **前端界面**: http://localhost
- **后端 API**: http://localhost:8086/api
- **API 文档**: http://localhost:8086/docs

### 5. 首次配置

1. 访问 http://localhost
2. 注册用户账号
3. 进入"AI模型管理"配置 AI 服务
4. 设置默认模型
5. 开始使用！

## 📦 服务说明

### 服务组成

- **postgres**: PostgreSQL 15 数据库
- **backend**: FastAPI 后端服务
- **frontend**: Vue 3 前端 + Nginx

### 端口映射

| 服务 | 容器端口 | 主机端口 |
|------|---------|---------|
| frontend (nginx) | 80 | 80 |
| backend | 8086 | 8086 |
| postgres | 5432 | 5432 |

### 数据持久化

数据通过 Docker Volume 持久化存储：

- `postgres_data`: PostgreSQL 数据库文件
- `./literature-assistant-backend/uploads`: 上传的文献文件
- `./literature-assistant-backend/data`: 应用数据（日志等）

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器、网络、卷
docker-compose down -v
```

### 查看状态

```bash
# 查看运行状态
docker-compose ps

# 查看资源使用
docker stats
```

### 日志查看

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# 最后100行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U literature_user -d literature_assistant

# 进入前端容器
docker-compose exec frontend sh
```

## 🔍 故障排查

### 1. 检查容器状态

```bash
docker-compose ps
```

所有服务应显示为 `Up` 状态。

### 2. 检查健康状态

```bash
# 检查后端健康
curl http://localhost:8086/api/health

# 检查前端
curl http://localhost/

# 检查数据库连接
docker-compose exec postgres pg_isready -U literature_user
```

### 3. 查看日志

```bash
# 后端启动日志
docker-compose logs backend | grep "Application startup complete"

# 数据库连接日志
docker-compose logs backend | grep "Database"

# Nginx日志
docker-compose logs frontend
```

### 4. 常见问题

#### 后端无法连接数据库

检查 PostgreSQL 是否就绪：
```bash
docker-compose logs postgres
docker-compose exec postgres pg_isready
```

重启后端服务：
```bash
docker-compose restart backend
```

#### 前端无法访问后端 API

检查 nginx 配置和后端服务：
```bash
# 测试后端
curl http://localhost:8086/api/health

# 测试 nginx 代理
curl http://localhost/api/health
```

#### 上传文件失败

检查文件权限和目录：
```bash
docker-compose exec backend ls -la /app/uploads
docker-compose exec backend chmod -R 777 /app/uploads
```

## 🔒 生产环境配置

### 1. 使用 HTTPS

推荐使用 Let's Encrypt + Certbot，或在前面加一层 Nginx 反向代理。

修改 `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "443:443"
  volumes:
    - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf
    - ./ssl:/etc/nginx/ssl
```

### 2. 环境变量安全

**已默认配置** ✅

项目已配置使用 `.env` 文件管理敏感信息：

- ✅ `docker-compose.yml` 使用环境变量引用
- ✅ `.env.example` 提供配置模板
- ✅ `.env` 已添加到 `.gitignore`
- ✅ 所有敏感配置通过环境变量注入

**安全检查清单**：

```bash
# 1. 确认 .env 文件存在且已配置
ls -la .env

# 2. 确认 .env 文件权限（仅所有者可读写）
chmod 600 .env

# 3. 确认敏感信息不在 git 中
git check-ignore .env  # 应该显示 .env

# 4. 验证配置是否生效
docker-compose config  # 查看最终配置（密码会显示为环境变量值）
```

### 3. 资源限制

添加资源限制防止服务占用过多资源：

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

### 4. 备份策略

#### 数据库备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U literature_user literature_assistant | gzip > $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_backup_$TIMESTAMP.tar.gz literature-assistant-backend/uploads/

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x backup.sh
```

设置定时备份（crontab）：

```bash
# 每天凌晨2点备份
0 2 * * * /path/to/literature-assistant/backup.sh
```

#### 恢复备份

```bash
# 恢复数据库
gunzip < backups/db_backup_TIMESTAMP.sql.gz | docker-compose exec -T postgres psql -U literature_user literature_assistant

# 恢复上传文件
tar -xzf backups/uploads_backup_TIMESTAMP.tar.gz
```

## 📊 监控

### 基础监控

```bash
# 查看资源使用
docker stats

# 查看日志量
docker-compose logs --tail=1000 backend | wc -l
```

### 集成监控（可选）

可以集成 Prometheus + Grafana 进行更专业的监控。

## 🔄 更新部署

### 1. 拉取最新代码

```bash
git pull origin main
```

### 2. 重新构建并启动

```bash
# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs -f
```

### 3. 数据库迁移（如有需要）

```bash
docker-compose exec backend python manage.py migrate
```

## 🛑 完全卸载

```bash
# 停止并删除所有容器、网络
docker-compose down

# 删除数据卷（注意：会删除所有数据）
docker-compose down -v

# 删除镜像
docker rmi literature-assistant-backend
docker rmi literature-assistant-frontend
docker rmi postgres:15-alpine
docker rmi nginx:alpine

# 删除项目目录
cd ..
rm -rf literature-assistant
```

## 📝 注意事项

1. **首次启动**: PostgreSQL 初始化需要一些时间，后端可能会等待数据库就绪
2. **数据持久化**: 使用 `docker-compose down -v` 会删除所有数据，请谨慎使用
3. **端口冲突**: 确保 80、8086、5432 端口未被占用
4. **资源需求**: 建议至少 2GB RAM 和 10GB 磁盘空间
5. **安全配置**: 生产环境务必修改默认密码和密钥

## 🆘 获取帮助

- 查看日志: `docker-compose logs -f`
- 检查配置: `docker-compose config`
- GitHub Issues: [提交问题](https://github.com/yourusername/literature-assistant/issues)

---

**Happy Deploying! 🚀**

