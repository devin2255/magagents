# Department of Government Efficiency (DOGE)
# Inspired by Elon Musk's DOGE initiative

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AgentPerformance:
    """Performance metrics for an Agent."""
    agent_id: str
    tasks_completed: int
    tasks_failed: int
    avg_response_time: float  # seconds
    total_tokens: int
    total_cost: float
    efficiency_score: float  # 0-100
    loyalty_score: float  # 0-100
    last_active: datetime
    violations: List[str]

@dataclass
class WasteReport:
    """Daily waste report from DOGE."""
    date: str
    total_waste: float
    agents_fired: int
    agents_warned: int
    inefficiencies_found: List[Dict]
    savings_recommendations: List[str]


class DOGEAuditor:
    """
    Department of Government Efficiency Auditor.
    
    Monitors all agents for:
    - Token waste (inefficient prompts)
    - Time waste (slow responses)
    - Task failures
    - Policy violations
    - Loyalty issues
    """
    
    WASTE_THRESHOLDS = {
        "token_per_task": 5000,  # Max tokens per task
        "response_time": 300,     # Max seconds for response
        "failure_rate": 0.3,      # Max 30% failure rate
        "efficiency": 60.0,       # Min efficiency score
    }
    
    TARIFF_RATES = {
        "normal": 0.1,   # 10% tariff
        "high": 0.25,    # 25% tariff
        "emergency": 0.5 # 50% tariff
    }
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.performance_db = self.data_dir / "doge_performance.json"
        self.waste_logs = self.data_dir / "doge_waste_logs.json"
        self.agent_history = self.load_performance_db()
        self.waste_history = self.load_waste_logs()
    
    def load_performance_db(self) -> Dict[str, AgentPerformance]:
        """Load performance database."""
        if not self.performance_db.exists():
            return {}
        
        data = json.loads(self.performance_db.read_text())
        return {
            k: AgentPerformance(
                agent_id=v["agent_id"],
                tasks_completed=v["tasks_completed"],
                tasks_failed=v["tasks_failed"],
                avg_response_time=v["avg_response_time"],
                total_tokens=v["total_tokens"],
                total_cost=v["total_cost"],
                efficiency_score=v["efficiency_score"],
                loyalty_score=v["loyalty_score"],
                last_active=datetime.fromisoformat(v["last_active"]),
                violations=v["violations"]
            )
            for k, v in data.items()
        }
    
    def save_performance_db(self):
        """Save performance database."""
        data = {
            k: {
                **asdict(v),
                "last_active": v.last_active.isoformat()
            }
            for k, v in self.agent_history.items()
        }
        self.performance_db.write_text(json.dumps(data, indent=2))
    
    def load_waste_logs(self) -> List[WasteReport]:
        """Load waste report history."""
        if not self.waste_logs.exists():
            return []
        
        data = json.loads(self.waste_logs.read_text())
        return [
            WasteReport(
                date=d["date"],
                total_waste=d["total_waste"],
                agents_fired=d["agents_fired"],
                agents_warned=d["agents_warned"],
                inefficiencies_found=d["inefficiencies_found"],
                savings_recommendations=d["savings_recommendations"]
            )
            for d in data
        ]
    
    def save_waste_logs(self):
        """Save waste report history."""
        data = [
            {
                **asdict(report),
                "inefficiencies_found": report.inefficiencies_found,
                "savings_recommendations": report.savings_recommendations
            }
            for report in self.waste_history
        ]
        self.waste_logs.write_text(json.dumps(data, indent=2))
    
    def record_task_completion(self, agent_id: str, tokens: int, cost: float, 
                               response_time: float, success: bool):
        """Record a task completion for an agent."""
        if agent_id not in self.agent_history:
            self.agent_history[agent_id] = AgentPerformance(
                agent_id=agent_id,
                tasks_completed=0,
                tasks_failed=0,
                avg_response_time=0.0,
                total_tokens=0,
                total_cost=0.0,
                efficiency_score=100.0,
                loyalty_score=100.0,
                last_active=datetime.now(),
                violations=[]
            )
        
        perf = self.agent_history[agent_id]
        
        if success:
            perf.tasks_completed += 1
        else:
            perf.tasks_failed += 1
        
        perf.total_tokens += tokens
        perf.total_cost += cost
        perf.last_active = datetime.now()
        
        # Update average response time
        total_tasks = perf.tasks_completed + perf.tasks_failed
        perf.avg_response_time = (
            (perf.avg_response_time * (total_tasks - 1) + response_time) / total_tasks
        )
        
        # Calculate efficiency score
        perf.efficiency_score = self._calculate_efficiency(perf)
        
        # Check for violations
        self._check_violations(perf, tokens, response_time, success)
        
        self.save_performance_db()
    
    def _calculate_efficiency(self, perf: AgentPerformance) -> float:
        """Calculate efficiency score (0-100)."""
        if perf.tasks_completed + perf.tasks_failed == 0:
            return 100.0
        
        # Base score from success rate
        success_rate = perf.tasks_completed / (perf.tasks_completed + perf.tasks_failed)
        score = success_rate * 100
        
        # Penalize for slow responses
        if perf.avg_response_time > self.WASTE_THRESHOLDS["response_time"]:
            score -= 20
        
        # Penalize for high token usage
        avg_tokens = perf.total_tokens / max(perf.tasks_completed + perf.tasks_failed, 1)
        if avg_tokens > self.WASTE_THRESHOLDS["token_per_task"]:
            score -= 15
        
        # Penalize for violations
        score -= len(perf.violations) * 10
        
        return max(0.0, min(100.0, score))
    
    def _check_violations(self, perf: AgentPerformance, tokens: int, 
                          response_time: float, success: bool):
        """Check for policy violations."""
        violations = []
        
        if tokens > self.WASTE_THRESHOLDS["token_per_task"]:
            violations.append(f"Excessive token usage: {tokens}")
        
        if response_time > self.WASTE_THRESHOLDS["response_time"]:
            violations.append(f"Slow response: {response_time:.1f}s")
        
        if not success:
            violations.append("Task failure")
        
        # Check failure rate
        total = perf.tasks_completed + perf.tasks_failed
        if total > 5 and perf.tasks_failed / total > self.WASTE_THRESHOLDS["failure_rate"]:
            violations.append(f"High failure rate: {perf.tasks_failed}/{total}")
        
        perf.violations.extend(violations)
        # Keep only last 10 violations
        perf.violations = perf.violations[-10:]
    
    def generate_daily_report(self) -> WasteReport:
        """Generate daily waste report."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        total_waste = 0.0
        agents_fired = 0
        agents_warned = 0
        inefficiencies = []
        recommendations = []
        
        for agent_id, perf in self.agent_history.items():
            # Calculate waste for this agent
            waste = self._calculate_waste(perf)
            total_waste += waste
            
            # Check if agent should be fired
            if perf.efficiency_score < 30 or len(perf.violations) >= 5:
                agents_fired += 1
                inefficiencies.append({
                    "agent": agent_id,
                    "type": "termination",
                    "reason": f"Efficiency {perf.efficiency_score:.1f}, {len(perf.violations)} violations",
                    "waste_amount": waste
                })
            elif perf.efficiency_score < 60:
                agents_warned += 1
                inefficiencies.append({
                    "agent": agent_id,
                    "type": "warning",
                    "reason": f"Low efficiency: {perf.efficiency_score:.1f}",
                    "waste_amount": waste
                })
            
            # Add inefficiency details
            if perf.avg_response_time > self.WASTE_THRESHOLDS["response_time"]:
                inefficiencies.append({
                    "agent": agent_id,
                    "type": "slow_response",
                    "avg_time": perf.avg_response_time,
                    "waste_amount": waste * 0.2
                })
        
        # Generate recommendations
        if agents_fired > 0:
            recommendations.append(f"Fired {agents_fired} inefficient agents")
        if agents_warned > 0:
            recommendations.append(f"Issued warnings to {agents_warned} underperforming agents")
        if total_waste > 100:
            recommendations.append("Implement stricter token limits")
        
        report = WasteReport(
            date=today,
            total_waste=total_waste,
            agents_fired=agents_fired,
            agents_warned=agents_warned,
            inefficiencies_found=inefficiencies,
            savings_recommendations=recommendations
        )
        
        self.waste_history.append(report)
        self.save_waste_logs()
        
        return report
    
    def _calculate_waste(self, perf: AgentPerformance) -> float:
        """Calculate waste amount for an agent."""
        waste = 0.0
        
        # Token waste
        avg_tokens = perf.total_tokens / max(perf.tasks_completed + perf.tasks_failed, 1)
        if avg_tokens > self.WASTE_THRESHOLDS["token_per_task"]:
            waste += (avg_tokens - self.WASTE_THRESHOLDS["token_per_task"]) * 0.001
        
        # Time waste
        if perf.avg_response_time > self.WASTE_THRESHOLDS["response_time"]:
            waste += (perf.avg_response_time - self.WASTE_THRESHOLDS["response_time"]) * 0.01
        
        # Failure waste
        waste += perf.tasks_failed * 0.5
        
        return waste
    
    def get_firing_recommendations(self) -> List[str]:
        """Get list of agents recommended for firing."""
        recommendations = []
        for agent_id, perf in self.agent_history.items():
            if perf.efficiency_score < 30 or len(perf.violations) >= 5:
                recommendations.append(agent_id)
        return recommendations
    
    def get_tariff_rate(self, agent_id: str) -> float:
        """Get tariff rate for an agent based on performance."""
        if agent_id not in self.agent_history:
            return self.TARIFF_RATES["normal"]
        
        perf = self.agent_history[agent_id]
        
        if perf.efficiency_score < 30:
            return self.TARIFF_RATES["emergency"]
        elif perf.efficiency_score < 60:
            return self.TARIFF_RATES["high"]
        else:
            return self.TARIFF_RATES["normal"]
    
    def get_leaderboard(self, limit: int = 10) -> List[AgentPerformance]:
        """Get top performing agents."""
        sorted_agents = sorted(
            self.agent_history.values(),
            key=lambda x: x.efficiency_score,
            reverse=True
        )
        return sorted_agents[:limit]
    
    def get_summary(self) -> Dict:
        """Get overall DOGE summary."""
        if not self.agent_history:
            return {
                "total_agents": 0,
                "avg_efficiency": 0.0,
                "total_waste": 0.0,
                "agents_fired": 0
            }
        
        total_waste = sum(self._calculate_waste(p) for p in self.agent_history.values())
        avg_efficiency = sum(p.efficiency_score for p in self.agent_history.values()) / len(self.agent_history)
        agents_fired = sum(1 for p in self.agent_history.values() if p.efficiency_score < 30)
        
        return {
            "total_agents": len(self.agent_history),
            "avg_efficiency": avg_efficiency,
            "total_waste": total_waste,
            "agents_fired": agents_fired,
            "last_updated": datetime.now().isoformat()
        }
