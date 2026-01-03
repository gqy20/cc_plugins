---
name: bdd
description: 行为驱动开发（BDD）流程助手
version: 0.0.1
tags:
  - bdd
  - testing
  - workflow
  - acceptance
dependencies:
  git: "any"
---

# BDD 行为驱动开发

> **业务语言描述测试，连接需求与代码**

用自然语言描述验收标准，让业务、开发、测试达成共识。

---

## 快捷命令

```bash
/bdd                 # 交互式引导
/bdd feature         # 创建 Feature 文件
/bdd step            # 实现步骤定义
/bdd run             # 运行 BDD 测试
```

---

## 1. BDD 与 TDD 分层

```
┌─────────────────────────────────────────┐
│  BDD - 验收测试 (behave)                │
│  Feature: 用户登录                       │
│  Scenario: 错误密码登录                  │
│  → 描述业务价值                          │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  TDD - 单元测试 (pytest)                │
│  def test_login(): ...                  │
│  → 保证代码质量                          │
└─────────────────────────────────────────┘
```

| 层次 | 工具 | 关注点 | 执行频率 |
|------|------|--------|----------|
| **E2E/验收** | behave | 业务场景 | 每次提交 |
| **集成** | pytest | 模块交互 | 开发中 |
| **单元** | pytest | 函数逻辑 | 开发中 |

---

## 2. Gherkin 语法

### 2.1 基本结构

```gherkin
Feature: [功能名称]

  Scenario: [场景名称]
    Given [前置条件]
    When [执行操作]
    Then [预期结果]
```

### 2.2 关键字

| 关键字 | 用途 | 示例 |
|--------|------|------|
| `Feature` | 功能描述 | `Feature: 用户登录` |
| `Scenario` | 具体场景 | `Scenario: 使用错误密码` |
| `Given` | 前置条件 | `Given 用户在登录页` |
| `When` | 执行动作 | `When 点击登录按钮` |
| `Then` | 验证结果 | `Then 显示错误提示` |
| `And` | 补充条件 | `And 输入用户名` |
| `But` | 替代条件 | `But 密码为空` |

### 2.3 场景大纲

```gherkin
Scenario Outline: 多用户登录
  Given 用户 <username> 存在
  When 使用密码 <password> 登录
  Then 返回状态 <status>

  Examples:
    | username | password | status |
    | alice    | correct  | success |
    | bob      | wrong    | failed  |
```

---

## 3. 项目结构

```
project/
├── features/
│   ├── login.feature          # Gherkin 场景
│   └── user_profile.feature
├── features/steps/
│   ├── login_steps.py         # 步骤定义
│   └── profile_steps.py
└── features/environment.py    # 环境配置
```

---

## 4. 步骤定义

### 4.1 基本模式

```python
from behave import given, when, then
from pytest import raises

@given('用户在登录页面')
def step_login_page(context):
    context.page = LoginPage()

@when('输入用户名 "{username}" 和密码 "{password}"')
def step_input_credentials(context, username, password):
    context.page.login(username, password)

@then('显示错误消息 "{message}"')
def step_check_error(context, message):
    assert context.page.error == message
```

### 4.2 上下文共享

```python
@given('用户 "{username}" 存在')
def step_create_user(context, username):
    if not hasattr(context, 'users'):
        context.users = {}
    context.users[username] = create_user(username)

@when('用户 "{username}" 登录')
def step_login(context, username):
    context.current_user = context.users[username]
```

### 4.3 表格参数

```gherkin
Given 以下产品存在:
  | name  | price | stock |
  | Apple | 5.0   | 100   |
  | Banana| 2.0   | 50    |
```

```python
@given('以下产品存在')
def step_products(context):
    for row in context.table:
        create_product(row['name'], row['price'], row['stock'])
```

---

## 5. 环境配置

### 5.1 environment.py

```python
from behave.api.fixture import use_fixture_by_tag

# 标签钩子
def before_feature(context, feature):
    context.fixtures = []

def after_feature(context, feature):
    cleanup_fixtures(context.fixtures)

# 标签 fixtures
@use_fixture_by_tag
def browser_fixture(context, browser):
    context.browser = Browser(browser)
    yield context.browser
    context.browser.quit()
```

### 5.2 标签使用

```gherkin
@slow
Feature: 慢速测试功能

  @browser
  Scenario: 需要 UI 测试
```

```bash
behave --tags=~slow          # 跳过慢速测试
behave --tags=browser        # 只运行 UI 测试
```

---

## 6. 运行命令

| 场景 | 命令 |
|------|------|
| 运行全部 | `behave` |
| 特定文件 | `behave features/login.feature` |
| 特定场景 | `behave --name="错误密码"` |
| 格式化输出 | `behave --format=pretty` |
| 生成报告 | `behave --format=json --outfile=report.json` |
| 并行执行 | `behave -n 4` |

---

## 7. 与 TDD 协作

### 7.1 开发流程

```
1. 编写 Feature (BDD)
   ↓
2. 实现步骤定义 → 调用应用代码
   ↓
3. 编写单元测试 (TDD) → 实现功能
   ↓
4. BDD + TDD 都通过 → 完成
```

### 7.2 示例

**Feature** (login.feature):
```gherkin
Scenario: 用户使用有效凭证登录
  Given 用户 "alice" 存在
  When 输入用户名 "alice" 和密码 "correct"
  Then 登录成功并跳转到首页
```

**步骤定义** (login_steps.py):
```python
@when('输入用户名 "{username}" 和密码 "{password}"')
def step_login(context, username, password):
    # 调用应用代码
    result = authenticate(username, password)
    context.auth_result = result
```

**单元测试** (test_auth.py):
```python
def test_authenticate_success():
    result = authenticate("alice", "correct")
    assert result.success == True
```

---

## 8. Git 提交规范

| 阶段 | 前缀 | 示例 |
|------|------|------|
| 创建 Feature | `test:` | `test: 添加登录功能场景` |
| 实现步骤 | `test:` | `test: 实现登录步骤定义` |
| 修复场景 | `fix:` | `fix: 修复登录场景断言` |

---

## 9. 常见模式

### 9.1 异常处理

```gherkin
Scenario: 登录失败
  When 用户登录
  Then 抛出 AuthenticationError
```

```python
@then('抛出 {error_name}')
def step_check_exception(context, error_name):
    with raises(getattr(exceptions, error_name)):
        context.execute()
```

### 9.2 异步步骤

```python
from异步 import async_run

@when('异步处理订单')
def step_async(context):
    context.result = async_run(process_order())
```

### 9.3 Mock 外部依赖

```python
from unittest.mock import patch

@given('支付服务可用')
def step_payment_ready(context):
    context.payment_mock = patch('services.Payment')
    context.payment_mock.start()

def after_scenario(context):
    if hasattr(context, 'payment_mock'):
        context.payment_mock.stop()
```

---

## 10. 最佳实践

| 原则 | 说明 |
|------|------|
| **业务语言** | Scenario 应该业务人员能读懂 |
| **单一职责** | 一个 Scenario 一个行为 |
| **避免实现细节** | 不描述"点击按钮"而描述"提交订单" |
| **可执行文档** | Feature 即活文档 |
| **与 TDD 配合** | BDD 做验收，TDD 做单元 |

---

**业务共识 → 可执行文档 → 自动化测试**
