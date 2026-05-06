#!/bin/bash
# Stop Hook - 会话结束时通过 ntfy.sh 推送通知
set -euo pipefail

LOG="$HOME/.claude/notify.log"
TOPIC="claude-qy113-notify"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# --- 依赖检查 ---
for cmd in python3 curl; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "$(date) | SKIP | $cmd not found" >> "$LOG"
        exit 0
    fi
done

# --- 读取 stdin（只读一次）---
INPUT=$(cat)
echo "$(date): hook fired from $SCRIPT_DIR" >> "$LOG"

# 取当前目录最后两级
CWD=$(basename "$(dirname "$PWD")")/$(basename "$PWD")

# --- 临时文件（唯一命名，避免并发冲突）---
PYTMP=$(mktemp /tmp/cc_notify.XXXXXX.py)
RESP_TMP=$(mktemp /tmp/cc_notify_resp.XXXXXX)
HTTP_TMP=$(mktemp /tmp/cc_notify_http.XXXXXX)
ERR_TMP=$(mktemp /tmp/cc_notify_err.XXXXXX)
trap 'rm -f "$PYTMP" "$RESP_TMP" "$HTTP_TMP" "$ERR_TMP"' EXIT

# --- Python 处理逻辑 ---
cat > "$PYTMP" << 'PYEOF'
import sys, json, re, os

raw = sys.stdin.read()
try:
    data = json.loads(raw)
except:
    data = {}

msg = data.get('last_assistant_message', '') or ''

# --- 清理 markdown 语法，提取纯文本 ---
def clean_markdown(text):
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 移除行内代码
    text = re.sub(r'`[^`]*`', '', text)
    # 移除 markdown 表格行（含 | 分隔符的行）
    text = re.sub(r'^[\s]*\|.*\|[\s]*$', '', text, flags=re.MULTILINE)
    # 移除表格分隔符行
    text = re.sub(r'^[\s]*[\|\-\:\s]+$', '', text, flags=re.MULTILINE)
    # 移除标题标记
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 移除加粗/斜体标记但保留文字
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # 移除链接标记，保留文字
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # 移除图片标记
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
    # 移除引用标记
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # 移除列表标记
    text = re.sub(r'^[\s]*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    # 移除水平线
    text = re.sub(r'^[\s]*[-*_]{3,}[\s]*$', '', text, flags=re.MULTILINE)
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 清理多余空白
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# --- 提取最后三段作为摘要 ---
summary = '任务完成，等待输入'
cleaned = clean_markdown(msg)

if cleaned:
    # 按空行分段
    paragraphs = [p.strip() for p in cleaned.split('\n\n') if p.strip()]
    if paragraphs:
        raw_summary = ' '.join(paragraphs[-3:])
        # UTF-8 安全截断（200 字符上限）
        if len(raw_summary) > 200:
            raw_summary = raw_summary[:200]
            # 确保不在多字节字符中间截断
            try:
                raw_summary.encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                raw_summary = raw_summary[:196] + '...'
        summary = raw_summary

# 如果清理后为空，用原始消息的前 100 字符
if not summary or summary == '任务完成，等待输入':
    if msg:
        fallback = re.sub(r'\s+', ' ', msg)[:100]
        if fallback.strip():
            summary = fallback.strip()

# --- 判断优先级 ---
priority = 'default'
if re.search(r'[？\?]$', summary) or summary.endswith('吗') or summary.endswith('呢'):
    priority = 'high'
elif any(k in summary for k in ['错误', '失败', 'error', 'Error', 'FAILED', '异常']):
    priority = 'urgent'

# --- 计算会话时长 ---
duration = ''
try:
    transcript = data.get('transcript_path', '')
    if transcript and os.path.exists(transcript):
        with open(transcript, 'r') as f:
            first_ts = None
            last_ts = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    ts = entry.get('timestamp', '')
                    if ts and not first_ts:
                        first_ts = ts
                    if ts:
                        last_ts = ts
                except:
                    continue
        if first_ts and last_ts:
            from datetime import datetime
            for fmt in ('%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ'):
                try:
                    t1 = datetime.strptime(first_ts, fmt)
                    t2 = datetime.strptime(last_ts, fmt)
                    secs = int((t2 - t1).total_seconds())
                    if secs >= 3600:
                        duration = f'{secs//3600}h{(secs%3600)//60}m'
                    elif secs >= 60:
                        duration = f'{secs//60}m{secs%60}s'
                    else:
                        duration = f'{secs}s'
                    break
                except:
                    continue
except:
    pass

print(summary)
print(priority)
print(duration)
PYEOF

RESULT=$(echo "$INPUT" | python3 "$PYTMP")
PY_EXIT=$?

if [ $PY_EXIT -ne 0 ]; then
    echo "$(date) | ERROR | python exit code=$PY_EXIT" >> "$LOG"
    exit 1
fi

MSG=$(echo "$RESULT" | sed -n '1p')
PRIORITY=$(echo "$RESULT" | sed -n '2p')
DURATION=$(echo "$RESULT" | sed -n '3p')

MSG="${MSG:-任务完成，等待输入}"
PRIORITY="${PRIORITY:-default}"

# 构造标题
TITLE="CC($USER) [$CWD]"
[ -n "$DURATION" ] && TITLE="$TITLE ${DURATION}"

# 根据优先级选择 tag
case "$PRIORITY" in
    high)   TAGS="question";;
    urgent) TAGS="warning";;
    *)      TAGS="white_check_mark";;
esac

# 写日志
echo "$(date) | $PRIORITY | $CWD | $MSG" >> "$LOG"

# ntfy.sh 推送（带超时）
HTTP_CODE=$(curl -s --connect-timeout 5 --max-time 15 \
  -o "$RESP_TMP" -w "%{http_code}" \
  -H "Title: $TITLE" \
  -H "Tags: $TAGS" \
  -H "Priority: $PRIORITY" \
  --data-binary "$MSG" \
  "https://ntfy.sh/$TOPIC" 2>"$ERR_TMP" || echo "000")

if [ "$HTTP_CODE" != "200" ]; then
    CURL_ERR=$(cat "$ERR_TMP" 2>/dev/null)
    echo "$(date) | PUSH_FAILED | http=$HTTP_CODE err=$CURL_ERR" >> "$LOG"
else
    echo "$(date) | PUSH_OK | http=$HTTP_CODE" >> "$LOG"
fi

# 终端 BEL
printf '\a' 2>/dev/null || true
