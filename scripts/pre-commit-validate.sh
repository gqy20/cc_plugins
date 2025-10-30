#!/bin/bash

# Claude Code Plugins 预提交验证脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_error() { echo -e "${RED}❌ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查是否需要验证
should_validate() {
    local staged_files=$(git diff --cached --name-only)
    for file in $staged_files; do
        if [[ "$file" == .claude-plugin/* || "$file" == plugins/* ]]; then
            return 0
        fi
    done
    return 1
}

# 主验证流程
main() {
    echo "🔍 验证插件配置..."

    # 检查 Claude CLI
    if ! command -v claude &> /dev/null; then
        log_error "Claude CLI 未安装"
        exit 1
    fi

    # 验证 marketplace.json
    if [ ! -f ".claude-plugin/marketplace.json" ]; then
        log_error "未找到 marketplace.json"
        exit 1
    fi

    if ! claude plugin validate .claude-plugin/marketplace.json; then
        log_error "marketplace.json 验证失败"
        exit 1
    fi

    log_success "配置验证通过"
}

# 只在有相关文件变更时执行
if should_validate; then
    main
else
    echo "⏭️  跳过验证（无插件相关变更）"
fi