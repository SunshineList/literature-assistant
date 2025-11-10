# AI 提供商配置指南

## 📝 概述

本项目支持多个 AI 提供商，通过环境变量轻松切换。目前支持：

- **Kimi AI** (月之暗面)
- **Ollama** (本地部署)

## 🔧 配置方式

### 环境变量配置

在 `.env` 文件中设置：

```env
# 选择 AI 提供商: kimi 或 ollama
AI_PROVIDER=kimi

# Kimi AI 配置
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest

# 通用配置
AI_MAX_TOKENS=20480
AI_TEMPERATURE=0.7
AI_TIMEOUT=300
```

## 🌙 Kimi AI 配置

### 1. 获取 API Key

1. 访问 [Kimi 开放平台](https://platform.moonshot.cn/)
2. 注册并登录账号
3. 在控制台创建 API Key
4. 将 API Key 保存到前端（前端会自动保存到 localStorage）

### 2. 配置参数

```env
AI_PROVIDER=kimi
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k  # 或其他可用模型
```

### 3. 可用模型

- `moonshot-v1-8k`: 8K 上下文窗口
- `moonshot-v1-32k`: 32K 上下文窗口
- `moonshot-v1-128k`: 128K 上下文窗口

### 4. 优点

- ✅ 云端服务，无需本地部署
- ✅ 响应速度快
- ✅ 中文能力强
- ✅ 支持大上下文窗口
- ✅ API 兼容 OpenAI 格式

### 5. 注意事项

- 需要网络连接
- 需要有效的 API Key
- 按使用量计费
- 用户需要在前端输入自己的 API Key

## 🦙 Ollama 配置

### 1. 安装 Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
下载并安装：https://ollama.com/download

### 2. 下载模型

```bash
# 下载推荐的 Qwen2.5 模型
ollama pull qwen2.5:latest

# 或其他中文模型
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
ollama pull deepseek-r1:latest
```

### 3. 启动 Ollama 服务

```bash
ollama serve
```

默认运行在 `http://localhost:11434`

### 4. 配置参数

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:latest
```

### 5. 优点

- ✅ 完全本地运行，无需网络
- ✅ 无需 API Key
- ✅ 免费使用
- ✅ 数据隐私有保障
- ✅ 支持多种开源模型

### 6. 注意事项

- 需要本地安装 Ollama
- 需要足够的硬件资源（建议 8GB+ 内存）
- 首次运行需要下载模型（可能较大）
- 响应速度取决于本地硬件

### 7. 推荐配置

**基础配置** (8GB 内存):
```bash
ollama pull qwen2.5:7b
```

**推荐配置** (16GB+ 内存):
```bash
ollama pull qwen2.5:latest  # 通常是 14B 参数版本
```

**高性能配置** (32GB+ 内存 + GPU):
```bash
ollama pull qwen2.5:32b
```

## 🔄 切换 AI 提供商

### 从 Kimi 切换到 Ollama

1. 确保 Ollama 已安装并运行：
```bash
ollama serve
```

2. 修改 `.env` 文件：
```env
AI_PROVIDER=ollama
```

3. 重启服务：
```bash
python run.py
```

### 从 Ollama 切换到 Kimi

1. 修改 `.env` 文件：
```env
AI_PROVIDER=kimi
```

2. 重启服务

3. 在前端输入 Kimi API Key

## 🎯 使用场景建议

### 选择 Kimi AI 的场景

- 🌐 有稳定的网络连接
- 💰 可以接受按量计费
- 🚀 需要快速响应
- 📊 需要处理大量请求
- 🔒 对数据隐私要求不是特别严格

### 选择 Ollama 的场景

- 🏠 需要离线使用
- 💸 预算有限，需要免费方案
- 🔐 对数据隐私有严格要求
- 🖥️ 有足够的本地计算资源
- 🧪 需要实验不同的开源模型

## 📊 性能对比

| 特性 | Kimi AI | Ollama |
|------|---------|--------|
| 响应速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 中文能力 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 成本 | 按量付费 | 免费 |
| 离线使用 | ❌ | ✅ |
| 部署难度 | 低 | 中 |
| 数据隐私 | 云端 | 本地 |
| 上下文长度 | 128K | 依模型 |

## 🛠️ 开发和调试

### 测试 Kimi AI 连接

```python
from openai import AsyncOpenAI

async def test_kimi():
    client = AsyncOpenAI(
        api_key="your-api-key",
        base_url="https://api.moonshot.cn/v1"
    )
    
    response = await client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "user", "content": "你好"}
        ]
    )
    
    print(response.choices[0].message.content)
```

### 测试 Ollama 连接

```bash
# 测试 Ollama 是否运行
curl http://localhost:11434/api/version

# 测试模型
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:latest",
  "prompt": "你好"
}'
```

```python
import ollama

async def test_ollama():
    client = ollama.AsyncClient()
    
    response = await client.chat(
        model="qwen2.5:latest",
        messages=[
            {"role": "user", "content": "你好"}
        ]
    )
    
    print(response["message"]["content"])
```

## ⚠️ 常见问题

### Kimi AI

**Q: API Key 无效怎么办？**
A: 检查：
1. API Key 是否正确复制
2. API Key 是否已激活
3. 账户余额是否充足

**Q: 请求超时怎么办？**
A: 
1. 检查网络连接
2. 增加 `AI_TIMEOUT` 配置
3. 检查 Kimi 服务状态

### Ollama

**Q: 无法连接到 Ollama？**
A: 检查：
1. Ollama 是否正在运行（`ollama serve`）
2. 端口是否正确（默认 11434）
3. 防火墙是否阻止了连接

**Q: 模型加载失败？**
A: 
1. 确认模型已下载：`ollama list`
2. 重新拉取模型：`ollama pull qwen2.5:latest`
3. 检查磁盘空间

**Q: 生成速度太慢？**
A: 
1. 使用更小的模型（如 7B 版本）
2. 如果有 GPU，确保 Ollama 正确使用
3. 减少 `max_tokens` 配置

## 🔮 未来支持

计划支持的 AI 提供商：

- [ ] OpenAI GPT-4
- [ ] Anthropic Claude
- [ ] 智谱 AI (GLM)
- [ ] 阿里云通义千问
- [ ] 百度文心一言

## 📚 相关文档

- [Kimi AI 官方文档](https://platform.moonshot.cn/docs)
- [Ollama 官方文档](https://github.com/ollama/ollama)
- [OpenAI SDK 文档](https://github.com/openai/openai-python)
- [Ollama Python SDK](https://github.com/ollama/ollama-python)

---

**最后更新**: 2024-11-10
**维护者**: Literature Assistant Team

