# .env 文件 vs Config 文件对比

## 1. .env 文件方式（当前使用）

### 特点
- **格式**：简单的键值对，每行一个配置
- **加载方式**：通过 `python-dotenv` 库自动加载为环境变量
- **安全性**：通常包含敏感信息，不提交到 Git

### 示例
```bash
# .env 文件
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.example.com/v1
MODEL=moonshot-v1-8k
```

### 代码使用
```python
import os
from dotenv import load_dotenv

load_dotenv()  # 自动加载 .env 文件
api_key = os.getenv("OPENAI_API_KEY")  # 读取环境变量
```

---

## 2. Config 文件方式（传统方式）

### 2.1 Python Config 文件（config.py）

#### 特点
- **格式**：Python 代码，可以包含逻辑
- **加载方式**：直接 `import config`
- **灵活性**：可以写函数、类、条件判断等

#### 示例
```python
# config.py
API_KEY = "sk-xxx"
BASE_URL = "https://api.example.com/v1"
MODEL = "moonshot-v1-8k"

# 可以包含逻辑
if os.getenv("ENV") == "production":
    API_KEY = os.getenv("PROD_API_KEY")
else:
    API_KEY = os.getenv("DEV_API_KEY")
```

#### 代码使用
```python
import config

api_key = config.API_KEY
```

### 2.2 JSON Config 文件（config.json）

#### 特点
- **格式**：JSON 格式，结构化数据
- **加载方式**：使用 `json` 库读取
- **适用场景**：配置项较多，需要嵌套结构

#### 示例
```json
{
  "openai": {
    "api_key": "sk-xxx",
    "base_url": "https://api.example.com/v1",
    "model": "moonshot-v1-8k"
  },
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
```

#### 代码使用
```python
import json

with open("config.json") as f:
    config = json.load(f)
api_key = config["openai"]["api_key"]
```

### 2.3 YAML Config 文件（config.yaml）

#### 特点
- **格式**：YAML 格式，可读性好
- **加载方式**：使用 `pyyaml` 库读取
- **适用场景**：复杂配置，需要注释

#### 示例
```yaml
openai:
  api_key: sk-xxx
  base_url: https://api.example.com/v1
  model: moonshot-v1-8k

database:
  host: localhost
  port: 5432
```

---

## 对比总结

| 特性 | .env 文件 | config.py | config.json | config.yaml |
|------|-----------|-----------|-------------|-------------|
| **格式** | 键值对 | Python 代码 | JSON | YAML |
| **安全性** | ⭐⭐⭐⭐⭐ 不提交 Git | ⭐⭐⭐ 可能提交 | ⭐⭐⭐ 可能提交 | ⭐⭐⭐ 可能提交 |
| **简单性** | ⭐⭐⭐⭐⭐ 最简单 | ⭐⭐⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐⭐ 复杂 |
| **灵活性** | ⭐⭐ 仅键值对 | ⭐⭐⭐⭐⭐ 可写逻辑 | ⭐⭐⭐ 结构化 | ⭐⭐⭐⭐ 结构化+注释 |
| **环境变量** | ⭐⭐⭐⭐⭐ 原生支持 | ⭐⭐⭐ 需手动处理 | ⭐⭐ 需手动处理 | ⭐⭐ 需手动处理 |
| **跨语言** | ⭐⭐⭐⭐⭐ 通用 | ⭐ 仅 Python | ⭐⭐⭐⭐ 通用 | ⭐⭐⭐⭐ 通用 |
| **适用场景** | 敏感配置、环境变量 | 简单项目、Python专用 | 复杂配置、多语言 | 复杂配置、DevOps |

---

## 推荐使用场景

### 使用 .env 文件 ✅
- **敏感信息**（API Key、密码、Token）
- **环境变量配置**（开发/测试/生产环境）
- **12-Factor App 标准**
- **Docker、云部署**（环境变量是标准做法）

### 使用 config.py ✅
- **简单 Python 项目**
- **需要配置逻辑**（条件判断、计算等）
- **团队都是 Python 开发者**

### 使用 config.json ✅
- **复杂配置结构**
- **需要版本控制配置模板**
- **多语言项目共享配置**

### 使用 config.yaml ✅
- **DevOps、CI/CD 配置**
- **需要详细注释的配置**
- **Kubernetes、Docker Compose 等**

---

## 最佳实践建议

### 混合使用（推荐）✨
```python
# config.py - 非敏感配置
DEFAULT_MODEL = "moonshot-v1-8k"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# .env - 敏感配置（不提交到 Git）
# OPENAI_API_KEY=sk-xxx
# OPENAI_BASE_URL=https://api.example.com/v1

# 代码中
import os
from dotenv import load_dotenv
import config

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 从 .env 读取
model = config.DEFAULT_MODEL  # 从 config.py 读取
```

这样既安全又灵活！

