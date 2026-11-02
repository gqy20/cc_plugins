---
paths:
  - "**/*.py"
---

# Python 规则

- 标准库优先；加依赖前先确认没有现成实现。
- 路径用 `pathlib`，不用 `os.path` 拼接。
- 公共函数写类型标注；错误不要静默吞掉。
- 脚本要能独立运行：带 `if __name__ == "__main__"` 入口。
- 非平凡逻辑留一个最小可运行检查（assert / self-check 或 `tests/`）。
