# 设计模式说明

本项目在 AI 服务层采用了多种设计模式，以提高代码的可维护性、可扩展性和可测试性。

## 🎯 核心设计模式

### 1. 策略模式 (Strategy Pattern)

**位置**: `app/services/ai_providers/`

**目的**: 封装不同的 AI 提供商实现，使它们可以互相替换

**实现**:

```
AIProvider (抽象基类)
    ├── KimiProvider (Kimi AI 实现)
    └── OllamaProvider (Ollama 实现)
```

**优点**:
- ✅ 新增 AI 提供商只需实现 `AIProvider` 接口
- ✅ 不同提供商之间可以无缝切换
- ✅ 每个提供商独立封装，互不影响
- ✅ 符合开闭原则（对扩展开放，对修改关闭）

**代码示例**:

```python
# 基类定义统一接口
class AIProvider(ABC):
    @abstractmethod
    async def generate_stream(self, system_prompt, user_message, api_key):
        pass
    
    @abstractmethod
    async def generate(self, system_prompt, user_message, api_key):
        pass

# Kimi 实现
class KimiProvider(AIProvider):
    async def generate_stream(self, system_prompt, user_message, api_key):
        # Kimi 特定实现
        client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)
        # ...

# Ollama 实现
class OllamaProvider(AIProvider):
    async def generate_stream(self, system_prompt, user_message, api_key):
        # Ollama 特定实现
        client = ollama.AsyncClient(host=self.base_url)
        # ...
```

### 2. 工厂模式 (Factory Pattern)

**位置**: `app/services/ai_providers/factory.py`

**目的**: 根据配置动态创建 AI 提供商实例

**实现**:

```python
class AIProviderFactory:
    _providers = {
        "kimi": KimiProvider,
        "ollama": OllamaProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, **config) -> AIProvider:
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise AIException(f"不支持的提供商: {provider_name}")
        return provider_class(**config)
```

**优点**:
- ✅ 客户端代码不需要知道具体的提供商类
- ✅ 集中管理所有提供商的创建逻辑
- ✅ 易于添加新的提供商类型
- ✅ 支持运行时动态选择提供商

**使用示例**:

```python
# 创建 Kimi 提供商
provider = AIProviderFactory.create_provider("kimi", base_url="...", model="...")

# 创建 Ollama 提供商
provider = AIProviderFactory.create_provider("ollama", base_url="...", model="...")
```

### 3. 单例模式 (Singleton Pattern)

**位置**: `app/services/ai_service.py`

**目的**: 确保 AI 服务只有一个实例，节省资源

**实现**:

```python
class AIService:
    def __init__(self):
        # 初始化配置
        pass

# 创建全局唯一实例
ai_service = AIService()
```

**优点**:
- ✅ 避免重复初始化配置
- ✅ 全局访问点
- ✅ 节省资源

### 4. 外观模式 (Facade Pattern)

**位置**: `app/services/ai_service.py`

**目的**: 为复杂的 AI 提供商系统提供简单的统一接口

**实现**:

```python
class AIService:
    def _get_provider(self, api_key):
        # 内部处理提供商创建和配置
        return AIProviderFactory.create_provider(...)
    
    async def generate_reading_guide_stream(self, content, api_key):
        # 对外暴露简单接口
        provider = self._get_provider(api_key)
        async for message in provider.generate_stream(...):
            yield message
```

**优点**:
- ✅ 隐藏内部复杂性
- ✅ 提供简单易用的 API
- ✅ 客户端不需要了解工厂和策略的细节

## 📊 架构图

### AI 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                     AIService                           │
│                   (Facade 外观层)                        │
│  - generate_reading_guide_stream()                      │
│  - extract_tags_and_description()                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               AIProviderFactory                         │
│                  (Factory 工厂)                         │
│  - create_provider(name, **config)                      │
│  - register_provider(name, class)                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌───────────────┐
│ KimiProvider  │          │OllamaProvider │
│  (Strategy)   │          │  (Strategy)   │
├───────────────┤          ├───────────────┤
│+ generate_    │          │+ generate_    │
│  stream()     │          │  stream()     │
│+ generate()   │          │+ generate()   │
└───────────────┘          └───────────────┘
```

## 🔌 扩展新的 AI 提供商

### 步骤 1: 创建提供商类

```python
# app/services/ai_providers/openai_provider.py

