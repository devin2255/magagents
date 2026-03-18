#!/usr/bin/env python3
"""
TRUMPTOPIA AI - Kanban Update CLI
Agent command-line interface for interacting with the dashboard
Inspired by edict's kanban_update.py

Usage:
    python3 kanban_update.py state <task_id> <new_state> [remark]
    python3 kanban_update.py flow <task_id> <from> <to> <remark>
    python3 kanban_update.py progress <task_id> <text> [todos]
    python3 kanban_update.py todo <task_id> <todo_list>
    python3 kanban_update.py done <task_id> <output> <summary>
    python3 kanban_update.py stop <task_id> [reason]
    python3 kanban_update.py resume <task_id> [reason]
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import TrumptopiaOrchestrator, AgentState


class KanbanCLI:
    """CLI for agents to interact with the task board."""
    
    def __init__(self):
        self.orch = TrumptopiaOrchestrator()
        self.data_dir = Path(__file__).parent.parent / "data"
    
    def update_state(self, task_id: str, new_state: str, remark: str = ""):
        """Update task state."""
        try:
            state_enum = AgentState(new_state)
        except ValueError:
            print(f"❌ Invalid state: {new_state}")
            print(f"Valid states: {[s.value for s in AgentState]}")
            return False
        
        success = self.orch.transition_state(task_id, state_enum, remark)
        
        if success:
            task = self.orch.get_task(task_id)
            task.add_flow_log(
                task.assigned_agent or "System",
                new_state,
                remark or f"State changed to {new_state}"
            )
            self.orch.save_tasks()
            print(f"✅ Task {task_id} state updated to {new_state}")
            if remark:
                print(f"   Remark: {remark}")
        else:
            print(f"❌ Failed to update state for {task_id}")
            print("   Check if transition is valid")
        
        return success
    
    def add_flow_log(self, task_id: str, from_entity: str, to_entity: str, remark: str):
        """Add a flow log entry."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        task.add_flow_log(from_entity, to_entity, remark)
        self.orch.save_tasks()
        print(f"✅ Flow log added to {task_id}")
        print(f"   {from_entity} → {to_entity}: {remark}")
        return True
    
    def add_progress(self, task_id: str, text: str, todos: str = ""):
        """Add a progress report."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        # Parse todos if provided
        todos_list = []
        if todos:
            for i, item in enumerate(todos.split("|")):
                parts = item.strip().split(":")
                if len(parts) >= 2:
                    todos_list.append({
                        "id": str(i + 1),
                        "title": parts[0].strip(),
                        "status": parts[1].strip() if len(parts) > 1 else "pending"
                    })
        
        # Update task todos
        if todos_list:
            task.update_todos(todos_list)
        
        # Add progress log
        task.add_progress_log(
            agent=task.assigned_agent or "Unknown",
            text=text,
            todos_snapshot=todos_list or task.todos
        )
        
        self.orch.save_tasks()
        print(f"✅ Progress logged for {task_id}")
        print(f"   {text}")
        if todos_list:
            print(f"   Todos: {len(todos_list)} items")
        return True
    
    def update_todos(self, task_id: str, todo_list: str):
        """Update task todos."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        todos = []
        for i, item in enumerate(todo_list.split("|")):
            parts = item.strip().split(":")
            todos.append({
                "id": str(i + 1),
                "title": parts[0].strip(),
                "status": parts[1].strip() if len(parts) > 1 else "pending"
            })
        
        task.update_todos(todos)
        self.orch.save_tasks()
        print(f"✅ Todos updated for {task_id}")
        print(f"   {len(todos)} items")
        return True
    
    def mark_done(self, task_id: str, output: str, summary: str):
        """Mark task as done."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        success = self.orch.transition_state(task_id, AgentState.DONE, "Task completed")
        
        if success:
            task.output = output
            task.add_flow_log(
                task.assigned_agent or "System",
                "Done",
                summary
            )
            self.orch.save_tasks()
            print(f"✅ Task {task_id} marked as DONE")
            print(f"   Output: {output}")
            print(f"   Summary: {summary}")
        else:
            print(f"❌ Failed to complete task {task_id}")
        
        return success
    
    def stop_task(self, task_id: str, reason: str = ""):
        """Stop/pause a task."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        # Save current state for resume
        task._prev_state = task.state.value
        task.block = reason or "Stopped by agent"
        
        task.add_flow_log(
            "System",
            "Blocked",
            f"⏸️ Task stopped: {reason}"
        )
        
        self.orch.save_tasks()
        print(f"⏸️ Task {task_id} stopped")
        if reason:
            print(f"   Reason: {reason}")
        return True
    
    def resume_task(self, task_id: str, reason: str = ""):
        """Resume a stopped task."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        if not task._prev_state:
            print(f"❌ No previous state to resume to")
            return False
        
        # Restore previous state
        prev_state = AgentState(task._prev_state)
        success = self.orch.transition_state(task_id, prev_state, reason or "Resumed")
        
        if success:
            task.block = "无"
            task.add_flow_log(
                "System",
                prev_state.value,
                f"▶️ Task resumed: {reason}"
            )
            self.orch.save_tasks()
            print(f"▶️ Task {task_id} resumed to {prev_state.value}")
        else:
            print(f"❌ Failed to resume task {task_id}")
        
        return success
    
    def list_tasks(self, state: str = None):
        """List all tasks."""
        tasks = self.orch.tasks
        
        if state:
            tasks = {k: v for k, v in tasks.items() if v.state.value == state}
        
        if not tasks:
            print("No tasks found")
            return
        
        print(f"\n📋 Tasks ({len(tasks)} total):")
        print("-" * 80)
        print(f"{'ID':<15} {'State':<12} {'Priority':<10} {'Agent':<15} {'Title'}")
        print("-" * 80)
        
        for task_id, task in sorted(tasks.items()):
            print(f"{task_id:<15} {task.state.value:<12} {task.priority:<10} "
                  f"{task.assigned_agent or 'N/A':<15} {task.title[:30]}")
        
        print()
    
    def show_task(self, task_id: str):
        """Show task details."""
        task = self.orch.get_task(task_id)
        if not task:
            print(f"❌ Task {task_id} not found")
            return False
        
        print(f"\n📋 Task Details: {task_id}")
        print("=" * 60)
        print(f"Title:       {task.title}")
        print(f"State:       {task.state.value}")
        print(f"Priority:    {task.priority}")
        print(f"Agent:       {task.assigned_agent or 'Unassigned'}")
        print(f"Created:     {task.created_at}")
        print(f"Updated:     {task.updated_at}")
        print(f"Tokens:      {task.tokens_used}")
        print(f"Cost:        ${task.cost:.4f}")
        print(f"Block:       {task.block}")
        
        if task.todos:
            print(f"\n📝 Todos ({len(task.todos)}):")
            for todo in task.todos:
                status_icon = "✅" if todo.get('status') == 'completed' else "🔄" if todo.get('status') == 'in-progress' else "⏳"
                print(f"   {status_icon} {todo.get('title', 'Untitled')}")
        
        if task.flow_log:
            print(f"\n📜 Flow Log ({len(task.flow_log)} entries):")
            for entry in task.flow_log[-5:]:  # Show last 5
                print(f"   {entry.get('at', 'N/A')[:19]}: {entry.get('from', '?')} → {entry.get('to', '?')}")
        
        if task.progress_log:
            print(f"\n📊 Progress Log ({len(task.progress_log)} entries):")
            for entry in task.progress_log[-3:]:  # Show last 3
                print(f"   {entry.get('at', 'N/A')[:19]}: {entry.get('text', 'N/A')[:50]}")
        
        print()
        return True


def main():
    parser = argparse.ArgumentParser(
        description='TRUMPTOPIA AI Kanban CLI - Agent task management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update task state
  python3 kanban_update.py state TRUMP-001 doing "Starting implementation"
  
  # Add progress with todos
  python3 kanban_update.py progress TRUMP-001 "50% complete" "Design:completed|Coding:in-progress|Testing:pending"
  
  # Mark task done
  python3 kanban_update.py done TRUMP-001 "https://github.com/..." "API implemented successfully"
  
  # List all tasks
  python3 kanban_update.py list
  
  # Show task details
  python3 kanban_update.py show TRUMP-001
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # State command
    state_parser = subparsers.add_parser('state', help='Update task state')
    state_parser.add_argument('task_id', help='Task ID')
    state_parser.add_argument('new_state', help='New state (pending/congress/potus/cabinet/doing/done)')
    state_parser.add_argument('remark', nargs='?', default='', help='Optional remark')
    
    # Flow command
    flow_parser = subparsers.add_parser('flow', help='Add flow log entry')
    flow_parser.add_argument('task_id', help='Task ID')
    flow_parser.add_argument('from_entity', help='From entity')
    flow_parser.add_argument('to_entity', help='To entity')
    flow_parser.add_argument('remark', help='Remark')
    
    # Progress command
    progress_parser = subparsers.add_parser('progress', help='Add progress report')
    progress_parser.add_argument('task_id', help='Task ID')
    progress_parser.add_argument('text', help='Progress text')
    progress_parser.add_argument('todos', nargs='?', default='', help='Todos (title:status|title:status)')
    
    # Todo command
    todo_parser = subparsers.add_parser('todo', help='Update todos')
    todo_parser.add_argument('task_id', help='Task ID')
    todo_parser.add_argument('todo_list', help='Todo list (title:status|title:status)')
    
    # Done command
    done_parser = subparsers.add_parser('done', help='Mark task as done')
    done_parser.add_argument('task_id', help='Task ID')
    done_parser.add_argument('output', help='Output URL or path')
    done_parser.add_argument('summary', help='Completion summary')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop/pause task')
    stop_parser.add_argument('task_id', help='Task ID')
    stop_parser.add_argument('reason', nargs='?', default='', help='Reason for stopping')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume stopped task')
    resume_parser.add_argument('task_id', help='Task ID')
    resume_parser.add_argument('reason', nargs='?', default='', help='Reason for resuming')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--state', help='Filter by state')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('task_id', help='Task ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = KanbanCLI()
    
    # Execute command
    commands = {
        'state': lambda: cli.update_state(args.task_id, args.new_state, args.remark),
        'flow': lambda: cli.add_flow_log(args.task_id, args.from_entity, args.to_entity, args.remark),
        'progress': lambda: cli.add_progress(args.task_id, args.text, args.todos),
        'todo': lambda: cli.update_todos(args.task_id, args.todo_list),
        'done': lambda: cli.mark_done(args.task_id, args.output, args.summary),
        'stop': lambda: cli.stop_task(args.task_id, args.reason),
        'resume': lambda: cli.resume_task(args.task_id, args.reason),
        'list': lambda: cli.list_tasks(args.state),
        'show': lambda: cli.show_task(args.task_id),
    }
    
    if args.command in commands:
        commands[args.command]()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
