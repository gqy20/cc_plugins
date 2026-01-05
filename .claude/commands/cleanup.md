---
name: cleanup
description: Python 代码冗余检测清单
version: 0.0.1
tags:
  - python
  - cleanup
  - redundancy
  - code-quality
dependencies:
  grep: "any"
---

# Python 代码冗余检测

> **先看有什么，再看写什么**

检测代码中是否有可用标准库或已安装包替代的冗余实现。

---

## 快捷命令

```bash
/cleanup              # 显示完整清单
/cleanup scan         # 执行快速扫描
/cleanup <pattern>    # 查看特定模式详情
```

---

## 核心原则

| 原则 | 说明 |
|------|------|
| **依赖优先** | 检查 `uv.lock`，优先用已安装的包 |
| **标准库优先** | Python 内置功能无需安装 |
| **声明即存在** | `pyproject.toml` 中声明的就是可用的 |
| **删除而非兼容** | 不保留"以防万一"的旧代码 |

---

## 冗余模式对照表

| 当前模式 | 应该用 | 检测命令 |
|----------|--------|----------|
| `os.path.join` | `pathlib.Path` | `grep -rn "os.path\."` |
| `class X: def __init__` | `@dataclass` | `grep -rn "def __init__"` |
| `urllib.request` | `requests` | `grep -rn "urllib"` |
| `datetime.strptime` | `dateutil.parser` | `grep -rn "strptime"` |
| `csv.reader/open` | `pandas.read_csv` | `grep -rn "csv\\.reader\|open.*\\.csv"` |
| `try: finally: close()` | `contextlib` | `grep -rn "finally:.*close"` |

---

## 模式详解

### 1. pathlib 替代 os.path

**问题**：`os.path` 操作繁琐，不支持链式调用

```python
# ❌ 冗余
import os
path = os.path.join("data", "files", "test.txt")
if os.path.exists(path):
    with open(path) as f:
        content = f.read()

# ✅ 推荐
from pathlib import Path
path = Path("data") / "files" / "test.txt"
if path.exists():
    content = path.read_text()
```

**检测**：
```bash
grep -rn "os\.path\." src/
```

**替换场景**：
- `os.path.join` → `Path() / "file"`
- `os.path.exists` → `.exists()`
- `os.path.dirname` → `.parent`
- `os.path.basename` → `.name`
- `os.path.splitext` → `.stem` / `.suffix`

---

### 2. dataclasses 替代手动 __init__

**问题**：重复编写 `__init__`、`__repr__`、`__eq__`

```python
# ❌ 冗余
class User:
    def __init__(self, name: str, age: int, email: str):
        self.name = name
        self.age = age
        self.email = email
    def __repr__(self):
        return f"User(name={self.name}, age={self.age}, email={self.email})"
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return (self.name, self.age, self.email) == (other.name, other.age, other.email)

# ✅ 推荐
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
```

**检测**：
```bash
# 查找简单数据容器类（多个 self.xxx = xxx）
grep -Pn "class \w+.*:.*\n    def __init__" src/*.py | head -20
```

**适用信号**：
- 类主要是数据容器
- `__init__` 只做属性赋值
- 需要 `__repr__` 或 `__eq__`

---

### 3. requests 替代 urllib

**问题**：`urllib` API 复杂，错误处理繁琐

```python
# ❌ 冗余
import urllib.request
import urllib.parse
import json

url = "https://api.example.com/users"
data = json.dumps({"name": "Alice"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")

# ✅ 推荐
import requests

response = requests.post("https://api.example.com/users", json={"name": "Alice"})
result = response.json()  # 自动处理 JSON
```

**检测**：
```bash
grep -rn "urllib\." src/
```

**替换场景**：
- `urllib.request.urlopen` → `requests.get/post/put/delete`
- `urllib.parse.urlencode` → `requests` 自动处理
- 手动 JSON 处理 → `json=` 参数

---

### 4. dateutil 替代 strptime

**问题**：`strptime` 需要预知格式，无法处理多种格式

```python
# ❌ 冗余
from datetime import datetime

# 必须指定格式
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
dt2 = datetime.strptime("15/01/2024", "%d/%m/%Y")  # 不同格式需要不同解析

# ✅ 推荐
from dateutil import parser

# 自动识别格式
dt = parser.parse("2024-01-15")
dt2 = parser.parse("15/01/2024")
dt3 = parser.parse("January 15, 2024")
```

**检测**：
```bash
grep -rn "\.strptime" src/
```

