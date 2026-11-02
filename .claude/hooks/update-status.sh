#!/bin/bash
# Hook: 更新系统状态摘要
# 由其他 hook 调用，更新 .info/.status.json

set -e

# 加载共享库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# 初始化
init_colors
check_jq || exit 0

# 初始化状态对象
STATUS='{}'

# 1. 读取任务信息（单次 jq 调用批量获取）
if [ -f "$TASKS_FILE" ]; then
    # 一次 jq 调用获取所有任务统计信息
    TASK_STATS=$(jq -r '{
        active_task: ((.tasks // {}) | to_entries | map(select(.value.status == "active")) | sort_by(.value.created_at // "") | reverse | .[0] // null),
        total: ((.tasks // {}) | length),
        active: ([((.tasks // {}) | to_entries[]) | select(.value.status == "active")] | length),
        completed: ([((.tasks // {}) | to_entries[]) | select(.value.status == "completed")] | length),
        proven_count: ((.proven_skills // {}) | length),
        has_proven: (((.proven_skills // {}) | length) > 0),
        top_skill: ((.proven_skills // {}) | to_entries | sort_by(.value.usage_count // -100) | reverse | .[0] // null),
        total_reuses: ([((.proven_skills // {}) | to_entries[]) | .value.usage_count // 0] | add // 0),
        active_proven: ([((.proven_skills // {}) | to_entries[]) | select((.value.usage_count // 0) > 0)] | length)
    } | [
        (.active_task // {} | .key // ""),
        (.active_task // {} | .value.name // "无"),
        (.active_task // {} | .value.steps // [] | length),
        (.active_task // {} | .value.current_step // 0),
        .total, .active, .completed, .proven_count,
        .has_proven,
        (.top_skill // {} | .key // ""),
        (.top_skill // {} | .value.usage_count // 0),
        .total_reuses, .active_proven
    ] | map(tostring) | join("\u001f")' "$TASKS_FILE" 2>/dev/null)

    if [ -n "$TASK_STATS" ]; then
        IFS=$'\x1f' read -r ACTIVE_TASK TASK_NAME STEP_COUNT COMPLETED \
            TOTAL_TASKS ACTIVE_COUNT COMPLETED_COUNT PROVEN_COUNT \
            HAS_PROVEN TOP_SKILL TOP_COUNT TOTAL_REUSES ACTIVE_PROVEN <<< "$TASK_STATS"

        if [ -n "$ACTIVE_TASK" ]; then
            STEP_COUNT="${STEP_COUNT:-0}"
            COMPLETED="${COMPLETED:-0}"
            STATUS=$(echo "$STATUS" | jq --arg id "$ACTIVE_TASK" --arg name "$TASK_NAME" \
                --argjson total "$STEP_COUNT" --argjson completed "$COMPLETED" \
                '.active_task = $id | .task_name = $name | .total_steps = $total | .completed_steps = $completed')
        fi

        STATUS=$(echo "$STATUS" | jq --argjson total "$TOTAL_TASKS" --argjson active "$ACTIVE_COUNT" \
            --argjson completed "$COMPLETED_COUNT" --argjson proven "$PROVEN_COUNT" \
            '.total_tasks = $total | .active_tasks = $active | .completed_tasks = $completed | .proven_skills_count = $proven')

        if [ "$HAS_PROVEN" = "true" ]; then
            STATUS=$(echo "$STATUS" | jq --arg top "$TOP_SKILL" --argjson topc "$TOP_COUNT" \
                --argjson total "$TOTAL_REUSES" --argjson active "$ACTIVE_PROVEN" \
                '.top_reused_skill = $top | .top_reuse_count = $topc | .total_reuses = $total | .active_proven_skills = $active')
        else
            STATUS=$(echo "$STATUS" | jq '.top_reused_skill = "" | .top_reuse_count = 0 | .total_reuses = 0 | .active_proven_skills = 0')
        fi
    fi
fi

# 2. 读取用户画像信息（单次 jq 调用）
if [ -f "$PROFILE_FILE" ]; then
    PROFILE_INFO=$(jq -r '[.basic_info.name // "", .basic_info.role // ""] | @tsv' "$PROFILE_FILE" 2>/dev/null)
    if [ -n "$PROFILE_INFO" ]; then
        IFS=$'\t' read -r USER_NAME USER_ROLE <<< "$PROFILE_INFO"
        STATUS=$(echo "$STATUS" | jq --arg name "$USER_NAME" --arg role "$USER_ROLE" \
            '.user_name = $name | .user_role = $role')
    fi
fi

# 3. 统计技能数量（独立于用户画像）
# 包括：内置技能 + u_ 技能 + p_ 技能 + k_ 技能
if [ -d "$SKILLS_DIR" ]; then
    # 统计所有包含 SKILL.md 的目录
    SKILLS_COUNT=$(find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name "SKILL.md" -exec dirname {} \; 2>/dev/null | wc -l)
else
    SKILLS_COUNT=0
fi

STATUS=$(echo "$STATUS" | jq --argjson skills "$SKILLS_COUNT" '.skills_count = $skills')

# 4. 检查画像新鲜度
PROFILE_FRESH="true"
if [ -f "$PROFILE_FILE" ] && [ -d "$INFO_DIR" ]; then
    # 获取 info/ 目录最新文件（排除 results/ 子目录）
    # 目录为空时不能直接 xargs ls（会变成 ls 当前目录，再被 set -e 打挂）
    LATEST_INFO=$(find "$INFO_DIR" -type f \( -name "*.md" -o -name "*.json" -o -name "*.pdf" -o -name "*.txt" \) \
        -not -path "*/results/*" -print0 2>/dev/null \
        | xargs -0 sh -c 'if [ "$#" -gt 0 ]; then ls -t "$@"; fi' sh 2>/dev/null | head -1)

    if [ -n "$LATEST_INFO" ]; then
        INFO_MTIME=$(get_file_mtime "$LATEST_INFO" || true)
        PROFILE_MTIME=$(get_file_mtime "$PROFILE_FILE" || true)

        if [ -n "$INFO_MTIME" ] && [ -n "$PROFILE_MTIME" ] && [ "$INFO_MTIME" -gt "$PROFILE_MTIME" ]; then
            PROFILE_FRESH="false"
        fi
    fi
fi

STATUS=$(echo "$STATUS" | jq --arg fresh "$PROFILE_FRESH" '.profile_fresh = ($fresh == "true")')

# 5. 添加时间戳
TIMESTAMP=$(get_timestamp)
STATUS=$(echo "$STATUS" | jq --arg ts "$TIMESTAMP" '.updated_at = $ts')

# 写入状态文件（状态目录可能尚未创建）
mkdir -p "$(dirname "$STATUS_FILE")"
echo "$STATUS" | jq '.' > "$STATUS_FILE"

# 调试输出（可选，取消注释可查看）
# echo -e "${BLUE}🔄 状态已更新${NC}" >&2
# jq '.' "$STATUS_FILE" >&2

exit 0
