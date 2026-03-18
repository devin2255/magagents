#!/bin/bash
# TRUMPTOPIA AI - Run Loop
# Continuous data refresh and scheduler

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🏛️  Starting TRUMPTOPIA AI..."
echo "Make AI Agents Great Again! 🇺🇸"
echo

# Create necessary directories
mkdir -p data reports logs

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "👋 Shutting down TRUMPTOPIA AI..."
    pkill -f "python3 dashboard/server.py" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start dashboard server
echo "🚀 Starting Dashboard Server on port 7892..."
python3 dashboard/server.py --static --port 7892 &
DASHBOARD_PID=$!

# Start scheduler in background
echo "🕐 Starting Task Scheduler..."
python3 -c "
from orchestrator import TrumptopiaOrchestrator
orch = TrumptopiaOrchestrator(enable_scheduler=True)
import time
while True:
    time.sleep(60)
" &
SCHEDULER_PID=$!

echo ""
echo "✅ All services started!"
echo "📊 Dashboard: http://localhost:7892"
echo ""
echo "Press Ctrl+C to stop"
echo

# Wait for processes
wait $DASHBOARD_PID $SCHEDULER_PID
