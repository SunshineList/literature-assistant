## 🎨 项目中使用的设计模式全面总结

本项目在架构设计中广泛应用了多种设计模式，以提高代码质量、可维护性和可扩展性。

## 📋 设计模式应用清单

### 1. 策略模式 (Strategy Pattern)

#### 应用场景 1: AI 提供商

**位置**: `app/services/ai_providers/`

**问题**: 需要支持多个 AI 服务提供商（Kimi AI, Ollama），每个提供商有不同的实现方式

**解决方案**:
```
AIProvider (抽象基类)
    ├── KimiProvider
    └── OllamaProvider
```

**核心代码**:
```python
# 基类定义统一接口
class AIProvider(ABC):
    @abstractmethod
    async def generate_stream(self, system_prompt, user_message, api_key):
        pass
    
    @abstractmethod
    async def generate(self, system_prompt, user_message, api_key):
        pass

# 具体策略
class KimiProvider(AIProvider):
    async def generate_stream(self, ...):
        # Kimi 特定实现

class OllamaProvider(AIProvider):
    async def generate_stream(self, ...):
        # Ollama 特定实现
```

**优点**:
- ✅ 新增 AI 提供商只需实现接口
- ✅ 各提供商独立变化，互不影响
- ✅ 运行时可以切换提供商

#### 应用场景 2: 文件解析器

**位置**: `app/services/file_parsers/`

**问题**: 需要支持多种文件格式（PDF, Word, Markdown），每种格式的解析方式不同

**解决方案**:
```
FileParser (抽象基类)
    ├── PDFParser
    ├── WordParser
    └── MarkdownParser
```

**核心代码**:
```python
class FileParser(ABC):
    @abstractmethod
    async def parse(self, file_path: str) -> str:
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        pass

# 具体策略
class PDFParser(FileParser):
    async def parse(self, file_path):
        # PDF 解析逻辑
    
    @property
    def supported_extensions(self):
        return ['pdf']
```

**优点**:
- ✅ 添加新文件格式无需修改现有代码
- ✅ 每种格式的解析逻辑独立封装
- ✅ 易于测试和维护

---

### 2. 工厂模式 (Factory Pattern)

#### 应用场景 1: AI 提供商工厂

**位置**: `app/services/ai_providers/factory.py`

**问题**: 根据配置动态创建不同的 AI 提供商实例

**解决方案**:
```python
class AIProviderFactory:
    _providers = {
        "kimi": KimiProvider,
        "ollama": OllamaProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, **config) -> AIProvider:
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise AIException(f"不支持的提供商: {provider_name}")
        return provider_class(**config)
```

**优点**:
- ✅ 客户端代码不依赖具体实现
- ✅ 集中管理创建逻辑
- ✅ 易于扩展新类型

#### 应用场景 2: 文件解析器工厂

**位置**: `app/services/file_parsers/factory.py`

**问题**: 根据文件扩展名动态创建对应的解析器

**解决方案**:
```python
class FileParserFactory:
    _extension_map = {
        'pdf': PDFParser,
        'docx': WordParser,
        'md': MarkdownParser,
    }
    
    @classmethod
    def get_parser(cls, file_extension: str) -> FileParser:
        parser_class = cls._extension_map.get(file_extension)
        if not parser_class:
            raise FileException(f"不支持的文件类型")
        return parser_class()
```

**优点**:
- ✅ 自动映射文件类型到解析器
- ✅ 支持动态注册新解析器
- ✅ 统一的创建入口

---

### 3. 建造者模式 (Builder Pattern)

#### 应用场景 1: 查询构建器

**位置**: `app/services/query_builders/literature_query_builder.py`

**问题**: 文献查询有多个可选条件（关键词、标签、日期范围、分页等），需要灵活组合

**解决方案**:
```python
class LiteratureQueryBuilder:
    def with_keyword(self, keyword: str) -> "LiteratureQueryBuilder":
        if keyword:
            self._conditions.append(...)
        return self
    
    def with_tags(self, tags: list) -> "LiteratureQueryBuilder":
        if tags:
            self._conditions.append(...)
        return self
    
    def with_pagination(self, page_num, page_size) -> "LiteratureQueryBuilder":
        self._offset = (page_num - 1) * page_size
        self._limit = page_size
        return self
    
    def build_query(self) -> Select:
        return select(Literature).where(and_(*self._conditions))...
```

