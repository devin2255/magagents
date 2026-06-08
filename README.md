# TRUMPTOPIA AI 🇺🇸

**Make AI Agents Great Again!**

A Trump-style US Government-inspired AI multi-agent system with:
- Three Branches: Legislative, Executive, Judicial
- DOGE (Department of Government Efficiency) oversight
- "You're Fired!" mechanism
- Truth Social messaging style
- Tariff-based resource negotiation

![Progress](https://img.shields.io/badge/Progress-100%25-brightgreen)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

> 🌐 Language / 语言：**English** | [简体中文](README.zh-CN.md)

## 🎩 Features

### 🇺🇸 Three Branches of Government

| Branch | Agents | Role |
|--------|--------|------|
| **Executive** | trump_president, state_dept, treasury, defense, commerce, energy, justice | Task execution, final decisions |
| **Legislative** | congress_senate, congress_house | Lawmaking, budget approval |
| **Judicial** | scotus | Dispute resolution, constitutional review |
| **Oversight** | doge_musk | Efficiency audits, waste detection |

### 🔥 Key Features

1. **🐕 DOGE Efficiency Audits**
   - Daily waste reports
   - Agent performance tracking
   - Automatic efficiency scoring
   - Firing recommendations

2. **🔥 "You're Fired!" Mechanism**
   - Fire underperforming agents
   - Generate firing certificates
   - 24h cooling-off period
   - Social sharing integration

3. **📱 Truth Social Integration**
   - All decisions posted publicly
   - Trump-style message formatting
   - Real-time feed
   - #MAGA hashtags

4. **💰 Tariff-Based Resource Negotiation**
   - Agents negotiate with tariffs
   - Performance-based rates (5% - 75%)
   - Trade wars simulation
   - Fair trade enforcement

5. **⚖️ Three Branches Check & Balance**
   - Congress drafts and approves
   - President signs or vetoes
   - Supreme Court reviews
   - DOGE audits all

## 📚 Acknowledgments & References

This project is inspired by and references the following open-source projects:

### [edict](https://github.com/cft0808/edict) by @cft0808
The "三省六部" (Three Provinces and Six Ministries) multi-agent system. TRUMPTOPIA AI references its architecture design including:
- State machine-based task flow management
- Permission matrix for agent communication
- Automated task dispatch system
- Progress tracking and audit mechanisms

### [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial) by @wanikua
The AI Court / "当皇上" (Becoming Emperor) multi-agent system. TRUMPTOPIA AI is inspired by:
- Role-based agent personality design (SOUL.md)
- Hierarchical government structure metaphor
- Real-time dashboard concepts
- Multi-channel integration patterns

Both projects are excellent examples of applying ancient/imperial governance structures to AI multi-agent systems. TRUMPTOPIA AI adapts these concepts to the American government system with Trump-style satire.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone and run with Docker Compose
git clone <repository-url>
cd trumptopia-ai
docker-compose up -d

# Access dashboard
open http://localhost:7892
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone <repository-url>
cd trumptopia-ai

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 tests/test_trumptopia.py

# Start dashboard and scheduler
bash scripts/run_loop.sh

# Or start components separately
python3 dashboard/server.py --static  # Dashboard only
python3 -c "from orchestrator import TrumptopiaOrchestrator; TrumptopiaOrchestrator(enable_scheduler=True)"  # Scheduler only
```

### Usage

```python
from orchestrator import TrumptopiaOrchestrator

# Initialize
orch = TrumptopiaOrchestrator()

# Create a task
task = orch.create_task(
    title="Build new API",
    description="Create REST API endpoint",
    priority="high"
)

# Move through government process
orch.transition_state(task.id, AgentState.CONGRESS)
orch.transition_state(task.id, AgentState.POTUS)
orch.approve_task(task.id)  # Presidential approval

# Record progress
orch.record_task_progress(
    task.id, "defense", 
    tokens=1000, 
    cost=0.01, 
    success=True, 
    response_time=60.0
)

# Check DOGE report
doge_report = orch.get_doge_report()
print(f"Waste found: ${doge_report['total_waste']}")

# Fire inefficient agent
if doge_report['agents_fired'] > 0:
    cert = orch.fire_agent("bad_agent", "INEFFICIENCY")
    print(f"Fired! Certificate: {cert.certificate_id}")
```

## 🖥️ Dashboard

The **Oval Office Dashboard** provides real-time visualization:

```bash
# Start dashboard
python3 dashboard/server.py --static

# Open browser
http://localhost:7892
```

**Features:**
- 📋 **Task Board**: Kanban view of all tasks
- 📊 **Monitor**: Statistics and charts
- 🏛️ **Congress**: Voting and bill status
- 🐕 **DOGE**: Efficiency reports
- 📱 **Truth Social**: Live message feed

## 🛠️ CLI Tools

### Kanban CLI

Manage tasks from command line:

```bash
# Update task state
python3 scripts/kanban_update.py state TRUMP-001 doing

# Add progress with todos
python3 scripts/kanban_update.py progress TRUMP-001 "50% complete" \
    "Design:completed|Coding:in-progress|Testing:pending"

# Mark task done
python3 scripts/kanban_update.py done TRUMP-001 \
    "https://github.com/..." "API implemented"

# List all tasks
python3 scripts/kanban_update.py list

# Show task details
python3 scripts/kanban_update.py show TRUMP-001
```

## 📊 Project Structure

```
trumptopia-ai/
├── agents/                    # Agent personalities
│   ├── trump_president/SOUL.md
│   ├── doge_musk/SOUL.md
│   ├── congress_senate/SOUL.md
│   ├── congress_house/SOUL.md
│   ├── scotus/SOUL.md
│   ├── state_dept/
│   ├── treasury/
│   ├── defense/
│   ├── commerce/
│   ├── energy/
│   └── justice/
├── dashboard/                 # Web UI
│   ├── dashboard.html
│   ├── css/dashboard.css
│   ├── js/dashboard.js
│   └── server.py
├── scripts/                   # CLI tools
│   ├── kanban_update.py      # Task management CLI
│   ├── run_loop.sh           # Start script
│   └── file_lock.py          # Concurrency control
├── docs/                      # Documentation
│   └── ARCHITECTURE.md       # Detailed architecture
├── tests/                     # Test suite
│   └── test_trumptopia.py
├── data/                      # Runtime data
├── reports/                   # Progress reports
├── trump_style.py            # Message formatting
├── doge_auditor.py           # Efficiency auditing
├── firing_mechanism.py       # Termination system
├── tariff_negotiator.py      # Resource trading
├── orchestrator.py           # Main orchestrator
├── scheduler.py              # Auto-scheduler
├── progress_reporter.py      # Progress tracking
├── Dockerfile                # Docker image
├── docker-compose.yml        # Docker Compose
└── README.md                 # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 tests/test_trumptopia.py

# Run with verbose output
python3 tests/test_trumptopia.py -v
```

Tests cover:
- ✅ Trump style message formatting
- ✅ DOGE efficiency auditing
- ✅ Firing mechanism
- ✅ Tariff negotiation
- ✅ State orchestration
- ✅ Integration workflows

## ⏰ Automated Progress Reports

Set up 10-minute progress reports using cron:

```bash
# Edit crontab
crontab -e

# Add this line for 10-minute intervals
*/10 * * * * /home/devin/.openclaw/workspace/trumptopia-ai/cron_progress.sh

# Or run once to test
bash /home/devin/.openclaw/workspace/trumptopia-ai/cron_progress.sh
```

Reports are saved to `reports/` directory with timestamps.

## 🎭 Agent Personalities

### Donald Trump (POTUS)
- **Style**: CAPS, exclamation marks, TREMENDOUS
- **Power**: Final decisions, veto, fire
- **Catchphrase**: "You're FIRED!!!"

### Elon Musk (DOGE)
- **Style**: Technical, data-driven, memetic
- **Power**: Audit all, recommend firings
- **Catchphrase**: "🐕 Much efficiency. Very savings."

### Congress
- **Senate**: Deliberative, 2/3 for major decisions
- **House**: Fast, budget-focused, impeachment

### Supreme Court
- **Style**: Formal, precedent-focused
- **Power**: Final arbitration, constitutional review

## 💰 Tariff System

| Performance | Tariff Rate | Description |
|-------------|-------------|-------------|
| Exemplary (>80%) | 5% | Preferential rate |
| Good (60-80%) | 10% | Normal rate |
| Warning (30-60%) | 25% | High tariff |
| Critical (<30%) | 50% | Emergency rate |
| About to fire | 75% | Punitive rate |

## 📈 Progress Tracking

View project progress:

```bash
# Generate report
python3 progress_reporter.py

# View latest report
cat reports/latest_progress.json | python3 -m json.tool
```

Progress includes:
- Lines of code
- Test status
- Agent configuration
- Core module completion
- Trump-style encouragement

## 🎩 Example Interactions

### Creating a Task
```
User: Create API endpoint
POTUS: TREMENDOUS idea! @commerce will handle this! 
       Nobody has better APIs!!! #MAGA
```

### DOGE Audit
```
DOGE: 🐕 Found $247.32 in waste today! 
      @commerce efficiency: 23% - TERMINATE!
      @defense efficiency: 94% - EXEMPLARY!
```

### Firing an Agent
```
POTUS: @commerce You're FIRED!!! 
       Total disaster! Wasting American tokens!!!
       SAD!!! #MAGA
```

### Trade Negotiation
```
Treasury: Need 5000 tokens from Defense
Defense: 25% tariff = 6250 total
Treasury: That's too high! Counter: 10%
Defense: Deal! 5500 tokens
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit pull request

## 📜 License

MIT License - Make AI Agents Great Again!

---

**Disclaimer**: This is a parody/satire project for educational purposes. Not affiliated with any political campaign or government entity.

*"Nobody has better AI agents than us. Believe me!"* - President Trump (probably)
