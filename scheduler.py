# MAGAgents - Task Scheduler
# Automatic dispatch, stall detection, and escalation
# Inspired by edict's scheduler system

import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

class MAGAgentsScheduler:
    """
    Automatic task scheduler for MAGAgents.
    
    Features:
    - Periodic scan for stalled tasks
    - Automatic retry on timeout
    - Escalation to higher authorities
    - Auto-rollback on persistent failure
    """
    
    def __init__(self, orchestrator, scan_interval: int = 60):
        """
        Initialize scheduler.
        
        Args:
            orchestrator: MAGAgentsOrchestrator instance
            scan_interval: Seconds between scans (default: 60)
        """
        self.orchestrator = orchestrator
        self.scan_interval = scan_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.last_scan = None
        
        # Escalation chain
        self.ESCALATION_CHAIN = {
            0: None,  # No escalation
            1: "congress_senate",  # First escalation: Senate
            2: "trump_president",  # Second escalation: POTUS
        }
    
    def start(self):
        """Start scheduler in background thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"🕐 Scheduler started (scan interval: {self.scan_interval}s)")
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🕐 Scheduler stopped")
    
    def _run_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._scan_tasks()
                self.last_scan = datetime.now()
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            time.sleep(self.scan_interval)
    
    def _scan_tasks(self):
        """Scan all tasks for stalled ones."""
        for task_id, task in self.orchestrator.tasks.items():
            # Skip completed/cancelled tasks
            if task.state.value in ['done', 'vetoed', 'fired', 'cancelled']:
                continue
            
            # Check if task is stalled
            if task.is_stalled(task._scheduler["stallThresholdSec"]):
                self._handle_stalled_task(task)
    
    def _handle_stalled_task(self, task):
        """Handle a stalled task."""
        scheduler = task._scheduler
        
        # Stage 1: Retry if under max retry limit
        if scheduler["retryCount"] < scheduler["maxRetry"]:
            self._retry_task(task)
            return
        
        # Stage 2: Escalate if under max escalation level
        if scheduler["escalationLevel"] < 2:
            self._escalate_task(task)
            return
        
        # Stage 3: Auto-rollback if enabled
        if scheduler.get("autoRollback", True):
            self._rollback_task(task)
    
    def _retry_task(self, task):
        """Retry a stalled task."""
        task._scheduler["retryCount"] += 1
        
        # Add flow log
        task.add_flow_log(
            "Scheduler",
            task.assigned_agent or "System",
            f"🔄 Auto-retry #{task._scheduler['retryCount']} after stall"
        )
        
        # Re-dispatch to current agent
        if task.assigned_agent:
            self._dispatch_to_agent(task, task.assigned_agent)
        
        task.clear_stall()
        print(f"🔄 Retrying task {task.id} (attempt #{task._scheduler['retryCount']})")
    
    def _escalate_task(self, task):
        """Escalate a stalled task to higher authority."""
        current_level = task._scheduler["escalationLevel"]
        next_level = current_level + 1
        escalator = self.ESCALATION_CHAIN.get(next_level)
        
        if not escalator:
            return
        
        task._scheduler["escalationLevel"] = next_level
        
        # Add flow log
        task.add_flow_log(
            "Scheduler",
            escalator,
            f"📈 Escalated to level {next_level}: {escalator}"
        )
        
        # Wake up escalator agent
        self._dispatch_to_agent(task, escalator, is_escalation=True)
        
        task.clear_stall()
        print(f"📈 Task {task.id} escalated to {escalator}")
    
    def _rollback_task(self, task):
        """Rollback task to previous stable state."""
        if not task._prev_state:
            return
        
        # Add flow log
        task.add_flow_log(
            "Scheduler",
            task._prev_state,
            f"⏮️ Auto-rollback due to persistent stall"
        )
        
        # Rollback state
        from orchestrator import AgentState
        task.state = AgentState(task._prev_state)
        
        # Reset counters
        task._scheduler["retryCount"] = 0
        task._scheduler["escalationLevel"] = 0
        
        task.clear_stall()
        print(f"⏮️ Task {task.id} rolled back to {task._prev_state}")
    
    def _dispatch_to_agent(self, task, agent_id: str, is_escalation: bool = False):
        """Dispatch task to an agent."""
        # In a real implementation, this would trigger the agent
        # For now, we just update the flow log
        trigger = "escalation" if is_escalation else "retry"
        task._scheduler["lastDispatchStatus"] = f"dispatched-{trigger}"
    
    def get_status(self) -> dict:
        """Get scheduler status."""
        active_tasks = len([t for t in self.orchestrator.tasks.values() 
                          if t.state.value not in ['done', 'vetoed', 'fired']])
        stalled_tasks = len([t for t in self.orchestrator.tasks.values() 
                           if t.is_stalled()])
        
        return {
            "running": self.running,
            "scan_interval": self.scan_interval,
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "active_tasks": active_tasks,
            "stalled_tasks": stalled_tasks
        }
    
    def force_scan(self):
        """Force immediate scan (for testing)."""
        self._scan_tasks()
        print("🔍 Manual scan completed")


# Example usage
if __name__ == "__main__":
    from orchestrator import MAGAgentsOrchestrator
    
    orch = MAGAgentsOrchestrator()
    scheduler = MAGAgentsScheduler(orch)
    
    # Start scheduler
    scheduler.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
