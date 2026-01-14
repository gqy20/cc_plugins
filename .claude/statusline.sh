#!/bin/zsh

# Claude Code 状态行脚本 (zsh 版本) - 优化版
# 显示 Git 状态、上下文使用、工具调用统计、会话信息、Token 烧录率等

input=$(cat)
current_dir=$(echo "$input" | jq -r '.workspace.current_dir // empty')

# ====== 统一提取常用 JSON 字段（jq 性能优化） ======
# 一次性提取所有常用字段，避免重复调用 jq

# 1. context_window 相关（合并多个 jq 为 1 次）
context_data=$(echo "$input" | jq -r '
    .context_window.context_window_size // "0",
    .context_window.current_usage.input_tokens // "0",
    .context_window.current_usage.output_tokens // "0",
    .context_window.current_usage.cache_read_input_tokens // "0",
    .context_window.current_usage.cache_creation_input_tokens // "0"
' 2>/dev/null)
context_window_size=$(echo "$context_data" | sed -n '1p')
context_input=$(echo "$context_data" | sed -n '2p')
context_output=$(echo "$context_data" | sed -n '3p')
context_cache_read=$(echo "$context_data" | sed -n '4p')
context_cache_creation=$(echo "$context_data" | sed -n '5p')

# 如果 context_window 存在，则保留 context_usage 用于验证
context_usage=$(echo "$input" | jq -r '.context_window.current_usage // empty')

# 2. cost 相关（合并 3 个 jq 为 1 次）
cost_data=$(echo "$input" | jq -r '
    .cost.total_duration_ms // "0",
    .cost.total_lines_added // "0",
    .cost.total_lines_removed // "0"
' 2>/dev/null)
cost_total_duration_ms=$(echo "$cost_data" | sed -n '1p')
cost_lines_added=$(echo "$cost_data" | sed -n '2p')
cost_lines_removed=$(echo "$cost_data" | sed -n '3p')

# ====== JSON 字段提取完成 ======

# 颜色定义
C_GREEN=$'\e[32m'
C_RED=$'\e[31m'
C_YELLOW=$'\e[33m'
C_BLUE=$'\e[34m'
C_MAGENTA=$'\e[35m'
C_CYAN=$'\e[36m'
C_WHITE=$'\e[37m'
C_RESET=$'\e[0m'

# ====== 公共函数 ======

# 格式化字节大小为人类可读格式
format_size() {
    local size_kb=$1
    if [ "$size_kb" -ge 1048576 ]; then
        echo "$(echo "scale=1; $size_kb / 1048576" | bc 2>/dev/null)G"
    elif [ "$size_kb" -ge 1024 ]; then
        echo "$(echo "scale=1; $size_kb / 1024" | bc 2>/dev/null)M"
    else
        echo "${size_kb}K"
    fi
}

# 格式化 token 数量为 K/M/B
format_tokens() {
    local tokens=$1
    if [ "$tokens" -ge 1000000000 ]; then
        echo "$(echo "scale=1; $tokens / 1000000000" | bc)B"
    elif [ "$tokens" -ge 1000000 ]; then
        echo "$(echo "scale=1; $tokens / 1000000" | bc)M"
    elif [ "$tokens" -ge 1000 ]; then
        echo "$(echo "scale=0; $tokens / 1000" | bc)K"
    else
        echo "${tokens}"
    fi
}

# 项目统计缓存（2秒 TTL）
get_cached_project_stats() {
    local project_path=$1

    # 修复: 验证 project_path 不为空
    if [ -z "$project_path" ]; then
        return 1
    fi

    local cache_file="$HOME/.claude/project_stats_cache_${project_path}.txt"
    local cache_ttl=2  # 2秒缓存
    local current_time=$(date +%s)

    # 检查缓存
    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if [ -n "$cache_time" ] && [ $((current_time - cache_time)) -lt $cache_ttl ]; then
            cat "$cache_file"
            return 0
        fi
    fi

    # 缓存失效，重新计算
    local project_dir="$HOME/.claude/projects/${project_path}"
    if [ ! -d "$project_dir" ]; then
        return 1
    fi

    # 使用 awk 一次性统计所有数据（性能优化）
    local stats=$(awk '
    BEGIN {
        sessions=0;
        tool_uses=0;
        errors=0;
        native_tools=0;
        mcp_tools=0;
        slash_cmds=0;
        subagents=0;
    }
    {
        if (/"tool_use"/) tool_uses++;
        if (/"error"|warning|fail/) errors++;
        if (/"name":"[A-Z]/ && !/"name":"mcp__/) native_tools++;
        if (/"name":"mcp__/) mcp_tools++;
        if (/<command-name>\/[^<]+<\/command-name>/) slash_cmds++;
        if (/"subagent_type":"[^"]+"/) subagents++;
    }
    END {
        print sessions ":" tool_uses ":" errors ":" native_tools ":" mcp_tools ":" slash_cmds ":" subagents;
    }
    ' "$project_dir"/*.jsonl 2>/dev/null)

    # 统计会话数
    local agent_count=$(find "$project_dir" -name "agent-*.jsonl" 2>/dev/null | wc -l)
    local main_count=$(print -l "$project_dir"/[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*.jsonl(N) 2>/dev/null | wc -l)
    local total_sessions=$((agent_count + main_count))

    # 获取当前会话文件
    local main_session=$(print -l "$project_dir"/[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*.jsonl(N.om[1]) 2>/dev/null)
    local session_file="$main_session"
    if [ -z "$session_file" ]; then
        session_file=$(print -l "$project_dir"/agent-*.jsonl(N.om[1]) 2>/dev/null)
    fi

    # 当前会话统计
    local session_tools=0
    local session_size_kb=0
    local session_msgs=0
    if [ -n "$session_file" ]; then
        session_tools=$(grep -o '"tool_use"' "$session_file" 2>/dev/null | wc -l)
        session_size_kb=$(du -k "$session_file" 2>/dev/null | cut -f1)
        session_msgs=$(wc -l < "$session_file" 2>/dev/null || echo 0)
    fi

    # 组装缓存数据（用 | 分隔）
    local cache_data="${total_sessions}|${stats}|${session_tools}|${session_size_kb}|${session_msgs}"
    echo "$cache_data" > "$cache_file"
    echo "$cache_data"
    return 0
}

# 获取上下文窗口使用百分比
get_context_usage() {
    # 使用全局变量（已在脚本开头提取）
    if [ -z "$context_usage" ] || [ "$context_usage" = "null" ]; then
        return
    fi

    local current=$((context_input + context_cache_creation + context_cache_read))

    if [ "$context_window_size" -gt 0 ] 2>/dev/null; then
        local pct=$((current * 100 / context_window_size))
        if [ "$pct" -gt 80 ]; then
            echo "${C_RED}📊 ${pct}%%${C_RESET}"
        elif [ "$pct" -gt 50 ]; then
            echo "${C_YELLOW}📊 ${pct}%%${C_RESET}"
        else
            echo "${C_GREEN}📊 ${pct}%%${C_RESET}"
        fi
    fi
}

# 获取上下文详细统计 (输入/输出)
get_context_io() {
    # 使用全局变量（已在脚本开头提取）
    if [ -z "$context_usage" ] || [ "$context_usage" = "null" ]; then
        return
    fi

    # 使用公共函数格式化
    local input_str=$(format_tokens $context_input)
    local output_str=$(format_tokens $context_output)

    echo "${C_CYAN}↑${input_str}${C_RESET} ${C_CYAN}↓${output_str}${C_RESET}"
}

# 获取缓存命中率（新增）
get_cache_hit_rate() {
    # 使用全局变量（已在脚本开头提取）
    if [ -z "$context_usage" ] || [ "$context_usage" = "null" ]; then
        return
    fi

    # 修复: 严格验证 total_input 为有效正数，防止除以0或异常值
    if [ -z "$context_input" ] || [ "$context_input" -lt 0 ]; then
        return
    fi

    # 修复: 正确的缓存命中率计算公式
    # input_tokens 是新输入（不含缓存），cache_read_input_tokens 是从缓存读取
    # 所以总 token = input_tokens + cache_read_input_tokens
    # 缓存命中率 = cache_read / (input + cache_read)
    local total_tokens=$((context_input + context_cache_read))

    if [ "$total_tokens" -le 0 ]; then
        return
    fi

    local cache_pct=$((context_cache_read * 100 / total_tokens))

    # 根据命中率设置颜色
    local color
    if [ "$cache_pct" -gt 50 ]; then
        color="${C_GREEN}"
    elif [ "$cache_pct" -gt 20 ]; then
        color="${C_CYAN}"
    else
        color="${C_YELLOW}"
    fi
    echo "${color}💾 ${cache_pct}%%${C_RESET}"
}

# 获取会话持续时间
get_session_duration() {
    # 使用全局变量（已在脚本开头提取）
    local duration_ms="$cost_total_duration_ms"
    if [ -z "$duration_ms" ] || [ "$duration_ms" = "null" ] || [ "$duration_ms" = "0" ]; then
        return
    fi

    local duration_sec=$(echo "$duration_ms / 1000" | bc)
    local minutes=$(echo "$duration_sec / 60" | bc)
    local seconds=$(echo "$duration_sec % 60" | bc)

    if [ "$minutes" -gt 0 ]; then
        echo "${C_YELLOW}⏳ ${minutes}m${seconds}s${C_RESET}"
    else
        echo "${C_YELLOW}⏳ ${seconds}s${C_RESET}"
    fi
}

# 获取最后一次响应时间（从主会话文件读取）
get_last_response_time() {
    local project_path=$(echo "$current_dir" | sed 's/\//-/g')
    local project_dir="$HOME/.claude/projects/${project_path}"
    
    if [ ! -d "$project_dir" ]; then
        return
    fi
    
    # 优先使用主会话文件（UUID格式）
    local main_session=$(print -l "$project_dir"/[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*-[0-9a-f]*.jsonl(N.om[1]) 2>/dev/null)
    local target_file="$main_session"
    
    # 如果主会话文件不存在，回退到最新 agent 文件
    if [ -z "$target_file" ]; then
        target_file=$(print -l "$project_dir"/agent-*.jsonl(N.om[1]) 2>/dev/null)
    fi
    
    if [ -z "$target_file" ]; then
        return
    fi
    
    # 从文件末尾查找 user 和 assistant 消息
    local last_user_ts last_assistant_ts
    last_user_ts=$(tail -100 "$target_file" 2>/dev/null | jq -r 'select(.type == "user") | .timestamp' 2>/dev/null | tail -1)
    last_assistant_ts=$(tail -100 "$target_file" 2>/dev/null | jq -r 'select(.type == "assistant") | .timestamp' 2>/dev/null | tail -1)
    
    if [ -n "$last_user_ts" ] && [ -n "$last_assistant_ts" ]; then
        # 转换为 epoch 时间
        local user_epoch assistant_epoch
        user_epoch=$(date -d "${last_user_ts}" +%s 2>/dev/null)
        assistant_epoch=$(date -d "${last_assistant_ts}" +%s 2>/dev/null)
        
        if [ -n "$user_epoch" ] && [ -n "$assistant_epoch" ]; then
            # 计算响应时间（秒）
            local response_time=$((assistant_epoch - user_epoch))
            
            if [ "$response_time" -gt 0 ]; then
                # 根据时长设置颜色
                local color
                if [ "$response_time" -lt 2 ]; then
                    color="${C_GREEN}"
                elif [ "$response_time" -lt 5 ]; then
                    color="${C_YELLOW}"
                elif [ "$response_time" -lt 10 ]; then
                    color="${C_RED}"
                else
                    color="${C_RED}"  # 很慢
                fi
                
                # 格式化显示
                if [ "$response_time" -ge 60 ]; then
                    local minutes=$((response_time / 60))
                    local seconds=$((response_time % 60))
                    echo "${color}⚡ ${minutes}m${seconds}s${C_RESET}"
                else
                    # 显示整数或小数
                    if [ "$response_time" -ge 10 ]; then
                        echo "${color}⚡ ${response_time}s${C_RESET}"
                    else
                        echo "${color}⚡ $(echo "scale=1; $response_time / 1" | bc)s${C_RESET}"
                    fi
                fi
            fi
        fi
    fi
}

# 获取代码变更统计
get_code_changes() {
    # 使用全局变量（已在脚本开头提取）
    local lines_added="$cost_lines_added"
    local lines_removed="$cost_lines_removed"

    if [ "$lines_added" -gt 0 ] || [ "$lines_removed" -gt 0 ]; then
        echo "${C_GREEN}+${lines_added}${C_RESET} ${C_RED}-${lines_removed}${C_RESET}"
    fi
}

# 获取整体项目 TPM（使用缓存优化）
get_burn_rate() {
    local project_path=$(echo "$current_dir" | sed 's/\//-/g')
    local cache_file="$HOME/.claude/burn_rate_cache_${project_path}.txt"
    local cache_ttl=10  # 10秒缓存（TPM 不需要太频繁更新）
    local current_time=$(date +%s)

    # 检查缓存
    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
        if [ -n "$cache_time" ] && [ $((current_time - cache_time)) -lt $cache_ttl ]; then
            cat "$cache_file"
            return 0
        fi
    fi

    # 缓存失效，重新计算
    local project_dir="$HOME/.claude/projects/${project_path}"
    if [ ! -d "$project_dir" ]; then
        return 1
    fi

    local total_tokens=0
    local total_time=0

    # 使用 awk 一次性统计所有 token 和时间信息（性能优化）
    local agent_data=$(awk '
    BEGIN {
        total_tokens = 0;
        first_time = "";
        last_time = "";
    }
    /"output_tokens":[0-9]+/ {
        match($0, /"output_tokens":([0-9]+)/, a);
        tokens = a[1];
        total_tokens += tokens;
    }
    /.timestamp.*"([^"]+)"/ {
        ts = substr($1, RSTART, RLENGTH);
        gsub(/"/, "", ts);
        ts = substr(ts, 1, 19);
        if (first_time == "" || ts < first_time) first_time = ts;
        if (last_time == "" || ts > last_time) last_time = ts;
    }
    END {
        print total_tokens ":" first_time ":" last_time;
    }
    ' "$project_dir"/agent-*.jsonl 2>/dev/null)

    if [ -n "$agent_data" ]; then
        local tokens=$(echo "$agent_data" | cut -d: -f1)
        local first_ts=$(echo "$agent_data" | cut -d: -f2)
        local last_ts=$(echo "$agent_data" | cut -d: -f3)

        if [ -n "$tokens" ] && [ "$tokens" -gt 0 ] && [ -n "$first_ts" ] && [ -n "$last_ts" ]; then
            local first_epoch=$(date -d "${first_ts}" +%s 2>/dev/null)
            local last_epoch=$(date -d "${last_ts}" +%s 2>/dev/null)

            if [ -n "$first_epoch" ] && [ -n "$last_epoch" ]; then
                local time_diff=$((last_epoch - first_epoch))
                if [ "$time_diff" -gt 0 ]; then
                    total_tokens=$((total_tokens + tokens))
                    total_time=$((total_time + time_diff))
                fi
            fi
        fi
    fi

    # 计算整体 TPM
    if [ "$total_time" -gt 0 ]; then
        local tpm=$(( (total_tokens * 60) / total_time ))
        local result="${C_RED}🔥 ${tpm} tpm${C_RESET}"
        echo "$result" > "$cache_file"
        echo "$result"
    fi
}

# 获取项目工具统计（使用缓存优化）
get_project_tool_stats() {
    local project_path=$(echo "$current_dir" | sed 's/\//-/g')

    # 使用缓存函数获取数据
    local cached_data=$(get_cached_project_stats "$project_path")
    if [ $? -ne 0 ]; then
        return
    fi

    # 解析缓存数据
    # 格式: total_sessions|stats|session_tools|session_size_kb|session_msgs
    # stats 格式: sessions:tool_uses:errors:native_tools:mcp_tools
    local total_sessions=$(echo "$cached_data" | cut -d'|' -f1)
    local stats=$(echo "$cached_data" | cut -d'|' -f2)
    local session_tools=$(echo "$cached_data" | cut -d'|' -f3)
    local session_size_kb=$(echo "$cached_data" | cut -d'|' -f4)
    local session_msgs=$(echo "$cached_data" | cut -d'|' -f5)

    # 从 stats 中解析详细数据
    # stats 格式: sessions:tool_uses:errors:native_tools:mcp_tools:slash_cmds:subagents
    local total_tools=$(echo "$stats" | cut -d':' -f2)
    local error_count=$(echo "$stats" | cut -d':' -f3)
    local native_tools=$(echo "$stats" | cut -d':' -f4)
    local mcp_tools=$(echo "$stats" | cut -d':' -f5)
    local slash_cmds=$(echo "$stats" | cut -d':' -f6)
    local subagents=$(echo "$stats" | cut -d':' -f7)

    local result=""

    # 1. 会话数
    if [ "$total_sessions" -gt 0 ]; then
        result="${C_CYAN}📁 ${total_sessions}${C_RESET}  "
    fi

    # 2. 总工具数
    if [ "$total_tools" -gt 0 ]; then
        result+="${C_YELLOW}🔧 Σ${total_tools}${C_RESET}  "
    fi

    # 3. 当前会话工具数
    result+="${C_CYAN}🔨 now:${session_tools}${C_RESET}  "

    # 4. 当前会话文件大小（使用公共函数）
    if [ "$session_size_kb" -gt 0 ]; then
        local size_str=$(format_size $session_size_kb)
        result+="${C_BLUE}🔄 ${size_str}${C_RESET}  "
    fi

    # 5. 当前会话消息数
    if [ "$session_msgs" -gt 0 ]; then
        result+="${C_CYAN}💬 ${session_msgs}${C_RESET}  "
    fi

    # 6. 错误/警告数
    if [ "$error_count" -gt 0 ]; then
        result+="${C_RED}⚠️ ${error_count}${C_RESET}  "
    fi

    # 7. MCP 工具占比
    local total_tools_all=$((native_tools + mcp_tools))
    if [ "$total_tools_all" -gt 0 ]; then
        local mcp_pct=$((mcp_tools * 100 / total_tools_all))
        result+="${C_MAGENTA}🔗 MCP:${mcp_pct}%%${C_RESET}  "
    fi

    # 8. Slash Commands 使用次数
    if [ "$slash_cmds" -gt 0 ]; then
        result+="${C_GREEN}💬 /:${slash_cmds}${C_RESET}  "
    fi

    # 9. Subagents 调用次数
    if [ "$subagents" -gt 0 ]; then
        result+="${C_CYAN}🤖 ag:${subagents}${C_RESET}  "
    fi

    echo "$result"
}

# Git 状态信息函数
get_git_status() {
    local dir="$1"
    local git_status_info=""

    if ! git -C "$dir" rev-parse --git-dir > /dev/null 2>&1; then
        return
    fi

    local branch=$(git -C "$dir" branch --show-current 2>/dev/null)
    if [ -z "$branch" ]; then
        branch=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
    fi

    if [ -n "$branch" ]; then
        git_status_info="${C_MAGENTA}${branch}${C_RESET}"
    fi

    local unpushed=$(git -C "$dir" rev-list --count --left-right @{u}...HEAD 2>/dev/null | awk '{print $2}')
    if [ -n "$unpushed" ] && [ "$unpushed" -gt 0 ]; then
        git_status_info+=" ${C_YELLOW}↑${unpushed}${C_RESET}"
    fi

    local last_commit=$(git -C "$dir" rev-parse --short HEAD 2>/dev/null)
    if [ -n "$last_commit" ]; then
        git_status_info+=" ${C_WHITE}${last_commit}${C_RESET}"
    fi

    local porcelain=$(git -C "$dir" status --porcelain 2>/dev/null)
    if [ -n "$porcelain" ]; then
        local staged=$(echo "$porcelain" | grep "^[MADRC]" 2>/dev/null | wc -l)
        local unstaged=$(echo "$porcelain" | grep "^.M" 2>/dev/null | wc -l)
        local untracked=$(echo "$porcelain" | grep "^??" 2>/dev/null | wc -l)

        if [ "$staged" -gt 0 ]; then
            git_status_info+=" ${C_GREEN}●${staged}${C_RESET}"
        fi
        if [ "$unstaged" -gt 0 ]; then
            git_status_info+=" ${C_RED}✚${unstaged}${C_RESET}"
        fi
        if [ "$untracked" -gt 0 ]; then
            git_status_info+=" ${C_CYAN}…${untracked}${C_RESET}"
        fi
    fi

    echo "$git_status_info"
}

# 获取 GLM 配额使用情况（带缓存）
get_quota_usage() {
    local cache_file="$HOME/.claude/quota_cache.txt"
    local cache_ttl=300  # 缓存 5 分钟
    local current_time=$(date +%s)

    # 检查缓存是否存在且未过期
    if [ -f "$cache_file" ]; then
        local cache_time=$(cat "$cache_file" 2>/dev/null | cut -d'|' -f1)
        local cache_line1=$(cat "$cache_file" 2>/dev/null | cut -d'|' -f2)
        if [ -n "$cache_time" ] && [ $((current_time - cache_time)) -lt $cache_ttl ]; then
            # 只返回第一行的简洁版
            echo "$cache_line1"
            return
        fi
    fi

    # 从环境变量获取认证信息
    local base_url="${ANTHROPIC_BASE_URL:-}"
    local auth_token="${ANTHROPIC_AUTH_TOKEN:-}"

    if [ -z "$auth_token" ] || [ -z "$base_url" ]; then
        return
    fi

    # 提取基础域名
    local base_domain=$(echo "$base_url" | sed -E 's|^(https?://[^/]*).*$|\1|')

    # 获取配额信息
    local quota_response=$(curl -s -H "Authorization: ${auth_token}" \
        -H "Content-Type: application/json" \
        "${base_domain}/api/monitor/usage/quota/limit" 2>/dev/null)

    if [ -z "$quota_response" ]; then
        return
    fi

    # 解析 TOKENS_LIMIT 数据（合并 3 次 jq 为 1 次）
    # 使用 | 作为分隔符（注意：jq 输出中不能包含 |）
    local quota_data=$(echo "$quota_response" | jq -r '.data.limits[]? | select(.type=="TOKENS_LIMIT") | "\(.percentage)|\(.remaining)|\(.nextResetTime)" // empty' 2>/dev/null)
    local percentage=$(echo "$quota_data" | cut -d'|' -f1)
    local remaining=$(echo "$quota_data" | cut -d'|' -f2)
    local reset_time_ms=$(echo "$quota_data" | cut -d'|' -f3)

    if [ -z "$percentage" ]; then
        return
    fi

    # 格式化剩余 token 数量（使用 1000 进制，LLM 行业标准）
    local remaining_str
    if [ "$remaining" -ge 1000000000 ]; then
        remaining_str="$(echo "scale=1; $remaining / 1000000000" | bc)B"
    elif [ "$remaining" -ge 1000000 ]; then
        remaining_str="$(echo "scale=1; $remaining / 1000000" | bc)M"
    elif [ "$remaining" -ge 1000 ]; then
        remaining_str="$(echo "scale=0; $remaining / 1000" | bc)K"
    else
        remaining_str="${remaining}"
    fi

    # 获取过去一小时的用量
    local hour_ago=$(date -d '1 hour ago' '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    local now=$(date '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    local hourly_response=$(curl -s -G "${base_domain}/api/monitor/usage/model-usage" \
        --data-urlencode "startTime=${hour_ago}" \
        --data-urlencode "endTime=${now}" \
        -H "Authorization: ${auth_token}" \
        -H "Content-Type: application/json" 2>/dev/null)

    # 解析小时用量数据（合并 2 次 jq 为 1 次）
    # 使用 | 作为分隔符
    local hourly_data=$(echo "$hourly_response" | jq -r '"\(.data.totalUsage.totalTokensUsage // 0)|\(.data.totalUsage.totalModelCallCount // 0)"' 2>/dev/null)
    local hourly_tokens=$(echo "$hourly_data" | cut -d'|' -f1)
    local hourly_calls=$(echo "$hourly_data" | cut -d'|' -f2)

    # 获取今日总量
    local today_start=$(date -d 'today 00:00:00' '+%Y-%m-%d %H:%M:%S' 2>/dev/null)
    local today_response=$(curl -s -G "${base_domain}/api/monitor/usage/model-usage" \
        --data-urlencode "startTime=${today_start}" \
        --data-urlencode "endTime=${now}" \
        -H "Authorization: ${auth_token}" \
        -H "Content-Type: application/json" 2>/dev/null)

    # 解析今日用量数据（合并 2 次 jq 为 1 次）
    # 使用 | 作为分隔符
    local today_data=$(echo "$today_response" | jq -r '"\(.data.totalUsage.totalTokensUsage // 0)|\(.data.totalUsage.totalModelCallCount // 0)"' 2>/dev/null)
    local today_tokens=$(echo "$today_data" | cut -d'|' -f1)
    local today_calls=$(echo "$today_data" | cut -d'|' -f2)

    # 格式化小时用量
    local hourly_str
    if [ "$hourly_tokens" -ge 1000000 ]; then
        hourly_str="$(echo "scale=1; $hourly_tokens / 1000000" | bc)M"
    elif [ "$hourly_tokens" -ge 1000 ]; then
        hourly_str="$(echo "scale=0; $hourly_tokens / 1000" | bc)K"
    else
        hourly_str="${hourly_tokens}"
    fi

    # 格式化今日用量
    local today_str
    if [ "$today_tokens" -ge 1000000 ]; then
        today_str="$(echo "scale=1; $today_tokens / 1000000" | bc)M"
    elif [ "$today_tokens" -ge 1000 ]; then
        today_str="$(echo "scale=0; $today_tokens / 1000" | bc)K"
    else
        today_str="${today_tokens}"
    fi

    # 计算重置时间倒计时
    local reset_countdown=""
    if [ -n "$reset_time_ms" ] && [ "$reset_time_ms" != "null" ]; then
        local reset_time_sec=$((reset_time_ms / 1000))
        local time_left=$((reset_time_sec - current_time))

        if [ "$time_left" -gt 0 ]; then
            if [ "$time_left" -ge 3600 ]; then
                local hours=$((time_left / 3600))
                local minutes=$(((time_left % 3600) / 60))
                reset_countdown="${hours}h${minutes}m"
            elif [ "$time_left" -ge 60 ]; then
                local minutes=$((time_left / 60))
                reset_countdown="${minutes}m"
            else
                reset_countdown="${time_left}s"
            fi
        fi
    fi

    # 根据百分比设置颜色
    local color
    if [ "$percentage" -gt 80 ]; then
        color="${C_RED}"
    elif [ "$percentage" -gt 50 ]; then
        color="${C_YELLOW}"
    else
        color="${C_GREEN}"
    fi

    # 第一行：简洁配额信息 💎 3% (774M)
    local result_line1="${color}💎 ${percentage}%% (${remaining_str})${C_RESET}"

    # 保存完整数据到缓存（包含所有详细信息）
    local full_data="${current_time}|${result_line1}|${hourly_str}|${hourly_calls}|${today_str}|${today_calls}|${reset_countdown}"
    echo "${full_data}" > "$cache_file"

    # 输出简洁版（第一行用）
    echo "$result_line1"
}

# 获取配额详细信息（第二行用）
get_quota_detail() {
    local cache_file="$HOME/.claude/quota_cache.txt"

    # 从缓存读取详细信息
    if [ -f "$cache_file" ]; then
        # 使用 awk 稳定解析（zsh 数组从 1 开始，且 ANSI 颜色码可能干扰）
        local hourly_str=$(awk -F'|' '{print $3}' "$cache_file" 2>/dev/null)
        local hourly_calls=$(awk -F'|' '{print $4}' "$cache_file" 2>/dev/null)
        local today_str=$(awk -F'|' '{print $5}' "$cache_file" 2>/dev/null)
        local today_calls=$(awk -F'|' '{print $6}' "$cache_file" 2>/dev/null)
        local reset_countdown=$(awk -F'|' '{print $7}' "$cache_file" 2>/dev/null)

        if [ -n "$hourly_str" ] && [ "$hourly_str" != "" ]; then
            local detail="${C_CYAN}1h:${hourly_str}(${hourly_calls} calls)${C_RESET} "
            detail+="${C_YELLOW}today:${today_str}(${today_calls} calls)${C_RESET}"
            if [ -n "$reset_countdown" ] && [ "$reset_countdown" != "" ]; then
                detail+="${C_WHITE} ↺${reset_countdown}${C_RESET}"
            fi
            echo "$detail"
        fi
    fi
}

# 智能压缩模式：根据终端宽度调整显示
get_display_content() {
    local term_width=${COLUMNS:-$(tput cols 2>/dev/null || echo 80)}

    # 获取各模块数据
    context_io=$(get_context_io)
    cache_rate=$(get_cache_hit_rate)  # 新增缓存命中率
    session_duration=$(get_session_duration)
    last_response=$(get_last_response_time)
    code_changes=$(get_code_changes)
    burn_rate=$(get_burn_rate)
    quota_usage=$(get_quota_usage)
    quota_detail=$(get_quota_detail)
    context_info=$(get_context_usage)
    project_stats=$(get_project_tool_stats)
    git_info=$(get_git_status "$current_dir")

    local dir_name="${current_dir:t}"
    local user="%n"
    local host="%m"
    local time_info="${C_CYAN}%D{%H:%M}${C_RESET}"

    # 极简模式（宽度 < 80）
    if [ "$term_width" -lt 80 ]; then
        # 只显示最关键信息
        print -P "%F{green}${user}%f@%F{green}${host}%f ${time_info} ${context_info} ${quota_usage} ${cache_rate}"
        return
    fi

    # 紧凑模式（宽度 80-120）
    if [ "$term_width" -lt 120 ]; then
        # 合并部分信息，简化显示
        local basic_info="${user}@${host} ${time_info}"
        local key_info="${context_info} ${quota_usage} ${cache_rate}"  # 添加缓存率
        local status_info="${git_info:+${git_info} }${last_response} ${code_changes:+${code_changes} }${session_duration}"
        local detail_info="${burn_rate} ${quota_detail:+${quota_detail}}"

        print -P "%F{green}${basic_info}%f   %F{blue}${dir_name}%f   ${key_info}"
        print -P "  ${status_info}  ${detail_info}"
        return
    fi

    # 完整模式（宽度 >= 120）
    print -P "%F{green}${user}%f@%F{green}${host}%f   ${time_info}   %F{blue}${dir_name}%f   ${git_info}     ${context_info}  ${quota_usage}  ${cache_rate}  ${last_response}  ${code_changes}  ${context_io}  ${session_duration}"
    print -P "  ${project_stats}  ${burn_rate}  ${quota_detail}"
}

# 执行显示
get_display_content
