#!/usr/bin/env python3
"""
MAGAgents Dashboard Server
Real-time API for Oval Office Dashboard
Port: 7892
"""

import json
import sys
import threading
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# Ensure emoji/Unicode output works on all platforms (e.g. Windows GBK consoles)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import MAGAgentsOrchestrator

class DashboardHandler(BaseHTTPRequestHandler):
    orchestrator = None
    
    def __init__(self, *args, **kwargs):
        if DashboardHandler.orchestrator is None:
            DashboardHandler.orchestrator = MAGAgentsOrchestrator()
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        # Suppress logs
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        path = self.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()
        
        try:
            if path == '/api/tasks':
                data = self.get_tasks()
            elif path == '/api/agents':
                data = self.get_agents()
            elif path == '/api/stats':
                data = self.get_stats()
            elif path == '/api/doge':
                data = self.get_doge_report()
            elif path == '/api/posts':
                data = self.get_truth_posts()
            else:
                data = {'error': 'Not found'}
                self.send_response(404)
            
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        path = self.path
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode()) if body else {}
            
            if path == '/api/task/action':
                result = self.handle_task_action(data)
            elif path == '/api/task/create':
                result = self.handle_create_task(data)
            elif path == '/api/task/run':
                result = self.handle_run_agentic(data)
            elif path == '/api/agent/fire':
                result = self.handle_fire_agent(data)
            else:
                result = {'error': 'Not found'}
                self.send_response(404)
            
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_tasks(self):
        """Get all tasks"""
        tasks = []
        for task_id, task in self.orchestrator.tasks.items():
            tasks.append({
                'id': task.id,
                'title': task.title,
                'state': task.state.value,
                'priority': task.priority,
                'assigned_agent': task.assigned_agent,
                'agent': task.assigned_agent,  # alias for the frontend
                'created': task.created_at,
                'created_at': task.created_at,
                'tokens_used': task.tokens_used,
                'cost': task.cost,
                'outcome': getattr(task, 'outcome', ''),
                'output': getattr(task, 'output', ''),
                'decision_trace': getattr(task, 'decision_trace', []) or []
            })
        return tasks
    
    def get_agents(self):
        """Get all agents"""
        agents = []
        for agent_id, perf in self.orchestrator.doge.agent_history.items():
            agents.append({
                'id': agent_id,
                'efficiency': perf.efficiency_score,
                'loyalty': perf.loyalty_score,
                'tasks_completed': perf.tasks_completed,
                'tasks_failed': perf.tasks_failed,
                'total_tokens': perf.total_tokens,
                'status': 'fired' if self.orchestrator.firing.is_agent_fired(agent_id) else 'active'
            })
        return agents
    
    def get_stats(self):
        """Get system stats"""
        summary = self.orchestrator.get_system_summary()
        return {
            'total_tasks': summary['total_tasks'],
            'active_tasks': summary['active_tasks'],
            'completed_tasks': summary.get('completed_tasks', 0),
            'efficiency': summary['doge_summary']['avg_efficiency'],
            'approval_rating': 87,  # Mock for now
            'llm_enabled': summary.get('llm_enabled', False),
            'llm_usage': summary.get('llm_usage', {})
        }
    
    def get_doge_report(self):
        """Get DOGE report"""
        report = self.orchestrator.doge.generate_daily_report()
        return {
            'waste': report.total_waste,
            'agents_fired': report.agents_fired,
            'agents_warned': report.agents_warned,
            'inefficiencies': report.inefficiencies_found,
            'recommendations': report.savings_recommendations
        }
    
    def get_truth_posts(self):
        """Get Truth Social posts"""
        posts = self.orchestrator.truth_social.get_feed(50)
        return [
            {
                'agent_id': p['agent_id'],
                'content': p['message'],
                'timestamp': p['timestamp'],
                'likes': p['likes'],
                'reposts': p['reposts']
            }
            for p in posts
        ]
    
    def handle_task_action(self, data):
        """Handle task actions (approve/veto)"""
        task_id = data.get('task_id')
        action = data.get('action')
        
        if action == 'approve':
            success = self.orchestrator.approve_task(task_id)
        elif action == 'veto':
            success = self.orchestrator.veto_task(task_id, data.get('reason', 'Vetoed by POTUS'))
        else:
            return {'success': False, 'error': 'Unknown action'}
        
        return {'success': success}
    
    def handle_create_task(self, data):
        """Create a new task from the dashboard."""
        title = (data.get('title') or '').strip()
        if not title:
            return {'success': False, 'error': 'Empty title'}
        task = self.orchestrator.create_task(
            title=title,
            description=data.get('description', ''),
            priority=data.get('priority', 'normal'),
        )
        return {'success': True, 'task_id': task.id}

    def handle_run_agentic(self, data):
        """Run a task through the full agentic government flow."""
        task_id = data.get('task_id')
        if not task_id or task_id not in self.orchestrator.tasks:
            return {'success': False, 'error': 'Unknown task'}
        result = self.orchestrator.run_task_agentic(task_id)
        return {
            'success': 'error' not in result,
            'outcome': result.get('outcome'),
            'trace': result.get('trace', []),
            'llm_enabled': self.orchestrator.llm_enabled,
        }

    def handle_fire_agent(self, data):
        """Handle agent firing"""
        agent_id = data.get('agent_id')
        reason = data.get('reason', 'INEFFICIENCY')
        
        cert = self.orchestrator.fire_agent(agent_id, reason)
        
        if cert:
            return {
                'success': True,
                'certificate_id': cert.certificate_id,
                'message': cert.message
            }
        return {'success': False, 'error': 'Failed to fire agent'}


class DashboardServer:
    """Dashboard HTTP Server"""
    
    def __init__(self, port=7892):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start server in background thread"""
        self.server = ThreadingHTTPServer(('0.0.0.0', self.port), DashboardHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"🚀 Dashboard server running on http://localhost:{self.port}")
        print(f"📊 API endpoints:")
        print(f"   GET  /api/tasks    - List all tasks")
        print(f"   GET  /api/agents   - List all agents")
        print(f"   GET  /api/stats    - System statistics")
        print(f"   GET  /api/doge     - DOGE waste report")
        print(f"   GET  /api/posts    - Truth Social feed")
    
    def stop(self):
        """Stop server"""
        if self.server:
            self.server.shutdown()
            print("Dashboard server stopped")


def serve_static(port=7892):
    """Serve static files and API"""
    from http.server import SimpleHTTPRequestHandler
    import os
    
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    class CombinedHandler(DashboardHandler, SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/api/'):
                DashboardHandler.do_GET(self)
            else:
                # Serve static files
                if self.path == '/':
                    self.path = '/dashboard.html'
                SimpleHTTPRequestHandler.do_GET(self)
    
    server = ThreadingHTTPServer(('0.0.0.0', port), CombinedHandler)
    print(f"🚀 MAGAgents Dashboard")
    print(f"📊 URL: http://localhost:{port}")
    print(f"🏛️  The Oval Office Command Center")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MAGAgents Dashboard Server')
    parser.add_argument('--port', type=int, default=7892, help='Server port')
    parser.add_argument('--static', action='store_true', help='Serve static files')
    args = parser.parse_args()
    
    if args.static:
        serve_static(args.port)
    else:
        server = DashboardServer(args.port)
        server.start()
        
        # Keep main thread alive
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
