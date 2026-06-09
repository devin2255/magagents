# MAGAgents 🇺🇸

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

## 🔄 How a Task Flows — Real Separation of Powers (12 Agents)

`run_task_agentic()` drives a task through the U.S. government modeling **genuine
checks & balances**: no single branch can push it through alone. Each step is a
**real LLM decision**.

```
User task
   │
   ▼  LEGISLATIVE — bicameral Congress (BOTH chambers must pass)
1) 🏛️ House  (congress_house)  ─ reject → 🏛️ CONGRESS FAILED (end)
2) 🏛️ Senate (congress_senate) ─ reject → 🏛️ CONGRESS FAILED (end)
   │
   ▼  EXECUTIVE — presentment
3) 🎩 President (trump_president) ─ sign → step 4
   │                              └ veto → ⚖️ Congress override vote (2/3, both chambers)
   │                                         ├ overridden → enacted anyway → step 4
   │                                         └ sustained  → ❌ VETOED (end)
   ▼  EXECUTIVE — implementation
4) 💼 Cabinet department (assigned by the President) ── produces the deliverable
   │
   ▼  JUDICIAL — judicial review
5) ⚖️ Supreme Court (scotus) ─ uphold → step 6
   │                          └ strike_down → ⚖️ STRUCK DOWN / unconstitutional (end)
   ▼  OVERSIGHT
6) 🐕 DOGE (doge_musk) ─ audit on REAL token usage ─ pass → ✅ DONE
                                                    └ fire → 🔥 FIRED (end)
```

**The checks that make it real (no branch is supreme):**
- **Bicameralism** — both the House and Senate must pass (two legislative gates).
- **Veto + override** — the President can veto, but Congress can **override with a
  2/3 supermajority of both chambers** (legislature checks the executive).
- **Judicial review** — the Supreme Court can **strike down** the enacted action as
  unconstitutional (judiciary checks both branches).
- **Oversight** — DOGE audits execution on real token usage.

**Who does the work? The President assigns one Cabinet department by task type:**

| Department | Best for |
|---|---|
| `commerce` | Writing, content, marketing, data/market analysis *(default)* |
| `treasury` | Budgets, cost/ROI, financial calculations |
| `defense` | Security, risk, attack/defense, hardening |
| `state_dept` | External comms, partnerships, API/integration |
| `energy` | Compute scheduling, performance, resource/capacity |
| `justice` | Compliance, legal/policy review, governance |

Each branch acts as a **safety gatekeeper, not a bureaucrat** — it passes by
default and only stops **harmful, illegal, or nonsensical** tasks (missing detail
is never grounds to block), so legitimate work sails through while the checks
stay real.

**Outcomes:** `DONE` · `CONGRESS_FAILED` · `VETOED` · `STRUCK_DOWN` · `FIRED` ·
`OVER_BUDGET` (DOGE halts a task before the next step if it exceeds its budget).

Every step records **real token usage** into DOGE, and the whole pipeline
**replies in your input language**.

## 📚 Acknowledgments & References

This project is inspired by and references the following open-source projects:

### [edict](https://github.com/cft0808/edict) by @cft0808
The "三省六部" (Three Provinces and Six Ministries) multi-agent system. MAGAgents references its architecture design including:
- State machine-based task flow management
- Permission matrix for agent communication
- Automated task dispatch system
- Progress tracking and audit mechanisms

### [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial) by @wanikua
The AI Court / "当皇上" (Becoming Emperor) multi-agent system. MAGAgents is inspired by:
- Role-based agent personality design (SOUL.md)
- Hierarchical government structure metaphor
- Real-time dashboard concepts
- Multi-channel integration patterns

Both projects are excellent examples of applying ancient/imperial governance structures to AI multi-agent systems. MAGAgents adapts these concepts to the American government system with Trump-style satire.

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
python3 tests/test_magagents.py

# Start dashboard and scheduler
bash scripts/run_loop.sh

# Or start components separately
python3 dashboard/server.py --static  # Dashboard only
python3 -c "from orchestrator import MAGAgentsOrchestrator; MAGAgentsOrchestrator(enable_scheduler=True)"  # Scheduler only
```

### Usage

```python
from orchestrator import MAGAgentsOrchestrator

# Initialize
orch = MAGAgentsOrchestrator()

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
│   └── test_magagents.py
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

## 🤖 Real LLM Mode (Optional, Pluggable)

By default MAGAgents runs in **offline template mode** (no AI, no keys, deterministic).
You can optionally plug in **real LLMs** — with a **different model per agent**
(e.g. Claude for the President, DeepSeek for DOGE, Qwen for Congress).

```bash
# 1. Install optional deps
pip install -r requirements-llm.txt

# 2. Configure keys (only fill what you use)
cp .env.example .env        # then edit .env
export DEEPSEEK_API_KEY=sk-...   # or load .env via python-dotenv

# 3. Run — agents now speak/decide via real models
python demo.py
```

- **Per-agent models**: edit `config/models.yaml` (`agents:` section). Any agent
  left out uses `default`.
- **Providers**: DeepSeek, OpenAI, Qwen (DashScope), Kimi, OpenRouter, local
  (Ollama/vLLM) via the OpenAI-compatible adapter; Anthropic (Claude) via its own.
- **Override per run**: `MAGAGENTS_AGENT_TRUMP_PRESIDENT_MODEL=claude-sonnet-4-5`
- **Force offline**: `MAGAGENTS_LLM_ENABLED=off`
- **Graceful degradation**: if no key is set (or deps missing), MAGAgents
  automatically falls back to template mode — `demo.py` and the test suite always work.
- Real token usage flows into the system summary (`llm_usage`) and feeds DOGE audits.

**Agentic mode** — let the agents make the *real* decisions end-to-end:

```python
orch = MAGAgentsOrchestrator()
task = orch.create_task("Draft a press release", "Keep it punchy", "high")
result = orch.run_task_agentic(task.id)
#  Congress votes -> POTUS approves/vetoes & assigns -> Cabinet executes
#  -> DOGE audits on REAL token usage -> Done / Fired
print(result["outcome"], result.get("output"))
```

Offline it auto-approves with placeholder output (fully testable); with keys it
runs genuine multi-agent decisions. See it live at the end of `python demo.py`.

- **Cost circuit-breaker**: DOGE halts a task before the next step if it blows its
  budget. Configure in `config/models.yaml` (`budget:`) or per call
  (`run_task_agentic(id, max_cost=0.02)`); env: `MAGAGENTS_MAX_COST_PER_TASK`.
- **Dashboard**: open a task in the Oval Office Dashboard to see its full decision
  trace + deliverable, or hit **▶️ Run (Agentic)** to drive it live.
- **Chat CLI**: `python chat.py` — talk to the government; each agent's decision
  streams live, the deliverable prints at the end, in your input language.
  One-shot: `python chat.py "Write a tweet about the trade deal"`.

> 🔒 API keys are read from environment variables only and never committed (`.env` is gitignored).

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python3 tests/test_magagents.py

# Run with verbose output
python3 tests/test_magagents.py -v
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
