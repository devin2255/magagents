# TRUMPTOPIA AI - Core Orchestrator
# Manages all agents, state transitions, and interactions

import json
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


class AgentState(Enum):
    """States in the TRUMPTOPIA system."""
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
    """A task in the TRUMPTOPIA system."""
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
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "state": self.state.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        data = data.copy()
        data["state"] = AgentState(data["state"])
        return cls(**data)


class TrumptopiaOrchestrator:
    """
    Central orchestrator for the TRUMPTOPIA AI system.
    
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
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize subsystems
        self.doge = DOGEAuditor(self.data_dir)
        self.firing = FiringMechanism(self.data_dir)
        self.tariff = TariffNegotiator(self.doge)
        self.truth_social = TruthSocialAPI()
        
        # Task storage
        self.tasks_file = self.data_dir / "tasks.json"
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from storage."""
        if self.tasks_file.exists():
            data = json.loads(self.tasks_file.read_text())
            self.tasks = {k: Task.from_dict(v) for k, v in data.items()}
    
    def save_tasks(self):
        """Save tasks to storage."""
        data = {k: v.to_dict() for k, v in self.tasks.items()}
        self.tasks_file.write_text(json.dumps(data, indent=2))
    
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
        
        # Post to Truth Social
        self.truth_social.post(
            "trump_president",
            f"New task created: {title}! TREMENDOUS opportunity!!!",
            trump_style=True
        )
        
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
        
        message = messages.get(task.state, f"Task {task.id} moved to {task.state.value}")
        if reason:
            message += f" Reason: {reason}"
        
        self.truth_social.post("trump_president", message, trump_style=True)
    
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
        self.truth_social.post(
            "trump_president",
            TrumpStyleFormatter.format_firing(agent_id, reason),
            trump_style=False  # Already formatted
        )
        
        # Update any tasks assigned to this agent
        for task in self.tasks.values():
            if task.assigned_agent == agent_id:
                task.state = AgentState.FIRED
                task.updated_at = datetime.now().isoformat()
        
        self.save_tasks()
        return cert
    
    def veto_task(self, task_id: str, reason: str) -> bool:
        """Veto a task (POTUS power)."""
        success = self.transition_state(task_id, AgentState.VETOED, reason)
        if success:
            self.truth_social.post(
                "trump_president",
                TrumpStyleFormatter.format_veto(self.tasks[task_id].title, reason),
                trump_style=False
            )
        return success
    
    def approve_task(self, task_id: str) -> bool:
        """Approve a task (POTUS power)."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        success = self.transition_state(task_id, AgentState.CABINET, "Presidential approval")
        if success:
            self.truth_social.post(
                "trump_president",
                TrumpStyleFormatter.format_approval(
                    task.assigned_agent or "cabinet",
                    task.title
                ),
                trump_style=False
            )
        return success
    
    def get_doge_report(self) -> dict:
        """Generate DOGE daily report."""
        report = self.doge.generate_daily_report()
        
        # Post summary to Truth Social
        self.truth_social.post(
            "doge_musk",
            TrumpStyleFormatter.format_doge_report(
                report.total_waste,
                report.agents_fired
            ),
            trump_style=False
        )
        
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
    orchestrator = TrumptopiaOrchestrator()
    
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