**使用示例**:
```python
# 链式调用构建复杂查询
query_builder = (
    LiteratureQueryBuilder()
    .with_keyword("机器学习")
    .with_tags(["AI", "深度学习"])
    .with_date_range("2024-01-01", "2024-12-31")
    .with_pagination(1, 10)
    .order_by_create_time(descending=True)
)

query = query_builder.build_query()
```

**优点**:
- ✅ 链式调用，代码清晰易读
- ✅ 条件灵活组合，复用性强
- ✅ 避免构造函数参数过多

#### 应用场景 2: 响应构建器

**位置**: `app/core/response_builder.py`

**问题**: API 响应需要包含多个字段（success, message, data, code），希望提供灵活的构建方式

**解决方案**:
```python
class ResponseBuilder:
    def success(self, is_success: bool) -> "ResponseBuilder":
        self._success = is_success
        return self
    
    def message(self, message: str) -> "ResponseBuilder":
        self._message = message
        return self
    
    def data(self, data: T) -> "ResponseBuilder":
        self._data = data
        return self
    
    def code(self, code: int) -> "ResponseBuilder":
        self._code = code
        return self
    
    def build(self) -> Response:
        return Response(...)
```

**使用示例**:
```python
# 方式1: 链式调用
response = (
    ResponseBuilder()
    .success(True)
    .message("操作成功")
    .data({"id": 1})
    .code(200)
    .build()
)

# 方式2: 快捷方法
response = ResponseBuilder.ok(data=result, message="查询成功")
response = ResponseBuilder.not_found(message="资源不存在")
response = ResponseBuilder.error(message="服务器错误", code=500)
```

**优点**:
- ✅ API 更加语义化
- ✅ 提供多种构建方式
- ✅ 易于扩展新的响应类型

#### 应用场景 3: 分页数据构建器

**位置**: `app/core/response_builder.py`

**解决方案**:
```python
class PageDataBuilder:
    def records(self, records: list) -> "PageDataBuilder":
        self._records = records
        return self
    
    def total(self, total: int) -> "PageDataBuilder":
        self._total = total
        return self
    
    def pagination(self, page_num, page_size) -> "PageDataBuilder":
        self._page_num = page_num
        self._page_size = page_size
        return self
    
    @classmethod
    def from_query_result(cls, records, total, page_num, page_size):
        return (cls()
            .records(records)
            .total(total)
            .pagination(page_num, page_size)
            .build())
```

**优点**:
- ✅ 统一的分页数据构建方式
- ✅ 支持快捷创建方法

---

### 4. 外观模式 (Facade Pattern)

#### 应用场景: AI 服务外观

**位置**: `app/services/ai_service.py`

**问题**: AI 服务涉及工厂创建、提示词加载、提供商调用等多个子系统，客户端不应关心这些细节

**解决方案**:
```python
class AIService:
    def __init__(self):
        # 内部管理配置和工厂
        self.provider_name = settings.AI_PROVIDER
        self.provider_config = {...}
    
    def _get_provider(self, api_key):
        # 隐藏工厂创建细节
        return AIProviderFactory.create_provider(...)
    
    async def generate_reading_guide_stream(self, content, api_key):
        # 对外提供简单接口
        system_prompt = load_prompt("literature-guide-system-prompt")
        provider = self._get_provider(api_key)
        async for message in provider.generate_stream(...):
            yield message
```

**优点**:
- ✅ 简化客户端调用
- ✅ 隐藏子系统复杂性
- ✅ 提供统一的高层接口

---

### 5. 单例模式 (Singleton Pattern)

#### 应用场景: 全局服务实例

**位置**: 各服务模块

**问题**: 服务类无需多实例，全局共享一个实例即可

**解决方案**:
```python
# ai_service.py
class AIService:
    def __init__(self):
        # 初始化配置

# 创建全局单例
ai_service = AIService()

# file_service.py
class FileService:
    def __init__(self):
        # 初始化配置

file_service = FileService()

# literature_service.py
literature_service = LiteratureService()
```

**优点**:
- ✅ 节省资源
- ✅ 全局访问点
- ✅ 避免重复初始化

---

