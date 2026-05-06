#!/bin/bash
LOG="$HOME/.claude/notify.log"
TOPIC="claude-qy113-notify"

# 读取 stdin（只读一次）
INPUT=$(cat)
echo "$(date): hook fired" >> "$LOG"

# 取当前目录最后两级
CWD=$(basename "$(dirname "$PWD")")/$(basename "$PWD")

# 核心逻辑交给 python 处理（用临时文件避免 stdin 冲突）
PYTMP=$(mktemp /tmp/cc_notify.XXXXXX.py)
cat > "$PYTMP" << 'PYEOF'
import sys, json, re, os

raw = sys.stdin.read()
try:
    data = json.loads(raw)
except:
    data = {}

msg = data.get('last_assistant_message', '') or ''

# --- 提取最后三段作为摘要（上限 200 字）---
summary = '任务完成，等待输入'
lines = msg.split('\n')

# 提取段落（以空行分隔）
paragraphs = []
current = []
in_code = False

for line in lines:
    stripped = line.strip()
    # 跳过代码块
    if stripped.startswith('```'):
        in_code = not in_code
        if current:
            paragraphs.append('\n'.join(current))
            current = []
        continue
    if in_code:
        continue
    # 空行分隔段落
    if not stripped:
        if current:
            paragraphs.append('\n'.join(current))
            current = []
        continue
    # 跳过纯 markdown 语法行
    if re.match(r'^[\|\-\+\s]+$|^[\-\*]\s*$', stripped):
        continue
    current.append(stripped)

if current:
    paragraphs.append('\n'.join(current))

# 取最后三段
if paragraphs:
    summary = ' '.join(paragraphs[-3:])[:200]

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
rm -f "$PYTMP"

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

# ntfy.sh 推送
curl -s -o /dev/null \
  -H "Title: $TITLE" \
  -H "Tags: $TAGS" \
  -H "Priority: $PRIORITY" \
  -d "$MSG" \
  "https://ntfy.sh/$TOPIC" 2>/dev/null &

# 终端 BEL
printf '\a' 2>/dev/null