**适用场景**：
- 解析用户输入的日期
- 处理多种日期格式
- 不确定具体格式

---

### 5. pandas 替代手动 CSV 处理

**问题**：手动处理 CSV 代码冗长，易出错

```python
# ❌ 冗余
import csv

data = []
with open("data.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append({"name": row["name"], "value": float(row["value"])})

# 筛选、聚合需要更多代码...

# ✅ 推荐
import pandas as pd

df = pd.read_csv("data.csv")
filtered = df[df["value"] > 100]  # 一行搞定
result = df.groupby("category")["value"].sum()
```

**检测**：
```bash
grep -rn "csv\.reader\|csv\.DictReader\|open.*\.csv" src/
```

**适用场景**：
- 需要筛选/聚合/转换数据
- CSV 文件较大
- 需要数据分析

**不适场景**：
- 简单读写（用 `csv` 模块更轻量）
- 流式处理大文件（pandas 需要全部加载）

---

### 6. contextlib 替代 try-finally

**问题**：`try-finally` 样板代码多

```python
# ❌ 冗余
f = open("file.txt")
try:
    data = f.read()
    # 处理数据
finally:
    f.close()

# ✅ 推荐
from contextlib import ExitStack

with open("file.txt") as f:
    data = f.read()
    # 自动关闭
```

**检测**：
```bash
grep -rn "finally:" src/ | grep -i "close\|cleanup"
```

**适用场景**：
- 资源清理（文件、锁、连接）
- 需要管理多个资源（用 `ExitStack`）

---

## 快速扫描

### 一键扫描所有模式

```bash
# 创建扫描脚本
cat > scan_redundancy.sh << 'EOF'
#!/bin/bash
echo "🔍 扫描代码冗余..."
echo ""
echo "1️⃣ os.path 模式："
grep -rn "os\.path\." src/ 2>/dev/null || echo "  ✅ 未发现"
echo ""
echo "2️⃣ urllib 模式："
grep -rn "urllib\." src/ 2>/dev/null || echo "  ✅ 未发现"
echo ""
echo "3️⃣ strptime 模式："
grep -rn "\.strptime" src/ 2>/dev/null || echo "  ✅ 未发现"
echo ""
echo "4️⃣ csv 模式："
grep -rn "csv\.reader\|csv\.DictReader" src/ 2>/dev/null || echo "  ✅ 未发现"
echo ""
echo "5️⃣ finally close 模式："
grep -rn "finally:" src/ | grep -i "close" 2>/dev/null || echo "  ✅ 未发现"
echo ""
echo "6️⃣ 手动 __init__ 模式："
grep -Pn "class \w+.*:.*\n    def __init__" src/*.py 2>/dev/null | head -5 || echo "  ✅ 未发现"
EOF

chmod +x scan_redundancy.sh
./scan_redundancy.sh
```

### 按模式扫描

```bash
# 检查 uv.lock 中已安装的包
grep -A 100 "dependencies = \[" uv.lock | grep 'name = ' | cut -d'"' -f2

# 只检查已安装包相关的冗余
if grep -q "requests" uv.lock; then
    echo "📦 已安装 requests，检查 urllib..."
    grep -rn "urllib" src/
fi
```

---

## 完整示例

### 场景：重构 API 客户端

**Before**（冗余）：
```python
import urllib.request
import json
from datetime import datetime

class APIClient:
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url
        self.timeout = timeout

    def get_user(self, user_id: int):
        url = f"{self.base_url}/users/{user_id}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                user = data["user"]
                user["created_at"] = datetime.strptime(user["created_at"], "%Y-%m-%d")
                return user
        except urllib.error.HTTPError as e:
            return None
```

**After**（清理后）：
```python
import requests
from dateutil import parser
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime

class APIClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_user(self, user_id: int) -> Optional[User]:
        response = requests.get(
            f"{self.base_url}/users/{user_id}",
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()["user"]
        data["created_at"] = parser.parse(data["created_at"])
        return User(**data)
```

**改进**：
- `urllib` → `requests`（更简洁）
- `datetime.strptime` → `dateutil.parser.parse`（自动识别格式）
- 手动 `__init__` → `@dataclass`（自动生成 `__repr__`、`__eq__`）
- 添加类型提示（`Optional[User]`）

---

## 工具推荐

| 工具 | 用途 | 安装 |
|------|------|------|
| **ruff** | Lint & Format | `uv add ruff` |
| **mypy** | 类型检查 | `uv add mypy` |
| **grep** | 模式搜索 | 系统自带 |

---

**写代码前先看 `uv.lock`**
