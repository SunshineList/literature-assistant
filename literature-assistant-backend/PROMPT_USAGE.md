# 提示词使用指南

## 📝 概述

本项目使用文件化的提示词管理系统，所有提示词存储在 `app/prompts/` 目录下，支持动态加载、缓存和变量替换。

## 📁 提示词文件

### 当前提示词

1. **literature-guide-system-prompt.txt**
   - 用途：生成文献阅读指南的系统提示词
   - 包含：角色定义、工作流程、输出格式要求
   - 使用场景：AI 生成阅读指南时的系统指令

2. **literature-classification-system-prompt.txt**
   - 用途：从阅读指南中提取标签和描述
   - 包含：分类规则、输出格式、JSON 格式要求
   - 使用场景：自动分类和标签提取

## 🔧 使用方法

### 方法一：直接加载（推荐）

```python
from app.utils.prompt_loader import load_prompt

# 加载提示词（自动缓存）
system_prompt = load_prompt("literature-guide-system-prompt")

# 使用提示词
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input}
]
```

### 方法二：使用装饰器

```python
from app.utils.prompt_loader import with_prompt

@with_prompt("literature-guide-system-prompt", param_name="system_prompt")
async def generate_guide(content: str, system_prompt: str = None):
    # system_prompt 会被自动注入
    print(system_prompt)  # 已加载的提示词内容
    # ... 业务逻辑
```

### 方法三：使用 PromptLoader 实例

```python
from app.utils.prompt_loader import PromptLoader

# 创建加载器
loader = PromptLoader()

# 加载提示词
prompt = loader.load_prompt("literature-guide-system-prompt")

# 支持变量替换
prompt_with_vars = loader.get_prompt(
    "some-prompt-with-variables",
    variable1="value1",
    variable2="value2"
)

# 重新加载（清除缓存）
fresh_prompt = loader.reload_prompt("literature-guide-system-prompt")
```

## 📖 实际应用示例

### 示例1：在 AI 服务中使用

```python
# app/services/ai_service.py

from app.utils.prompt_loader import load_prompt

class AIService:
    async def generate_reading_guide_stream(self, content: str, api_key: str):
        # 加载系统提示词
        system_prompt = load_prompt("literature-guide-system-prompt")
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下文献生成阅读指南：\n\n{content}"}
        ]
        
        # 调用 AI API
        # ...
```

### 示例2：提取标签和描述

```python
# app/services/ai_service.py

async def extract_tags_and_description(self, reading_guide: str):
    # 加载分类提示词
    system_prompt = load_prompt("literature-classification-system-prompt")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"文献阅读指南：\n\n{reading_guide}"}
    ]
    
    # 调用 AI API 提取
    # ...
```

## 🎯 提示词变量替换

如果提示词中包含变量占位符（使用 `{variable_name}` 格式），可以这样使用：

### 创建带变量的提示词文件

```text
# my-prompt-with-vars.txt

你是一位{role}，专长于{specialty}。

请帮助用户完成以下任务：{task}
```

### 使用时替换变量

```python
from app.utils.prompt_loader import load_prompt

prompt = load_prompt(
    "my-prompt-with-vars",
    role="数据分析师",
    specialty="统计建模和数据可视化",
    task="分析销售数据趋势"
)

print(prompt)
# 输出：
# 你是一位数据分析师，专长于统计建模和数据可视化。
# 请帮助用户完成以下任务：分析销售数据趋势
```

## 📋 提示词命名规范

- 使用小写字母和连字符
- 描述性命名，清晰表达用途
- 统一使用 `.txt` 扩展名

示例：
- ✅ `literature-guide-system-prompt.txt`
- ✅ `literature-classification-system-prompt.txt`
- ✅ `error-analysis-prompt.txt`
- ❌ `prompt1.txt`
- ❌ `GUIDE_PROMPT.txt`

## 🔄 提示词缓存机制

提示词加载器使用 `@lru_cache` 装饰器实现缓存：

- **首次加载**：从文件读取并缓存
- **后续加载**：直接从缓存返回（提升性能）
- **缓存大小**：最多缓存 32 个提示词
- **手动清除**：使用 `reload_prompt()` 方法

```python
from app.utils.prompt_loader import prompt_loader

# 清除特定提示词缓存
prompt_loader.reload_prompt("literature-guide-system-prompt")

# 清除所有缓存
prompt_loader.load_prompt.cache_clear()
```

## 🛠️ 最佳实践

### 1. 提示词版本管理

为重要的提示词创建版本备份：

```
app/prompts/
├── literature-guide-system-prompt.txt       # 当前版本
├── literature-guide-system-prompt-v1.txt    # 备份版本1
└── literature-guide-system-prompt-v2.txt    # 备份版本2
```

### 2. 提示词测试

在修改提示词后，建议进行测试：

```python
# tests/test_prompts.py

def test_prompt_loading():
    from app.utils.prompt_loader import load_prompt
    
    # 测试加载
    prompt = load_prompt("literature-guide-system-prompt")
    assert prompt is not None
    assert len(prompt) > 0
    
    # 测试内容
    assert "Role:" in prompt
    assert "Workflow:" in prompt
```

### 3. 提示词文档化

在提示词文件开头添加注释说明：

```text
# literature-guide-system-prompt.txt
# 用途：生成文献阅读指南的系统提示词
# 版本：v1.0
# 最后更新：2024-11-10
# 作者：Literature Assistant Team

# Role: 资深学术导师
...
```

### 4. 模块化提示词

对于复杂的提示词，可以拆分为多个文件：

```python
from app.utils.prompt_loader import load_prompt

# 加载多个提示词片段
role_prompt = load_prompt("role-definition")
workflow_prompt = load_prompt("workflow-steps")
output_format_prompt = load_prompt("output-format")

# 组合使用
full_prompt = f"{role_prompt}\n\n{workflow_prompt}\n\n{output_format_prompt}"
```

## 🔍 调试技巧

### 查看加载的提示词

```python
from app.utils.prompt_loader import load_prompt

prompt = load_prompt("literature-guide-system-prompt")
print("=" * 50)
print("提示词内容：")
print("=" * 50)
print(prompt)
print("=" * 50)
print(f"提示词长度：{len(prompt)} 字符")
```

### 验证提示词文件

```python
from pathlib import Path

prompts_dir = Path("app/prompts")
print("可用的提示词文件：")
for prompt_file in prompts_dir.glob("*.txt"):
    print(f"  - {prompt_file.name}")
```

## 📚 相关资源

- 提示词编写指南：[OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- Markdown 格式规范：[CommonMark Spec](https://commonmark.org/)
- Mermaid 图表语法：[Mermaid Documentation](https://mermaid.js.org/)

## ❓ 常见问题

### Q: 如何添加新的提示词？

A: 在 `app/prompts/` 目录下创建新的 `.txt` 文件，然后使用 `load_prompt()` 加载即可。

### Q: 提示词文件找不到怎么办？

A: 检查以下几点：
1. 文件是否在 `app/prompts/` 目录下
2. 文件扩展名是否为 `.txt`
3. 文件名是否正确（区分大小写）

### Q: 如何更新已缓存的提示词？

A: 使用 `reload_prompt()` 方法：
```python
from app.utils.prompt_loader import prompt_loader
prompt_loader.reload_prompt("your-prompt-name")
```

### Q: 支持其他格式的提示词文件吗？

A: 目前只支持 `.txt` 格式。如果需要其他格式，可以修改 `PromptLoader` 类的 `load_prompt()` 方法。

---

**最后更新**: 2024-11-10
**维护者**: Literature Assistant Team

