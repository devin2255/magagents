#!/bin/bash
# TRUMPTOPIA AI - Progress Report Cron Job
# Run this script every 10 minutes using cron

PROJECT_DIR="/home/devin/.openclaw/workspace/trumptopia-ai"
LOG_FILE="$PROJECT_DIR/reports/cron.log"

# Create reports directory if not exists
mkdir -p "$PROJECT_DIR/reports"

# Log start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting progress report..." >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Run progress reporter
python3 progress_reporter.py >> "$LOG_FILE" 2>&1

# Check if successful
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Report generated successfully" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Report generation failed" >> "$LOG_FILE"
fi

echo "---" >> "$LOG_FILE"
