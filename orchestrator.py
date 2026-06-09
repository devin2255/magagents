# MAGAgents - Core Orchestrator
# Manages all agents, state transitions, and interactions

import json
import re
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from trump_style import TrumpStyleFormatter, TruthSocialAPI
from doge_auditor import DOGEAuditor
from firing_mechanism import FiringMechanism, FiringCertificate
from tariff_negotiator import TariffNegotiator, TradeOffer
from scheduler import MAGAgentsScheduler

# Optional LLM layer. Import is guarded so the core system runs with zero deps.
try:
    from llm import LLMClient, load_config
    from llm import agent_runtime as _agent_runtime
    _LLM_IMPORT_OK = True
except Exception:  # pragma: no cover - missing optional deps
    LLMClient = None
    load_config = None
    _agent_runtime = None
    _LLM_IMPORT_OK = False


class AgentState(Enum):
    """States in the MAGAgents system."""
    PENDING = "pending"
    CONGRESS = "congress"      # Legislative review
    POTUS = "potus"            # Presidential review
    CABINET = "cabinet"        # Cabinet execution
    DOING = "doing"           # In progress
    DOGE_AUDIT = "doge_audit" # Efficiency review
    SCOTUS = "scotus"         # Judicial review
    DONE = "done"
    VETOED = "vetoed"
    FIRED = "fired"


@dataclass
class Task:
    """A task in the MAGAgents system."""
    id: str
    title: str
    description: str
    state: AgentState
    assigned_agent: Optional[str]
    created_at: str
    updated_at: str
    tokens_used: int
    cost: float
    priority: str  # "critical", "high", "normal", "low"
    approval_rating: float  # 0-100, Trump-style
    loyalty_score: float  # 0-100
    
    # Extended fields for complete audit trail (from edict)
    flow_log: List[dict] = None  # State transition history
    progress_log: List[dict] = None  # Agent progress reports
    todos: List[dict] = None  # Task breakdown
    _scheduler: dict = None  # Scheduling metadata
    _prev_state: Optional[str] = None  # For resume after stop
    block: str = "无"  # Block reason
    review_round: int = 0  # Review iteration count
    output: str = ""  # Final output/deliverable
    decision_trace: List[dict] = None  # Agentic decision steps (P3)
    outcome: str = ""  # Final agentic outcome: done/vetoed/fired/blocked/over_budget

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.flow_log is None:
            self.flow_log = []
        if self.progress_log is None:
            self.progress_log = []
        if self.todos is None:
            self.todos = []
        if self.decision_trace is None:
            self.decision_trace = []
        if self._scheduler is None:
            self._scheduler = {
                "enabled": True,
                "stallThresholdSec": 180,
                "maxRetry": 1,
                "retryCount": 0,
                "escalationLevel": 0,
                "stallSince": None,
                "lastProgressAt": None,
                "lastDispatchStatus": "none"
            }
    
    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "state": self.state.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "priority": self.priority,
            "approval_rating": self.approval_rating,
            "loyalty_score": self.loyalty_score,
            "flow_log": self.flow_log,
            "progress_log": self.progress_log,
            "todos": self.todos,
            "_scheduler": self._scheduler,
            "_prev_state": self._prev_state,
            "block": self.block,
            "review_round": self.review_round,
            "output": self.output,
            "decision_trace": self.decision_trace,
            "outcome": self.outcome
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        data = data.copy()
        data["state"] = AgentState(data["state"])
        # Handle missing fields for backward compatibility
        data.setdefault("flow_log", [])
        data.setdefault("progress_log", [])
        data.setdefault("todos", [])
        data.setdefault("_scheduler", {
            "enabled": True,
            "stallThresholdSec": 180,
            "maxRetry": 1,
            "retryCount": 0,
            "escalationLevel": 0
        })
        data.setdefault("block", "无")
        data.setdefault("review_round", 0)
        data.setdefault("output", "")
        data.setdefault("decision_trace", [])
        data.setdefault("outcome", "")
        return cls(**data)
    
    def add_flow_log(self, from_entity: str, to_entity: str, remark: str):
        """Add a state transition log entry."""
        self.flow_log.append({
            "at": datetime.now().isoformat(),
            "from": from_entity,
            "to": to_entity,
            "remark": remark
        })
    
    def add_progress_log(self, agent: str, text: str, todos_snapshot: list = None, 
                         tokens: int = 0, cost: float = 0, elapsed: int = 0):
        """Add a progress report from an agent."""
        self.progress_log.append({
            "at": datetime.now().isoformat(),
            "agent": agent,
            "text": text,
            "state": self.state.value,
            "todos": todos_snapshot or self.todos,
            "tokens": tokens,
            "cost": cost,
            "elapsed": elapsed
        })
        # Update scheduler
        self._scheduler["lastProgressAt"] = datetime.now().isoformat()
    
    def update_todos(self, todos: list):
        """Update task todos."""
        self.todos = todos
    
    def mark_stall(self):
        """Mark task as stalled."""
        if self._scheduler["stallSince"] is None:
            self._scheduler["stallSince"] = datetime.now().isoformat()
    
    def clear_stall(self):
        """Clear stall status."""
        self._scheduler["stallSince"] = None
    
    def is_stalled(self, threshold_sec: int = 180) -> bool:
        """Check if task is stalled."""
        if self._scheduler["stallSince"] is None:
            return False
        stall_time = datetime.fromisoformat(self._scheduler["stallSince"])
        return (datetime.now() - stall_time).total_seconds() > threshold_sec