from app.services.ai_providers.base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self, **config):
        super().__init__(**config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")
    
    async def generate_stream(self, system_prompt, user_message, api_key=None, **kwargs):
        # OpenAI 特定实现
        pass
    
    async def generate(self, system_prompt, user_message, api_key=None, **kwargs):
        # OpenAI 特定实现
        pass
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    @property
    def requires_api_key(self) -> bool:
        return True
```

### 步骤 2: 注册到工厂

```python
# app/services/ai_providers/factory.py

from app.services.ai_providers.openai_provider import OpenAIProvider

class AIProviderFactory:
    _providers = {
        "kimi": KimiProvider,
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,  # 新增
    }
```

### 步骤 3: 添加配置

```python
# app/config.py

class Settings(BaseSettings):
    AI_PROVIDER: Literal["kimi", "ollama", "openai"] = "kimi"
    
    # OpenAI 配置
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
```

### 步骤 4: 更新服务层配置

```python
# app/services/ai_service.py

class AIService:
    def __init__(self):
        # ...
        
        # OpenAI 特定配置
        elif self.provider_name == "openai":
            self.provider_config.update({
                "base_url": settings.OPENAI_BASE_URL,
                "model": settings.OPENAI_MODEL
            })
```

完成！新的提供商就可以使用了。

## 🎨 设计原则

### SOLID 原则

1. **单一职责原则 (SRP)**
   - 每个提供商类只负责与特定 AI 服务的交互
   - 工厂类只负责创建实例
   - 服务类只负责协调和外观

2. **开闭原则 (OCP)**
   - 新增提供商不需要修改现有代码
   - 通过继承 `AIProvider` 扩展功能

3. **里氏替换原则 (LSP)**
   - 所有提供商都可以互相替换
   - 都遵循相同的接口契约

4. **接口隔离原则 (ISP)**
   - `AIProvider` 定义的接口精简且必要
   - 不强制实现不需要的方法

5. **依赖倒置原则 (DIP)**
   - 服务层依赖抽象（`AIProvider`）而不是具体实现
   - 通过工厂创建实例，解耦依赖

## 📝 使用示例

### 基本使用

```python
from app.services.ai_service import ai_service

# 生成阅读指南（自动使用配置的提供商）
async for message in ai_service.generate_reading_guide_stream(content, api_key):
    print(message)
```

### 动态切换提供商

```python
# 方式 1: 通过环境变量
# .env
AI_PROVIDER=ollama

# 方式 2: 通过代码（不推荐，仅用于测试）
from app.services.ai_providers.factory import AIProviderFactory

provider = AIProviderFactory.create_provider("kimi", model="moonshot-v1-8k")
```

### 注册自定义提供商

```python
from app.services.ai_providers.factory import AIProviderFactory
from my_custom_provider import MyCustomProvider

# 注册
AIProviderFactory.register_provider("custom", MyCustomProvider)

# 使用
provider = AIProviderFactory.create_provider("custom", **config)
```

## 🧪 测试策略

### 测试提供商

```python
import pytest
from app.services.ai_providers.kimi_provider import KimiProvider

@pytest.mark.asyncio
async def test_kimi_provider():
    provider = KimiProvider(
        base_url="https://api.moonshot.cn/v1",
        model="moonshot-v1-8k"
    )
    
    result = await provider.generate(
        system_prompt="你是一个助手",
        user_message="你好",
        api_key="test-key"
    )
    
    assert result is not None
```

### 测试工厂

```python
def test_factory_create_provider():
    provider = AIProviderFactory.create_provider("kimi")
    assert provider.name == "Kimi AI"
    
    provider = AIProviderFactory.create_provider("ollama")
    assert provider.name == "Ollama"
```

### Mock 测试

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_ai_service_with_mock():
    with patch('app.services.ai_service.AIProviderFactory') as mock_factory:
        mock_provider = AsyncMock()
        mock_factory.create_provider.return_value = mock_provider
        
        # 测试逻辑
        # ...
```

## 🔍 代码审查清单

添加新提供商时，请确保：

- [ ] 继承自 `AIProvider` 基类
- [ ] 实现所有抽象方法
- [ ] 正确处理异常并抛出 `AIException`
- [ ] 实现 `name` 和 `requires_api_key` 属性
- [ ] 在工厂中注册
- [ ] 添加配置项到 `Settings`
- [ ] 更新 `AIService.__init__` 中的配置逻辑
- [ ] 编写单元测试
- [ ] 更新文档

## 📚 参考资料

- [策略模式详解](https://refactoringguru.cn/design-patterns/strategy)
- [工厂模式详解](https://refactoringguru.cn/design-patterns/factory-method)
- [外观模式详解](https://refactoringguru.cn/design-patterns/facade)
- [Python 设计模式](https://python-patterns.guide/)

---

**最后更新**: 2024-11-10
**维护者**: Literature Assistant Team

