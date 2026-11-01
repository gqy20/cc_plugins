#!/bin/bash
# Hook: 检查 PDF 文件更新
# 在每次用户输入前检查 01_articles/ 目录是否有需要处理的 PDF 文件
# 检查逻辑：PDF 存在 + 配套文件(MD/摘要)不存在 = 需要处理
#
# 自动处理配置：
#   export PDF_AUTO_PROCESS=true   # 启用自动处理（检测到新文件后自动处理）
#   export PDF_AUTO_SUMMARY=true   # 自动生成摘要（需要 Claude API）
#   export PDF_BACKGROUND=true    # 后台处理（不阻塞用户输入）

set -e

# 加载共享库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# 初始化
init_colors
CYAN='\033[0;36m'
DIM='\033[2m'
check_jq || exit 0

# 配置
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PDF_DIR="$PROJECT_ROOT/01_articles"
PROCESSED_DIR="$PROJECT_ROOT/01_articles/processed"
MD_DIR="$PROCESSED_DIR/md"
SUMMARY_DIR="$PROCESSED_DIR/summaries"
ALERT_FILE="$PROJECT_ROOT/.info/.pdf_alert"

# 自动处理配置
# 优先读取环境变量，其次读取配置文件
CONFIG_FILE="$PROJECT_ROOT/.info/.pdf_auto_config"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

PDF_AUTO_PROCESS="${PDF_AUTO_PROCESS:-false}"
PDF_BACKGROUND="${PDF_BACKGROUND:-true}"

# 1. 检查配套文件是否存在
check_supporting_files() {
    local pdf_name="$1"
    local pdf_stem="${pdf_name%.pdf}"
    local md_path="$MD_DIR/${pdf_stem}.md"
    local summary_path="$SUMMARY_DIR/${pdf_stem}.json"

    local has_md=false
    local has_summary=false

    if [ -f "$md_path" ] && [ -s "$md_path" ]; then
        has_md=true
    fi

    if [ -f "$summary_path" ] && [ -s "$summary_path" ]; then
        has_summary=true
    fi

    echo "$has_md|$has_summary"
}

# 2. 获取所有 PDF 文件
get_all_pdfs() {
    if [ ! -d "$PDF_DIR" ]; then
        return
    fi

    find "$PDF_DIR" -type f -name "*.pdf" | sort
}

# 3. 检查是否有需要处理的 PDF
check_pending_pdfs() {
    local pending_pdfs=()
    local has_pending=false

    while IFS= read -r pdf_path; do
        local pdf_name="${pdf_path##*/}"
        local support_info=$(check_supporting_files "$pdf_name")
        local has_md="${support_info%%|*}"
        local has_summary="${support_info##*|}"

        # 如果 MD 文件或摘要文件不存在，则需要处理
        if [ "$has_md" = "false" ] || [ "$has_summary" = "false" ]; then
            pending_pdfs+=("$pdf_name")
            has_pending=true
        fi
    done < <(get_all_pdfs)

    if [ "$has_pending" = true ]; then
        echo "PENDING:${pending_pdfs[@]}"
    fi
}

# 4. 触发自动处理
trigger_auto_process() {
    if [ "$PDF_AUTO_PROCESS" != "true" ]; then
        return
    fi

    # 检查是否已经在运行
    if [ -f "$PROJECT_ROOT/.info/.pdf_processing.lock" ]; then
        local pid=$(cat "$PROJECT_ROOT/.info/.pdf_processing.lock" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return  # 已在运行
        fi
        rm -f "$PROJECT_ROOT/.info/.pdf_processing.lock"
    fi

    # 记录开始时间，避免重复触发
    local last_run_file="$PROJECT_ROOT/.info/.pdf_last_auto_run"
    local now=$(date +%s)
    local last_run=0

    if [ -f "$last_run_file" ]; then
        last_run=$(cat "$last_run_file")
    fi

    # 30秒内不重复触发
    if [ $((now - last_run)) -lt 30 ]; then
        return
    fi

    echo -e "${CYAN}📄 检测到待处理文件，自动启动处理...${NC}"

    # 记录开始时间
    echo "$now" > "$last_run_file"

    if [ "$PDF_BACKGROUND" = "true" ]; then
        # 后台处理
        (
            # 保存 PID
            echo $$ > "$PROJECT_ROOT/.info/.pdf_processing.lock"

            cd "$PROJECT_ROOT"
            python "$SCRIPT_DIR/../skills/pdf-processor/scripts/processor.py" 2>&1 | \
                while IFS= read -r line; do
                    echo -e "${DIM}[PDF Auto] $line${NC}"
                done

            # 清理锁文件
            rm -f "$PROJECT_ROOT/.info/.pdf_processing.lock"
        ) &
        disown

        echo -e "${DIM}  ✓ 处理已在后台启动${NC}"
    else
        # 同步处理（会阻塞用户输入）
        python "$SCRIPT_DIR/../skills/pdf-processor/scripts/processor.py"
    fi
}

# 4. 显示 PDF 处理提示
show_pdf_alert() {
    local result=$(check_pending_pdfs)

    if [ -z "$result" ]; then
        return
    fi

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📄 检测到待处理的 PDF 文件${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    local new_count=0
    local summary_count=0

    # 解析结果
    local pdf_list="${result#PENDING:}"

    for pdf_name in $pdf_list; do
        local support_info=$(check_supporting_files "$pdf_name")
        local has_md="${support_info%%|*}"
        local has_summary="${support_info##*|}"

        if [ "$has_md" = "false" ] && [ "$has_summary" = "false" ]; then
            # 全新文件
            echo -e "  ${GREEN}+${NC} 新文件: $pdf_name (未处理)"
            new_count=$((new_count + 1))
        elif [ "$has_summary" = "false" ]; then
            # 已转换 MD，待生成摘要
            echo -e "  ${YELLOW}~${NC} 待摘要: $pdf_name"
            summary_count=$((summary_count + 1))
        fi
    done

    echo ""
    echo -e "  ${DIM}待处理: $new_count | 待摘要: $summary_count${NC}"
    echo ""
    echo -e "  ${DIM}提示: 使用 /pdf-processor 处理这些文件${NC}"
    echo ""

    # 记录提示时间
    date +%s > "$ALERT_FILE"
}

# 主逻辑
if [ -d "$PDF_DIR" ]; then
    show_pdf_alert

    # 触发自动处理
    trigger_auto_process
fi

exit 0