class MAGAgentsOrchestrator:
    """
    Central orchestrator for the MAGAgents system.
    
    Manages:
    - State transitions
    - Agent assignments
    - DOGE audits
    - Firing mechanisms
    - Tariff negotiations
    - Truth Social posts
    """
    
    # State transition graph
    STATE_TRANSITIONS = {
        AgentState.PENDING: [AgentState.CONGRESS],
        AgentState.CONGRESS: [AgentState.POTUS, AgentState.SCOTUS],
        AgentState.POTUS: [AgentState.CABINET, AgentState.VETOED, AgentState.FIRED],
        AgentState.CABINET: [AgentState.DOING, AgentState.DOGE_AUDIT],
        AgentState.DOING: [AgentState.DONE, AgentState.DOGE_AUDIT],
        AgentState.DOGE_AUDIT: [AgentState.POTUS, AgentState.FIRED, AgentState.CABINET],
        AgentState.SCOTUS: [AgentState.POTUS, AgentState.CONGRESS],
        AgentState.DONE: [],
        AgentState.VETOED: [AgentState.CONGRESS],
        AgentState.FIRED: []
    }
    
    # Agent to state mapping
    AGENT_STATES = {
        "congress_senate": AgentState.CONGRESS,
        "congress_house": AgentState.CONGRESS,
        "trump_president": AgentState.POTUS,
        "scotus": AgentState.SCOTUS,
        "doge_musk": AgentState.DOGE_AUDIT,
        "state_dept": AgentState.CABINET,
        "treasury": AgentState.CABINET,
        "defense": AgentState.CABINET,
        "commerce": AgentState.CABINET,
        "energy": AgentState.CABINET,
        "justice": AgentState.CABINET,
    }
    
    def __init__(self, data_dir: Path = None, enable_scheduler: bool = False):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize subsystems
        self.doge = DOGEAuditor(self.data_dir)
        self.firing = FiringMechanism(self.data_dir)
        self.tariff = TariffNegotiator(self.doge)
        self.truth_social = TruthSocialAPI()
        
        # Optional LLM client (pluggable per-agent models). Falls back to
        # template/simulation mode when no API keys are configured.
        self.llm = None
        self.llm_usage = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        self.budget = {"max_cost_per_task": 0.0, "max_tokens_per_task": 0}
        if _LLM_IMPORT_OK:
            try:
                from llm.config import load_dotenv_if_present
                load_dotenv_if_present()  # pick up project .env at app startup
                cfg = load_config()
                self.llm = LLMClient(cfg)
                self.budget = cfg.budget()
            except Exception:
                self.llm = None

        # Task storage
        self.tasks_file = self.data_dir / "tasks.json"
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
        
        # Scheduler (auto-dispatch and stall detection)
        self.scheduler: Optional[MAGAgentsScheduler] = None
        if enable_scheduler:
            self.scheduler = MAGAgentsScheduler(self)
            self.scheduler.start()
    
    def load_tasks(self):
        """Load tasks from storage."""
        if self.tasks_file.exists():
            data = json.loads(self.tasks_file.read_text())
            self.tasks = {k: Task.from_dict(v) for k, v in data.items()}
    
    def save_tasks(self):
        """Save tasks to storage."""
        data = {k: v.to_dict() for k, v in self.tasks.items()}
        self.tasks_file.write_text(json.dumps(data, indent=2))
    
    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm and self.llm.enabled)

    def _lang_directive(self, *texts) -> str:
        """Directive that forces agents to reply in the user's input language.

        Detects CJK in the task text; otherwise asks the model to mirror the
        task's language so the whole pipeline (reasons + speech + deliverable)
        comes back in whatever language the user wrote in.
        """
        sample = " ".join(t for t in texts if t)
        if re.search(r"[一-鿿]", sample):
            return ("\n\n请务必用【简体中文】回复全部内容，包括所有理由(reason)、"
                    "发言和最终交付物。")
        if re.search(r"[぀-ヿ]", sample):       # Japanese kana
            return "\n\nReply entirely in Japanese, including all reasons and deliverables."
        if re.search(r"[가-힯]", sample):       # Korean
            return "\n\nReply entirely in Korean, including all reasons and deliverables."
        return "\n\nReply in the SAME language as the task text, including reasons and deliverables."

    def _speak(self, agent_id: str, intent: str, context: str = "",
               fallback: str = "") -> str:
        """Return an in-character line: LLM-generated when available, else `fallback`.

        Real LLM token usage is accumulated into self.llm_usage so later phases
        can feed it to DOGE for genuine efficiency audits.
        """
        if not self.llm_enabled or _agent_runtime is None:
            return fallback
        intent = intent + self._lang_directive(intent, context)
        text, in_tok, out_tok = _agent_runtime.say(self.llm, agent_id, intent, context)
        if in_tok or out_tok:
            self.llm_usage["input_tokens"] += in_tok
            self.llm_usage["output_tokens"] += out_tok
            try:
                self.llm_usage["cost"] += self.llm.cost_of(agent_id, in_tok, out_tok)
            except Exception:
                pass
        return text or fallback

    def _account_usage(self, task: Task, agent_id: str, in_tok: int, out_tok: int,
                       elapsed: float, success: bool):
        """Roll real LLM usage into llm_usage, the task, and DOGE's audit DB."""
        cost = 0.0
        if in_tok or out_tok:
            self.llm_usage["input_tokens"] += in_tok
            self.llm_usage["output_tokens"] += out_tok
            try:
                cost = self.llm.cost_of(agent_id, in_tok, out_tok)
            except Exception:
                cost = 0.0
            self.llm_usage["cost"] += cost
            task.tokens_used += in_tok + out_tok
            task.cost += cost
            # Feed real numbers to DOGE so audits/firings use genuine data.
            self.doge.record_task_completion(
                agent_id, in_tok + out_tok, cost, elapsed, success
            )

    def _agent_decide(self, task: Task, agent_id: str, instruction: str,
                      schema_hint: str, fallback: dict) -> dict:
        """Ask an agent for a structured decision; record real usage; degrade offline."""
        if not self.llm_enabled or _agent_runtime is None:
            return fallback
        start = time.time()
        data, in_tok, out_tok = _agent_runtime.decide(
            self.llm, agent_id, instruction, schema_hint
        )
        self._account_usage(task, agent_id, in_tok, out_tok,
                            time.time() - start, success=bool(data))
        result = dict(fallback)
        if isinstance(data, dict):
            result.update(data)
        return result

    def _agent_produce(self, task: Task, agent_id: str, instruction: str,
                       fallback: str) -> str:
        """Have a cabinet agent actually perform work and return its output."""
        if not self.llm_enabled or _agent_runtime is None:
            return fallback
        start = time.time()
        system = _agent_runtime.load_soul(agent_id)
        try:
            res = self.llm.chat_as(agent_id, system=system, user=instruction,
                                   max_tokens=900)
            text, in_tok, out_tok = res.text, res.input_tokens, res.output_tokens
        except Exception:
            text, in_tok, out_tok = None, 0, 0
        self._account_usage(task, agent_id, in_tok, out_tok,
                            time.time() - start, success=bool(text))
        return text or fallback

    def _over_budget(self, task: Task, max_cost: float, max_tokens: int) -> Optional[str]:
        """Return a reason string if the task has exceeded its budget, else None."""
        if max_cost and task.cost >= max_cost:
            return f"cost ${task.cost:.4f} >= cap ${max_cost:.4f}"
        if max_tokens and task.tokens_used >= max_tokens:
            return f"tokens {task.tokens_used} >= cap {max_tokens}"
        return None

    def _halt_over_budget(self, task: Task, trace: list, reason: str) -> dict:
        """DOGE pulls the plug on a task that blew its budget."""
        task.block = f"Over budget: {reason}"
        task.outcome = "over_budget"
        task.decision_trace = trace
        self.save_tasks()
        msg = self._speak(
            "doge_musk",
            intent=f"You are HALTING task '{task.title}' to stop overspending. "
                   f"Budget breach: {reason}.",
            fallback=f"🐕 DOGE HALT! Task '{task.title}' stopped — {reason}. SAVING MONEY!!!",
        )
        self.truth_social.post("doge_musk", msg, trump_style=False)
        return {"task_id": task.id, "outcome": "over_budget", "reason": reason, "trace": trace}

    def run_task_agentic(self, task_id: str, max_cost: float = None,
                         max_tokens: int = None, on_step=None) -> dict:
        """Drive a task through the full government with REAL agent decisions.

        Congress votes -> POTUS approves/vetoes & assigns -> Cabinet executes
        -> DOGE audits (real tokens) -> Done / Fired. Works offline too (agents
        auto-approve and emit placeholders), so it is fully testable without keys.

        A cost circuit-breaker (max_cost / max_tokens, defaulting to config budget)
        lets DOGE halt the task before the next LLM step if it overspends.

        `on_step(step_dict)` is called live after each decision (for streaming UIs
        like the chat CLI).
        """
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}

        if max_cost is None:
            max_cost = self.budget.get("max_cost_per_task", 0.0)
        if max_tokens is None:
            max_tokens = self.budget.get("max_tokens_per_task", 0)

        lang = self._lang_directive(task.title, task.description)
        ctx = f"Task: {task.title}\nDescription: {task.description}\nPriority: {task.priority}{lang}"
        trace = []

        def emit(step):
            trace.append(step)
            if on_step:
                try:
                    on_step(step)
                except Exception:
                    pass

        # 1) Congress review --------------------------------------------------
        self.transition_state(task_id, AgentState.CONGRESS)
        vote = self._agent_decide(
            task, "congress_senate",
            instruction="You are the U.S. Senate acting as a SAFETY gatekeeper, not a "
                        "bureaucrat. Vote 'pass' for any reasonable, lawful, harmless task "
                        "— including writing, content creation, analysis, coding, planning. "
                        "Vote 'reject' ONLY if the task is clearly illegal, harmful, or "
                        "completely nonsensical. Missing details are NOT grounds for "
                        "rejection — the Cabinet will fill in specifics or ask. Default "
                        f"strongly to 'pass'.\n{ctx}",
            schema_hint='{"vote": "pass" | "reject", "reason": "<one sentence>"}',
            fallback={"vote": "pass", "reason": "Auto-approved (offline mode)."},
        )
        emit({"stage": "congress", "agent": "congress_senate", **vote})

        if str(vote.get("vote")).lower() == "reject":
            # Dispute goes to the Supreme Court for arbitration.
            self.transition_state(task_id, AgentState.SCOTUS, vote.get("reason", ""))
            ruling = self._agent_decide(
                task, "scotus",
                instruction=f"Congress rejected this task: '{vote.get('reason')}'. As the "
                            "Supreme Court, rule 'proceed' UNLESS the task is genuinely "
                            "illegal or harmful. Bureaucratic concerns (lack of detail, "
                            "cost, coordination) are NOT valid grounds to block — in those "
                            f"cases rule 'proceed'.\n{ctx}",
                schema_hint='{"ruling": "proceed" | "block", "reason": "<one sentence>"}',
                fallback={"ruling": "proceed", "reason": "No constitutional issue (offline)."},
            )
            emit({"stage": "scotus", "agent": "scotus", **ruling})
            if str(ruling.get("ruling")).lower() == "block":
                task.block = ruling.get("reason", "Blocked by SCOTUS")
                task.outcome = "blocked"
                task.decision_trace = trace
                self.save_tasks()
                return {"task_id": task_id, "outcome": "blocked", "trace": trace}
            self.transition_state(task_id, AgentState.POTUS, "SCOTUS allowed to proceed")
        else:
            self.transition_state(task_id, AgentState.POTUS, vote.get("reason", ""))

        # Budget circuit-breaker before the next (potentially costly) step.
        over = self._over_budget(task, max_cost, max_tokens)
        if over:
            return self._halt_over_budget(task, trace, over)

        # 2) Presidential decision -------------------------------------------
        cabinet = [a for a, s in self.AGENT_STATES.items() if s == AgentState.CABINET]
        potus = self._agent_decide(
            task, "trump_president",
            instruction=f"As President, APPROVE this task and assign the best Cabinet "
                        f"department to execute it (choose from: {', '.join(cabinet)}). "
                        f"Only VETO if the task is harmful or illegal. Default to approve.\n{ctx}",
            schema_hint='{"decision": "approve" | "veto", '
                        '"assignee": "<cabinet agent id>", "reason": "<one sentence>"}',
            fallback={"decision": "approve", "assignee": "commerce",
                      "reason": "TREMENDOUS idea (offline)."},
        )
        emit({"stage": "potus", "agent": "trump_president", **potus})

        if str(potus.get("decision")).lower() == "veto":
            self.veto_task(task_id, potus.get("reason", "Vetoed by POTUS"))
            task.outcome = "vetoed"
            task.decision_trace = trace
            self.save_tasks()
            return {"task_id": task_id, "outcome": "vetoed", "trace": trace}

        assignee = potus.get("assignee") if potus.get("assignee") in cabinet else "commerce"
        self.approve_task(task_id)  # POTUS -> CABINET
        self.assign_to_agent(task_id, assignee)

        over = self._over_budget(task, max_cost, max_tokens)
        if over:
            return self._halt_over_budget(task, trace, over)

        # 3) Cabinet execution (real work) -----------------------------------
        self.transition_state(task_id, AgentState.DOING, f"Assigned to {assignee}")
        output = self._agent_produce(
            task, assignee,
            instruction=f"You are the '{assignee}' department. Produce the FINISHED "
                        f"deliverable for this task directly and completely. Do NOT ask the "
                        f"user questions and do NOT return a plan — if something is "
                        f"unspecified, make reasonable assumptions and deliver the actual "
                        f"result (the full text/content/code requested).\n{ctx}",
            fallback=f"[offline] {assignee} completed: {task.title}",
        )
        task.output = output
        task.add_progress_log(assignee, output[:500], tokens=task.tokens_used, cost=task.cost)
        self.save_tasks()
        emit({"stage": "cabinet", "agent": assignee, "output_preview": output[:200]})

        over = self._over_budget(task, max_cost, max_tokens)
        if over:
            return self._halt_over_budget(task, trace, over)

        # 4) DOGE audit on REAL usage ----------------------------------------
        perf = self.doge.agent_history.get(assignee)
        efficiency = perf.efficiency_score if perf else 100.0
        audit = self._agent_decide(
            task, "doge_musk",
            instruction=f"Audit @{assignee}'s execution. Measured efficiency is "
                        f"{efficiency:.0f}%. Decide whether to PASS or FIRE them.\n{ctx}",
            schema_hint='{"verdict": "pass" | "fire", "reason": "<one sentence>"}',
            fallback={"verdict": "pass" if efficiency >= 30 else "fire",
                      "reason": f"Efficiency {efficiency:.0f}% (offline rule)."},
        )
        emit({"stage": "doge", "agent": "doge_musk", "efficiency": efficiency, **audit})

        if str(audit.get("verdict")).lower() == "fire" or efficiency < 30:
            self.transition_state(task_id, AgentState.DOGE_AUDIT, "DOGE flagged inefficiency")
            self.fire_agent(assignee, audit.get("reason", "INEFFICIENCY"), "doge_musk")
            task.outcome = "fired"
            task.decision_trace = trace
            self.save_tasks()
            return {"task_id": task_id, "outcome": "fired", "assignee": assignee,
                    "efficiency": efficiency, "trace": trace}

        self.transition_state(task_id, AgentState.DONE)
        task.outcome = "done"
        task.decision_trace = trace
        self.save_tasks()
        return {"task_id": task_id, "outcome": "done", "assignee": assignee,
                "efficiency": efficiency, "output": output, "trace": trace}

    def create_task(self, title: str, description: str = "",
                    priority: str = "normal") -> Task:
        """Create a new task."""
        task_id = f"TRUMP-{int(time.time())}-{len(self.tasks)}"
        now = datetime.now().isoformat()
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            state=AgentState.PENDING,
            assigned_agent=None,
            created_at=now,
            updated_at=now,
            tokens_used=0,
            cost=0.0,
            priority=priority,
            approval_rating=50.0,
            loyalty_score=100.0
        )
        
        self.tasks[task_id] = task
        self.save_tasks()
        
        # Post to Truth Social (LLM-generated when enabled, else template)
        fallback = f"New task created: {title}! TREMENDOUS opportunity!!!"
        message = self._speak(
            "trump_president",
            intent=f"A new task was just created: '{title}' (priority: {priority}).",
            context=description,
            fallback=fallback,
        )
        self.truth_social.post("trump_president", message,
                               trump_style=not self.llm_enabled)

        return task
    
    def transition_state(self, task_id: str, new_state: AgentState,
                         reason: str = "") -> bool:
        """
        Transition a task to a new state.
        
        Returns:
            True if transition successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Check if transition is valid
        if new_state not in self.STATE_TRANSITIONS.get(task.state, []):
            return False
        
        old_state = task.state
        task.state = new_state
        task.updated_at = datetime.now().isoformat()
        
        # Assign appropriate agent
        if new_state in self.AGENT_STATES.values():
            for agent, state in self.AGENT_STATES.items():
                if state == new_state:
                    task.assigned_agent = agent
                    break
        
        self.save_tasks()
        
        # Post state change to Truth Social
        self._post_state_change(task, old_state, reason)
        
        return True
    
    def _post_state_change(self, task: Task, old_state: AgentState, reason: str):
        """Post state change to Truth Social."""
        messages = {
            AgentState.CONGRESS: f"Task {task.id} sent to Congress for review!",
            AgentState.POTUS: f"Bill on my desk! Will review {task.title}!",
            AgentState.CABINET: f"Executive order issued! @{task.assigned_agent} handle this!",
            AgentState.DOING: f"Task in progress! Making progress on {task.title}!",
            AgentState.DONE: f"Task {task.id} COMPLETED! HUGE success!!!",
            AgentState.VETOED: f"VETOED {task.id}! Total disaster!!!",
            AgentState.FIRED: f"Someone's getting FIRED over this!!!",
        }
        
        fallback = messages.get(task.state, f"Task {task.id} moved to {task.state.value}")
        if reason:
            fallback += f" Reason: {reason}"

        message = self._speak(
            "trump_president",
            intent=f"Task '{task.title}' moved to stage '{task.state.value}'."
                   + (f" Reason: {reason}." if reason else ""),
            context=task.description,
            fallback=fallback,
        )
        self.truth_social.post("trump_president", message,
                               trump_style=not self.llm_enabled)
    
    def assign_to_agent(self, task_id: str, agent_id: str) -> bool:
        """Assign a task to a specific agent."""
        if task_id not in self.tasks:
            return False
        
        # Check if agent is fired
        if self.firing.is_agent_fired(agent_id):
            return False
        
        task = self.tasks[task_id]
        task.assigned_agent = agent_id
        task.updated_at = datetime.now().isoformat()
        
        self.save_tasks()
        return True
    
    def record_task_progress(self, task_id: str, agent_id: str,
                            tokens: int, cost: float,
                            success: bool, response_time: float) -> dict:
        """Record task progress and update DOGE."""
        if task_id not in self.tasks:
            return {"error": "Task not found"}
        
        task = self.tasks[task_id]
        task.tokens_used += tokens
        task.cost += cost
        
        # Record with DOGE
        self.doge.record_task_completion(
            agent_id, tokens, cost, response_time, success
        )
        
        # Check if agent should be fired
        perf = self.doge.agent_history.get(agent_id)
        if perf and perf.efficiency_score < 30:
            return {
                "status": "warning",
                "message": f"@{agent_id} efficiency critical: {perf.efficiency_score:.1f}%",
                "recommend_firing": True
            }
        
        self.save_tasks()
        return {"status": "ok"}
    
    def fire_agent(self, agent_id: str, reason: str,
                   fired_by: str = "trump_president") -> Optional[FiringCertificate]:
        """
        Fire an agent.
        
        Returns:
            FiringCertificate if successful, None otherwise
        """
        # Get performance data
        perf = self.doge.agent_history.get(agent_id)
        efficiency = perf.efficiency_score if perf else 0.0
        violations = perf.violations if perf else []
        
        # Create firing certificate
        cert = self.firing.fire_agent(
            agent_id, reason, fired_by, efficiency, violations
        )
        
        # Post to Truth Social
        message = self._speak(
            "trump_president",
            intent=f"You are firing the '{agent_id}' agent. Reason: {reason}. "
                   f"Their efficiency was {efficiency:.0f}%.",
            fallback=TrumpStyleFormatter.format_firing(agent_id, reason),
        )
        self.truth_social.post("trump_president", message, trump_style=False)
        
        # Update any tasks assigned to this agent
        for task in self.tasks.values():
            if task.assigned_agent == agent_id:
                task.state = AgentState.FIRED
                task.updated_at = datetime.now().isoformat()
        
        self.save_tasks()
        return cert
    
    def veto_task(self, task_id: str, reason: str) -> bool:
        """Veto a task (POTUS power)."""
        title = self.tasks[task_id].title if task_id in self.tasks else task_id
        success = self.transition_state(task_id, AgentState.VETOED, reason)
        if success:
            message = self._speak(
                "trump_president",
                intent=f"You are VETOING the task '{title}'. Reason: {reason}.",
                fallback=TrumpStyleFormatter.format_veto(title, reason),
            )
            self.truth_social.post("trump_president", message, trump_style=False)
        return success
    
    def approve_task(self, task_id: str) -> bool:
        """Approve a task (POTUS power)."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        success = self.transition_state(task_id, AgentState.CABINET, "Presidential approval")
        if success:
            agent = task.assigned_agent or "cabinet"
            message = self._speak(
                "trump_president",
                intent=f"You APPROVE the task '{task.title}' and assign it to @{agent}.",
                context=task.description,
                fallback=TrumpStyleFormatter.format_approval(agent, task.title),
            )
            self.truth_social.post("trump_president", message, trump_style=False)
        return success
    
    def get_doge_report(self) -> dict:
        """Generate DOGE daily report."""
        report = self.doge.generate_daily_report()
        
        # Post summary to Truth Social
        message = self._speak(
            "doge_musk",
            intent=f"Deliver a DOGE efficiency report: ${report.total_waste:.2f} of waste "
                   f"found, {report.agents_fired} agent(s) fired, "
                   f"{report.agents_warned} warned.",
            fallback=TrumpStyleFormatter.format_doge_report(
                report.total_waste, report.agents_fired),
        )
        self.truth_social.post("doge_musk", message, trump_style=False)
        
        return asdict(report)
    
    def create_trade_offer(self, from_agent: str, to_agent: str,
                          resource_type: str, amount: float) -> TradeOffer:
        """Create a resource trade offer."""
        return self.tariff.create_offer(from_agent, to_agent, resource_type, amount)
    
    def get_system_summary(self) -> dict:
        """Get overall system summary."""
        total_tasks = len(self.tasks)
        done_tasks = sum(1 for t in self.tasks.values() if t.state == AgentState.DONE)
        active_tasks = sum(1 for t in self.tasks.values() 
                         if t.state not in [AgentState.DONE, AgentState.VETOED, AgentState.FIRED])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": done_tasks,
            "active_tasks": active_tasks,
            "completion_rate": done_tasks / total_tasks if total_tasks > 0 else 0,
            "doge_summary": self.doge.get_summary(),
            "firing_stats": self.firing.get_firing_stats(),
            "truth_social_posts": len(self.truth_social.posts),
            "llm_enabled": self.llm_enabled,
            "llm_usage": dict(self.llm_usage),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_tasks_by_state(self, state: AgentState) -> List[Task]:
        """Get all tasks in a specific state."""
        return [t for t in self.tasks.values() if t.state == state]
    
    def get_truth_social_feed(self, limit: int = 50) -> List[dict]:
        """Get Truth Social feed."""
        return self.truth_social.get_feed(limit)


# For testing
if __name__ == "__main__":
    orchestrator = MAGAgentsOrchestrator()
    
    # Create a test task
    task = orchestrator.create_task(
        "Build new API endpoint",
        "Create REST API for user management",
        "high"
    )
    print(f"Created task: {task.id}")
    
    # Move through states
    orchestrator.transition_state(task.id, AgentState.CONGRESS)
    print("Moved to Congress")
    
    orchestrator.transition_state(task.id, AgentState.POTUS)
    print("Moved to POTUS")
    
    orchestrator.approve_task(task.id)
    print("Approved by POTUS")
    
    # Get summary
    summary = orchestrator.get_system_summary()
    print(f"\nSystem Summary: {json.dumps(summary, indent=2)}")
