#!/usr/bin/env python3
"""
TRUMPTOPIA AI - Project Progress Reporter
Generates progress reports every 10 minutes
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

def count_files_by_type(directory: Path, extensions: list) -> dict:
    """Count files by extension."""
    counts = {}
    for ext in extensions:
        files = list(directory.rglob(f"*{ext}"))
        counts[ext] = len(files)
    return counts

def count_lines_of_code(directory: Path, extensions: list) -> int:
    """Count total lines of code."""
    total_lines = 0
    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
    return total_lines

def check_test_status() -> dict:
    """Run tests and get status."""
    test_dir = PROJECT_ROOT / "tests"
    if not test_dir.exists():
        return {"status": "no_tests", "passed": 0, "failed": 0}
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + result.stderr
        
        # Parse results
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        
        return {
            "status": "completed",
            "passed": passed,
            "failed": failed,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "passed": 0,
            "failed": 0
        }

def get_git_status() -> dict:
    """Get git repository status."""
    try:
        # Check if git repo
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Get last commit
        commit_result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        last_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "N/A"
        
        return {
            "is_repo": True,
            "uncommitted_changes": len(changes),
            "last_commit": last_commit
        }
    except:
        return {
            "is_repo": False,
            "uncommitted_changes": 0,
            "last_commit": "N/A"
        }

def get_project_structure() -> dict:
    """Analyze project structure."""
    structure = {}
    
    # Key directories
    dirs = ["agents", "tests", "docs", "examples"]
    for d in dirs:
        dir_path = PROJECT_ROOT / d
        if dir_path.exists():
            structure[d] = len(list(dir_path.rglob("*")))
        else:
            structure[d] = 0
    
    return structure

def generate_progress_report() -> dict:
    """Generate comprehensive progress report."""
    now = datetime.now()
    
    # File statistics
    python_files = count_files_by_type(PROJECT_ROOT, [".py"])
    md_files = count_files_by_type(PROJECT_ROOT, [".md"])
    json_files = count_files_by_type(PROJECT_ROOT, [".json"])
    
    # Lines of code
    loc = count_lines_of_code(PROJECT_ROOT, [".py"])
    
    # Test status
    tests = check_test_status()
    
    # Git status
    git = get_git_status()
    
    # Project structure
    structure = get_project_structure()
    
    # Core modules check
    core_modules = [
        "trump_style.py",
        "doge_auditor.py",
        "firing_mechanism.py",
        "tariff_negotiator.py",
        "orchestrator.py"
    ]
    
    modules_status = {}
    for module in core_modules:
        module_path = PROJECT_ROOT / module
        modules_status[module] = {
            "exists": module_path.exists(),
            "lines": count_lines_of_code(PROJECT_ROOT / module, [".py"]) if module_path.exists() else 0
        }
    
    # Agent SOUL files
    agents_dir = PROJECT_ROOT / "agents"
    agent_souls = []
    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                soul_file = agent_dir / "SOUL.md"
                if soul_file.exists():
                    agent_souls.append(agent_dir.name)
    
    report = {
        "timestamp": now.isoformat(),
        "project": "TRUMPTOPIA AI",
        "summary": {
            "total_python_files": python_files.get(".py", 0),
            "total_md_files": md_files.get(".md", 0),
            "total_json_files": json_files.get(".json", 0),
            "lines_of_code": loc,
            "test_status": tests["status"],
            "tests_passed": tests["passed"],
            "tests_failed": tests["failed"]
        },
        "core_modules": modules_status,
        "agents_configured": len(agent_souls),
        "agent_list": agent_souls,
        "project_structure": structure,
        "git_status": git,
        "progress_percentage": calculate_progress_percentage(modules_status, agent_souls, tests)
    }
    
    return report

def calculate_progress_percentage(modules: dict, agents: list, tests: dict) -> int:
    """Calculate rough progress percentage."""
    score = 0
    total = 100
    
    # Core modules (50 points)
    module_score = sum(1 for m in modules.values() if m["exists"]) / len(modules) * 50
    score += module_score
    
    # Agents (30 points)
    expected_agents = 10  # POTUS, Congress, SCOTUS, DOGE, 6 Cabinet
    agent_score = min(len(agents) / expected_agents, 1.0) * 30
    score += agent_score
    
    # Tests (20 points)
    if tests["status"] == "completed" and tests["failed"] == 0:
        score += 20
    elif tests["status"] == "completed":
        score += 10
    elif tests["status"] == "no_tests":
        score += 0
    
    return int(score)

def format_report_text(report: dict) -> str:
    """Format report as readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"🇺🇸 TRUMPTOPIA AI - PROGRESS REPORT")
    lines.append(f"📅 {report['timestamp']}")
    lines.append("=" * 60)
    lines.append("")
    
    # Progress bar
    progress = report['progress_percentage']
    bar_length = 30
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    lines.append(f"📊 Overall Progress: [{bar}] {progress}%")
    lines.append("")
    
    # Summary
    summary = report['summary']
    lines.append("📈 CODE STATISTICS:")
    lines.append(f"   • Python files: {summary['total_python_files']}")
    lines.append(f"   • Documentation files: {summary['total_md_files']}")
    lines.append(f"   • Lines of code: {summary['lines_of_code']:,}")
    lines.append("")
    
    # Core modules
    lines.append("🔧 CORE MODULES:")
    for module, status in report['core_modules'].items():
        icon = "✅" if status['exists'] else "❌"
        lines.append(f"   {icon} {module}: {status['lines']} lines")
    lines.append("")
    
    # Agents
    lines.append(f"🤖 AGENTS CONFIGURED: {report['agents_configured']}")
    for agent in report['agent_list']:
        lines.append(f"   • {agent}")
    lines.append("")
    
    # Tests
    lines.append("🧪 TEST STATUS:")
    test = report['summary']
    if test['test_status'] == 'completed':
        lines.append(f"   ✅ Passed: {test['tests_passed']}")
        lines.append(f"   {'✅' if test['tests_failed'] == 0 else '❌'} Failed: {test['tests_failed']}")
    elif test['test_status'] == 'no_tests':
        lines.append("   ⚠️  No tests found")
    else:
        lines.append(f"   ❌ Error: {test.get('error', 'Unknown')}")
    lines.append("")
    
    # Git status
    git = report['git_status']
    if git['is_repo']:
        lines.append("📦 GIT STATUS:")
        lines.append(f"   • Uncommitted changes: {git['uncommitted_changes']}")
        lines.append(f"   • Last commit: {git['last_commit']}")
    lines.append("")
    
    # Trump-style message
    if progress >= 80:
        lines.append("🎩 TRUMP SAYS: This is TREMENDOUS progress! HUGE win!!!")
    elif progress >= 50:
        lines.append("🎩 TRUMP SAYS: Making good progress! Keep winning!!!")
    else:
        lines.append("🎩 TRUMP SAYS: Need to work harder! SAD!!! Get it done!!!")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)

def save_report(report: dict):
    """Save report to file."""
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"progress_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save latest
    latest_file = reports_dir / "latest_progress.json"
    with open(latest_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_file

def main():
    """Main entry point."""
    print("🔄 Generating TRUMPTOPIA AI progress report...\n")
    
    report = generate_progress_report()
    
    # Save to file
    report_file = save_report(report)
    
    # Print formatted report
    print(format_report_text(report))
    print(f"\n💾 Report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()
