---
name: explore
description: 并行代码库探索
user-invocable: true
version: 0.0.1
tags: [research, exploration]
argument-hint: [topic] [parallel]
---

# 代码库快速探索

调研主题：**$1** | 并行数量：**$2（默认 5）**

---

## 执行方式

在**单个响应**中并行启动 Explore agents。

**探索规模**：$2 个 agents（默认 5）

探索维度由 Agent 根据主题 **$1** 动态分析决定：

| 主题示例 | 可能的探索维度 |
|----------|---------------|
| "API 设计" | 接口定义、错误处理、版本控制、文档、测试 |
| "性能优化" | 瓶颈分析、缓存策略、数据库查询、算法优化 |
| "插件配置" | 结构、代码、依赖、配置、文档 |
| "错误处理" | 错误类型、捕获机制、恢复策略、日志记录 |

解析参数：`$IF($2, 启动 $2 个 agents, 启动 5 个 agents)`

```
# 启动 $2 个 Explore agents，每个 agent 根据主题 $1 选择不同的探索维度
Task(subagent_type="Explore", description="维度1",
     prompt="探索 $1 的 [维度1]", model="haiku")

Task(subagent_type="Explore", description="维度2",
     prompt="探索 $1 的 [维度2]", model="haiku")

# ... 继续 $2 个 agents
```

---

## 会话管理

### 会话文件

调研结果自动保存到 `tmp/`：
- `explore-session-<timestamp>.json` - 会话元数据
- `explore-report-<timestamp>.md` - 完整调研报告

### JSON 格式

```json
{
  "session_id": "explore-20250106-143022",
  "topic": "$1",
  "timestamp": "2025-01-06T14:30:22",
  "parallel_count": "$2 或 5",
  "agents": [
    {"name": "结构", "status": "completed", "agent_id": "xxx", "duration_ms": 15000}
  ],
  "total_duration_ms": 75000,
  "report_file": "tmp/explore-report-20250106-143022.md"
}
```

### 管理命令

```bash
# 查看状态
/explore --status

# 查看报告
cat tmp/explore-report-*.md

# 清理会话
rm tmp/explore-session-*.json tmp/explore-report-*.md
find tmp/ -name "explore-*" -mtime +7 -delete
```

### 文件保存降级

如果 `tmp/` 不可写，自动降级：
1. `/tmp/` 目录
2. `$HOME/.cache/claude-code/`
3. 都失败则不保存，正常运行

---

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| **全部失败** | 输出错误信息，不生成报告 |
| **部分失败** | 标记失败维度，生成部分报告 |
| **超时** | 单个 agent 超时 5 分钟，标记为超时 |

---

## 输出模板

### 状态显示

```
🔄 Explore 会话

┌─────────────────────────────────────────┐
│  主题：$1                               │
│  并行：$2 或 5 agents                   │
│ �耗时：75 秒                             │
├─────────────────────────────────────────┤
│  ✅ 结构 (15s) - agent_id               │
│  ✅ 代码 (18s) - agent_id               │
│  ✅ 依赖 (12s) - agent_id               │
│  ✅ 配置 (14s) - agent_id               │
│  ✅ 文档 (16s) - agent_id               │
├─────────────────────────────────────────┤
│  📄 报告：tmp/explore-report-*.md      │
└─────────────────────────────────────────┘
```

### 报告格式

```markdown
## [$1] 调研报告

**会话 ID**: explore-<timestamp>
**并行数量**: $2 或 5
**生成时间**: <timestamp>

### 🏗️ 结构
[Agent 结果]

### 🔍 代码
[Agent 结果]

### 🔗 依赖
[Agent 结果]

### ⚙️ 配置
[Agent 结果]

### 📚 文档
[Agent 结果]
```

---

## 示例

```bash
/explore "插件配置"           # 默认 5 个 agents，维度自动分析
/explore "验证脚本" 10        # 10 个 agents，深入探索
/explore "错误处理" 15        # 15 个 agents，全面覆盖
```