## 🏗️ 设计模式协作图

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (外观)                      │
│                  literature.py                          │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐      ┌────────────────┐
│  AIService    │      │FileService     │
│  (外观)       │      │ (外观)         │
└───────┬───────┘      └───────┬────────┘
        │                      │
        │                      ▼
        │              ┌───────────────────┐
        │              │FileParserFactory  │
        │              │    (工厂)         │
        │              └───────┬───────────┘
        │                      │
        │              ┌───────┴─────────┐
        │              │                 │
        │              ▼                 ▼
        │          PDFParser        WordParser
        │          (策略)           (策略)
        │
        ▼
┌──────────────────┐
│AIProviderFactory │
│     (工厂)       │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
KimiProvider  OllamaProvider
  (策略)        (策略)
```

## 📊 设计模式对比

| 设计模式 | 使用场景 | 主要优点 | 使用位置 |
|---------|---------|---------|---------|
| **策略模式** | AI提供商、文件解析器 | 算法可替换、易扩展 | `ai_providers/`, `file_parsers/` |
| **工厂模式** | 创建AI提供商、解析器 | 解耦创建逻辑 | `factory.py` 文件 |
| **建造者模式** | 查询构建、响应构建 | 链式调用、灵活组合 | `query_builders/`, `response_builder.py` |
| **外观模式** | AI服务、文件服务 | 简化接口、隐藏复杂性 | 各 Service 类 |
| **单例模式** | 全局服务实例 | 节省资源、全局访问 | 服务模块 |

## 🎯 设计原则遵循

### SOLID 原则

1. **单一职责原则 (SRP)**
   - ✅ 每个策略类只负责一种算法
   - ✅ 工厂类只负责创建对象
   - ✅ 建造者只负责构建对象

2. **开闭原则 (OCP)**
   - ✅ 新增AI提供商/文件解析器不修改现有代码
   - ✅ 通过继承扩展，而非修改

3. **里氏替换原则 (LSP)**
   - ✅ 所有策略都可以互相替换
   - ✅ 遵循相同的接口契约

4. **接口隔离原则 (ISP)**
   - ✅ 接口精简且必要
   - ✅ 不强制实现不需要的方法

5. **依赖倒置原则 (DIP)**
   - ✅ 依赖抽象而非具体实现
   - ✅ 通过工厂注入依赖

## 🚀 扩展示例

### 添加新的 AI 提供商

```python
# 1. 创建策略
class OpenAIProvider(AIProvider):
    async def generate_stream(self, ...):
        # 实现
        pass

# 2. 注册到工厂
AIProviderFactory._providers["openai"] = OpenAIProvider

# 3. 添加配置
settings.AI_PROVIDER = "openai"

# 完成！无需修改现有代码
```

### 添加新的文件解析器

```python
# 1. 创建策略
class ExcelParser(FileParser):
    async def parse(self, file_path):
        # 实现
        pass
    
    @property
    def supported_extensions(self):
        return ['xlsx', 'xls']

# 2. 注册
FileParserFactory.register_parser(ExcelParser)

# 完成！自动支持Excel文件
```

## 📝 最佳实践

1. **优先使用组合而非继承**
   - ✅ 策略模式使用组合关系
   - ✅ 更灵活，运行时可替换

2. **面向接口编程**
   - ✅ 所有策略实现抽象基类
   - ✅ 客户端依赖接口而非实现

3. **保持类的单一职责**
   - ✅ 工厂只负责创建
   - ✅ 策略只负责算法
   - ✅ 建造者只负责构建

4. **使用建造者处理复杂对象**
   - ✅ 多个可选参数时使用建造者
   - ✅ 提供链式API

5. **外观模式简化接口**
   - ✅ 隐藏子系统复杂性
   - ✅ 提供高层统一接口

## 🔍 代码质量指标

通过应用这些设计模式，项目达到了以下质量指标：

- ✅ **可维护性**: 高内聚低耦合
- ✅ **可扩展性**: 符合开闭原则
- ✅ **可测试性**: 依赖抽象，易于Mock
- ✅ **可读性**: 代码结构清晰，职责明确
- ✅ **可复用性**: 策略和建造者可独立复用

---

**最后更新**: 2024-11-10
**维护者**: Literature Assistant Team

