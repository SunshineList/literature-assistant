# 环境变量配置指南

## Docker Compose 环境变量使用说明

### 基本概念

Docker Compose 支持从 `.env` 文件读取环境变量，有两种使用方式：

#### 1. 在 docker-compose.yml 中使用（变量替换）

```yaml
postgres:
  environment:
    POSTGRES_DB: ${POSTGRES_DB}        # 从 .env 读取并替换
    POSTGRES_USER: ${POSTGRES_USER}    # 从 .env 读取并替换
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # 从 .env 读取并替换
```

#### 2. 通过 env_file 注入到容器

```yaml
backend:
  env_file:
    - .env  # 将 .env 中的所有变量注入到容器内部
```

### 项目配置说明

#### .env 文件内容示例

```bash
# .env 文件
POSTGRES_DB=literature_assistant
POSTGRES_USER=literature_user
POSTGRES_PASSWORD=my_secure_password_123

DATABASE_URL=postgresql+asyncpg://literature_user:my_secure_password_123@postgres:5432/literature_assistant
SECRET_KEY=my_jwt_secret_key_xyz
```

#### docker-compose.yml 配置

```yaml
services:
  postgres:
    environment:
      # 方式1：使用 ${VAR} 语法，Docker Compose 会从 .env 读取并替换
      POSTGRES_DB: ${POSTGRES_DB}              # 替换为: literature_assistant
      POSTGRES_USER: ${POSTGRES_USER}          # 替换为: literature_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # 替换为: my_secure_password_123

  backend:
    # 方式2：使用 env_file，将整个 .env 文件的内容注入到容器
    env_file:
      - .env
    # 容器内部会有以下环境变量：
    # DATABASE_URL=postgresql+asyncpg://literature_user:my_secure_password_123@postgres:5432/literature_assistant
    # SECRET_KEY=my_jwt_secret_key_xyz
    # 等等...
```

### 重要注意事项

#### 1. 密码一致性

如果在 `.env` 中修改了 `POSTGRES_PASSWORD`，必须同步修改 `DATABASE_URL` 中的密码：

```bash
# ❌ 错误：密码不一致
POSTGRES_PASSWORD=new_password
DATABASE_URL=postgresql+asyncpg://literature_user:old_password@postgres:5432/literature_assistant

# ✅ 正确：密码一致
POSTGRES_PASSWORD=new_password
DATABASE_URL=postgresql+asyncpg://literature_user:new_password@postgres:5432/literature_assistant
```

#### 2. 特殊字符处理

如果密码包含特殊字符（如 `@`, `#`, `:` 等），在 URL 中需要进行 URL 编码：

```bash
# 原始密码：my@pass#word
# URL 编码后：my%40pass%23word

POSTGRES_PASSWORD=my@pass#word
DATABASE_URL=postgresql+asyncpg://literature_user:my%40pass%23word@postgres:5432/literature_assistant
```

常见字符的 URL 编码：
- `@` → `%40`
- `#` → `%23`
- `:` → `%3A`
- `/` → `%2F`
- `?` → `%3F`
- `&` → `%26`

#### 3. 引号使用

`.env` 文件中的值通常不需要引号：

```bash
# ✅ 推荐（不用引号）
POSTGRES_PASSWORD=my_password
SECRET_KEY=my_secret_key

# ⚠️ 可以（但引号会成为值的一部分）
POSTGRES_PASSWORD="my_password"   # 实际值是："my_password"（包含引号）

# ✅ 如果值中有空格，需要引号
APP_NAME="Literature Assistant"
```

### 配置步骤

#### 1. 复制模板

```bash
cp .env.example .env
```

#### 2. 编辑 .env 文件

```bash
vim .env
# 或
nano .env
# 或使用任何文本编辑器
```

#### 3. 修改配置

修改以下值：
```bash
# 修改数据库密码
POSTGRES_PASSWORD=your_strong_password_here

# 同步修改 DATABASE_URL 中的密码
DATABASE_URL=postgresql+asyncpg://literature_user:your_strong_password_here@postgres:5432/literature_assistant

# 修改 JWT 密钥（生成方法见下）
SECRET_KEY=your_generated_secret_key
```

#### 4. 生成安全的 JWT 密钥

```bash
# 使用 Python 生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用 openssl
openssl rand -base64 32

# 或使用 Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

#### 5. 验证配置

```bash
# 查看 Docker Compose 最终配置（会显示替换后的值）
docker-compose config

# 启动服务
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs -f
```

### 故障排查

#### 问题1：环境变量未生效

**症状**：容器中的环境变量是空的或使用了默认值

**解决**：
```bash
# 1. 确认 .env 文件在正确位置（与 docker-compose.yml 同目录）
ls -la .env

# 2. 确认 .env 文件格式正确（没有多余空格、使用正确的语法）
cat .env

# 3. 重新构建并启动
docker-compose down
docker-compose up -d --build
```

#### 问题2：数据库连接失败

**症状**：后端无法连接到 PostgreSQL

**检查**：
```bash
# 1. 确认密码一致
grep POSTGRES_PASSWORD .env
grep DATABASE_URL .env

# 2. 测试数据库连接
docker-compose exec postgres psql -U literature_user -d literature_assistant

# 3. 查看后端日志
docker-compose logs backend | grep -i "database\|error"
```

#### 问题3：特殊字符密码问题

**症状**：密码中有特殊字符，但无法连接

**解决**：
```bash
# 将密码改为不包含特殊字符的
# 或者对 DATABASE_URL 中的密码进行 URL 编码
```

### 安全建议

1. **永远不要提交 .env 文件到 Git**
   ```bash
   # 确认 .env 在 .gitignore 中
   cat .gitignore | grep ".env"
   ```

2. **使用强密码**
   - 至少 16 个字符
   - 包含大小写字母、数字、特殊字符
   - 不要使用常见单词

3. **定期更换密钥**
   - JWT 密钥应定期更换
   - 数据库密码应定期更换

4. **限制 .env 文件权限**
   ```bash
   chmod 600 .env  # 仅所有者可读写
   ```

5. **生产环境额外安全措施**
   - 使用密钥管理服务（如 AWS Secrets Manager、HashiCorp Vault）
   - 使用加密的环境变量
   - 启用数据库 SSL 连接

### 示例：完整配置流程

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/literature-assistant.git
cd literature-assistant

# 2. 创建 .env 文件
cp .env.example .env

# 3. 生成密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 输出：如 "abc123xyz789..."

# 4. 编辑 .env
vim .env
# 修改：
# POSTGRES_PASSWORD=MySecurePass2024!
# DATABASE_URL=postgresql+asyncpg://literature_user:MySecurePass2024!@postgres:5432/literature_assistant
# SECRET_KEY=abc123xyz789...

# 5. 保存并设置权限
chmod 600 .env

# 6. 启动服务
docker-compose up -d

# 7. 验证
docker-compose ps
docker-compose logs backend | head -20

# 8. 访问应用
# http://localhost
```

---

**如有问题，请查看 [DEPLOY.md](DEPLOY.md) 获取更多部署信息。**

