# TRUMPTOPIA AI - Architecture Documentation

> A Trump-style US Government-inspired AI Multi-Agent System

## Table of Contents

1. [Overview](#overview)
2. [Architecture Design](#architecture-design)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [State Machine](#state-machine)
6. [API Reference](#api-reference)
7. [Deployment](#deployment)

---

## Overview

TRUMPTOPIA AI implements a **Three Branches of Government** model for AI agent coordination, inspired by the US federal government system with Trump-style satire.

### Key Features

- **Executive Branch**: President + Cabinet (task execution)
- **Legislative Branch**: Congress (review and approval)
- **Judicial Branch**: Supreme Court (dispute resolution)
- **DOGE Oversight**: Efficiency audits and waste detection
- **Truth Social**: Public decision logging

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Oval Office Dashboard                     │
│              (Web UI - Port 7892)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP API
┌───────────────────────────▼─────────────────────────────────┐
│              TrumptopiaOrchestrator                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Task      │  │   DOGE      │  │   Firing    │         │
│  │   Manager   │  │  Auditor    │  │  Mechanism  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Tariff    │  │   Truth     │  │  Scheduler  │         │
│  │ Negotiator  │  │  Social API │  │  (Auto-run) │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Executive  │   │  Legislative │   │   Judicial   │
│   Agents     │   │    Agents    │   │    Agents    │
├──────────────┤   ├──────────────┤   ├──────────────┤
│ trump_president│  │ congress_senate│  │    scotus    │
│ state_dept   │   │ congress_house │  └──────────────┘
│ treasury     │   └──────────────┘
│ defense      │
│ commerce     │
│ energy       │
│ justice      │
└──────────────┘
```

---

## Core Components

### 1. Orchestrator (`orchestrator.py`)

Central coordinator managing:
- Task lifecycle
- State transitions
- Agent assignments
- Integration between subsystems

```python
from orchestrator import TrumptopiaOrchestrator

orch = TrumptopiaOrchestrator(enable_scheduler=True)

# Create task
task = orch.create_task("Build API", "Create REST endpoint", "high")

# Transition state
orch.transition_state(task.id, AgentState.CONGRESS)
orch.approve_task(task.id)

# Check DOGE report
report = orch.get_doge_report()
```

### 2. Task Scheduler (`scheduler.py`)

Automatic task management:
- **Stall Detection**: 180s timeout
- **Auto-Retry**: Up to configured attempts
- **Escalation**: Senate → POTUS
- **Auto-Rollback**: On persistent failure

```python
scheduler = TrumptopiaScheduler(orchestrator)
scheduler.start()  # Background thread
```

### 3. DOGE Auditor (`doge_auditor.py`)

Efficiency monitoring:
- Token usage tracking
- Response time analysis
- Efficiency scoring (0-100)
- Firing recommendations

### 4. Dashboard (`dashboard/`)

Real-time web interface:
- **Kanban Board**: Task visualization
- **Monitor**: Statistics and charts
- **Congress**: Voting display
- **DOGE**: Waste reports
- **Truth Social**: Message feed

---

## Data Models

### Task Model

```python
@dataclass
class Task:
    id: str                    # TRUMP-{timestamp}-{seq}
    title: str
    description: str
    state: AgentState          # pending/congress/potus/cabinet/doing/done
    assigned_agent: Optional[str]
    
    # Audit Trail (inspired by edict)
    flow_log: List[dict]       # State transitions
    progress_log: List[dict]   # Agent reports
    todos: List[dict]          # Task breakdown
    
    # Scheduling
    _scheduler: dict           # Stall detection config
    _prev_state: Optional[str] # For resume after stop
    
    # Metadata
    created_at: str
    updated_at: str
    tokens_used: int
    cost: float
    priority: str              # critical/high/normal/low
```

### Flow Log Entry

```json
{
  "at": "2026-03-18T10:30:00",
  "from": "congress_senate",
  "to": "trump_president",
  "remark": "Bill passed, sent to POTUS"
}
```

### Progress Log Entry

```json
{
  "at": "2026-03-18T10:35:00",
  "agent": "defense",
  "text": "API 50% complete",
  "state": "doing",
  "todos": [
    {"id": "1", "title": "Design", "status": "completed"},
    {"id": "2", "title": "Code", "status": "in-progress"}
  ],
  "tokens": 1500,
  "cost": 0.015,
  "elapsed": 300
}
```

---

## State Machine

### States

| State | Description | Next States |
|-------|-------------|-------------|
| `pending` | New task | congress |
| `congress` | Legislative review | potus, scotus |
| `potus` | Presidential review | cabinet, vetoed, fired |
| `cabinet` | Executive execution | doing, doge_audit |
| `doing` | In progress | done, doge_audit |
| `doge_audit` | Efficiency check | potus, fired, cabinet |
| `scotus` | Judicial review | potus, congress |
| `done` | Completed | - |
| `vetoed` | Rejected | congress |
| `fired` | Agent terminated | - |

### State Transition Rules

```python
STATE_TRANSITIONS = {
    AgentState.PENDING: [AgentState.CONGRESS],
    AgentState.CONGRESS: [AgentState.POTUS, AgentState.SCOTUS],
    AgentState.POTUS: [AgentState.CABINET, AgentState.VETOED, AgentState.FIRED],
    # ... etc
}
```

---

## API Reference

### Dashboard API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | List all tasks |
| `/api/agents` | GET | List all agents |
| `/api/stats` | GET | System statistics |
| `/api/doge` | GET | DOGE waste report |
| `/api/posts` | GET | Truth Social feed |
| `/api/task/action` | POST | Approve/Veto task |
| `/api/agent/fire` | POST | Fire an agent |

### CLI Commands

```bash
# Update task state
python3 scripts/kanban_update.py state TRUMP-001 doing

# Add progress
python3 scripts/kanban_update.py progress TRUMP-001 "50% done" "Design:completed|Code:in-progress"

# List tasks
python3 scripts/kanban_update.py list

# Show task details
python3 scripts/kanban_update.py show TRUMP-001
```

---

## Deployment

### Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Access dashboard
open http://localhost:7892
```

### Manual

```bash
# Install dependencies
pip install -r requirements.txt

# Start dashboard and scheduler
bash scripts/run_loop.sh

# Or start separately
python3 dashboard/server.py --static &
python3 -c "from orchestrator import TrumptopiaOrchestrator; TrumptopiaOrchestrator(enable_scheduler=True)"
```

### Systemd Service

```ini
[Unit]
Description=TRUMPTOPIA AI
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/trumptopia-ai
ExecStart=/usr/bin/python3 dashboard/server.py --static
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Performance

- **Task Throughput**: ~100 tasks/minute
- **Dashboard Latency**: <50ms API responses
- **Scheduler**: 60s scan interval
- **Memory**: ~50MB base + ~1MB per task

---

## References

- [edict](https://github.com/cft0808/edict) - 三省六部架构参考
- [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial) - 角色设计参考

---

**License**: MIT - Make AI Agents Great Again! 🇺🇸
