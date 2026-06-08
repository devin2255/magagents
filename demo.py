#!/usr/bin/env python3
"""
MAGAgents - Demo Script
Demonstrates all major features
"""

import sys
from pathlib import Path

# Ensure emoji/Unicode output works on all platforms (e.g. Windows GBK consoles)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from trump_style import TrumpStyleFormatter
from doge_auditor import DOGEAuditor
from firing_mechanism import FiringMechanism
from tariff_negotiator import TariffNegotiator
from orchestrator import MAGAgentsOrchestrator, AgentState


def print_header(title):
    """Print section header."""
    print("\n" + "=" * 60)
    print(f"🇺🇸 {title}")
    print("=" * 60)


def demo_trump_style():
    """Demo Trump style formatting."""
    print_header("TRUMP STYLE MESSAGES")
    
    messages = [
        "The system is working well",
        "New task created",
        "Task completed successfully"
    ]
    
    for msg in messages:
        formatted = TrumpStyleFormatter.format(msg, intensity=1.0)
        print(f"\nOriginal: {msg}")
        print(f"Trump:    {formatted}")
    
    print("\n🔥 FIRING MESSAGE:")
    print(TrumpStyleFormatter.format_firing("commerce", "inefficiency"))
    
    print("\n🐕 DOGE REPORT:")
    print(TrumpStyleFormatter.format_doge_report(247.32, 3))
    
    print("\n✅ APPROVAL:")
    print(TrumpStyleFormatter.format_approval("defense", "Security Bill"))
    
    print("\n❌ VETO:")
    print(TrumpStyleFormatter.format_veto("Budget Bill", "Too expensive"))


def demo_doge():
    """Demo DOGE auditing."""
    print_header("DOGE EFFICIENCY AUDITS")
    
    doge = DOGEAuditor()
    
    # Simulate good agent
    print("\n📊 Recording good agent performance...")
    for i in range(5):
        doge.record_task_completion(
            "defense", tokens=2000, cost=0.02, 
            response_time=60, success=True
        )
    
    # Simulate bad agent
    print("📊 Recording poor agent performance...")
    for i in range(10):
        doge.record_task_completion(
            "commerce", tokens=8000, cost=0.08,
            response_time=400, success=False
        )
    
    # Show leaderboard
    print("\n🏆 AGENT LEADERBOARD:")
    for perf in doge.get_leaderboard():
        status = "🔥" if perf.efficiency_score < 30 else "⚠️" if perf.efficiency_score < 60 else "✅"
        print(f"   {status} {perf.agent_id}: {perf.efficiency_score:.1f}% efficiency")
    
    # Show firing recommendations
    print("\n🚫 FIRING RECOMMENDATIONS:")
    recommendations = doge.get_firing_recommendations()
    if recommendations:
        for agent in recommendations:
            print(f"   • Fire {agent}!")
    else:
        print("   • No agents to fire")
    
    # Generate report
    print("\n📋 DAILY WASTE REPORT:")
    report = doge.generate_daily_report()
    print(f"   • Waste Found: ${report.total_waste:.2f}")
    print(f"   • Agents Fired: {report.agents_fired}")
    print(f"   • Agents Warned: {report.agents_warned}")


def demo_firing():
    """Demo firing mechanism."""
    print_header("'YOU'RE FIRED!' MECHANISM")
    
    firing = FiringMechanism()
    
    # Fire an agent
    print("\n🔥 FIRING AGENT...")
    cert = firing.fire_agent(
        agent_id="commerce",
        reason="INEFFICIENCY",
        fired_by="trump_president",
        efficiency_score=23.5,
        violations=["slow_response", "excessive_tokens", "task_failures"]
    )
    
    print(f"   Agent: {cert.agent_name}")
    print(f"   Reason: {cert.reason}")
    print(f"   Message: {cert.message}")
    print(f"   Certificate ID: {cert.certificate_id}")
    
    # Check unemployment
    print("\n📋 UNEMPLOYED AGENTS:")
    unemployed = firing.get_unemployed_agents()
    for agent in unemployed:
        print(f"   • {agent['agent_id']}: {agent['hours_remaining']:.1f}h remaining")
    
    # Show stats
    print("\n📊 FIRING STATS:")
    stats = firing.get_firing_stats()
    print(f"   • Total Fired: {stats['total_fired']}")
    print(f"   • Currently Unemployed: {stats['currently_unemployed']}")


def demo_tariffs():
    """Demo tariff negotiation."""
    print_header("TARIFF-BASED NEGOTIATION")
    
    negotiator = TariffNegotiator()
    
    # Create offers
    print("\n💰 CREATING TRADE OFFERS:")
    
    offer1 = negotiator.create_offer(
        "treasury", "defense", "tokens", 5000.0
    )
    print(f"   • {offer1.from_agent} → {offer1.to_agent}")
    print(f"     Amount: {offer1.amount} tokens")
    print(f"     Tariff: {offer1.tariff_rate*100:.0f}%")
    print(f"     Total: {offer1.total_cost:.0f} tokens")
    
    # Accept offer
    print("\n✅ ACCEPTING OFFER...")
    result = negotiator.respond_to_offer(offer1.offer_id, "accept")
    print(f"   Status: {result.status.value}")
    
    # Trade summary
    print("\n📊 TRADE SUMMARY:")
    summary = negotiator.get_trade_summary()
    print(f"   • Total Trades: {summary['total_trades']}")
    print(f"   • Accepted: {summary['accepted']}")
    print(f"   • Total Volume: {summary['total_volume']:.0f} tokens")
    print(f"   • Tariffs Collected: {summary['total_tariffs_collected']:.0f} tokens")
    
    # Trade war simulation
    print("\n🔥 TRADE WAR SIMULATION:")
    war_log = negotiator.simulate_trade_war("treasury", "commerce")
    for line in war_log[:5]:
        print(f"   {line}")


def demo_orchestrator():
    """Demo main orchestrator."""
    print_header("MAGAgents ORCHESTRATOR")
    
    orch = MAGAgentsOrchestrator()
    
    # Create task
    print("\n📋 CREATING TASK...")
    task = orch.create_task(
        title="Build Border Wall API",
        description="Create secure API endpoint",
        priority="critical"
    )
    print(f"   Task ID: {task.id}")
    print(f"   Title: {task.title}")
    print(f"   State: {task.state.value}")
    
    # Move through government
    print("\n🏛️ MOVING THROUGH GOVERNMENT...")
    
    orch.transition_state(task.id, AgentState.CONGRESS)
    print(f"   → Congress review")
    
    orch.transition_state(task.id, AgentState.POTUS)
    print(f"   → Presidential review")
    
    orch.approve_task(task.id)
    print(f"   → Presidential APPROVAL ✓")
    
    # Record progress
    print("\n📊 RECORDING PROGRESS...")
    orch.record_task_progress(
        task.id, "defense", tokens=3000, cost=0.03,
        success=True, response_time=90.0
    )
    print(f"   • Defense: 3000 tokens used")
    
    # Complete task
    print("\n✅ COMPLETING TASK...")
    orch.transition_state(task.id, AgentState.DONE)
    task = orch.get_task(task.id)
    print(f"   Final state: {task.state.value}")
    print(f"   Total tokens: {task.tokens_used}")
    
    # Show Truth Social feed
    print("\n📱 TRUTH SOCIAL FEED:")
    feed = orch.get_truth_social_feed(limit=5)
    for post in feed:
        print(f"   @{post['agent_id']}: {post['message'][:60]}...")
    
    # System summary
    print("\n📊 SYSTEM SUMMARY:")
    summary = orch.get_system_summary()
    print(f"   • Total Tasks: {summary['total_tasks']}")
    print(f"   • Truth Social Posts: {summary['truth_social_posts']}")
    print(f"   • Avg Efficiency: {summary['doge_summary']['avg_efficiency']:.1f}%")

    # LLM status & real usage (proof of real-model mode)
    u = summary.get("llm_usage", {})
    total_tok = u.get('input_tokens', 0) + u.get('output_tokens', 0)
    if summary.get("llm_enabled") and total_tok > 0:
        print(f"   • 🤖 LLM: ON (real models)")
        print(f"   • Tokens used: {u.get('input_tokens', 0)} in / "
              f"{u.get('output_tokens', 0)} out")
        print(f"   • LLM cost: ${u.get('cost', 0):.5f}")
    elif summary.get("llm_enabled"):
        print(f"   • 🤖 LLM: ON but 0 tokens — calls fell back to templates "
              f"(check API key / network)")
    else:
        print(f"   • 🤖 LLM: OFF (offline template mode)")


def demo_agentic():
    """Demo P3: agents make the REAL decisions and execute the task."""
    print_header("AGENTIC GOVERNMENT (real decisions)")

    import tempfile
    # Fresh, isolated data dir so this showcase isn't affected by earlier
    # demo sections' persisted DOGE history.
    orch = MAGAgentsOrchestrator(data_dir=Path(tempfile.mkdtemp()))
    if not orch.llm_enabled:
        print("\n🤖 LLM is OFF — running in offline auto-approve mode.")
        print("   Set an API key in .env to see real Congress/POTUS/Cabinet decisions.")

    task = orch.create_task(
        title="Draft a one-paragraph press release announcing a new trade deal",
        description="Audience: the American public. Keep it punchy.",
        priority="high",
    )
    print(f"\n📋 Task: {task.title}")
    print("\n🏛️ Running full government flow (Congress → POTUS → Cabinet → DOGE)...")

    result = orch.run_task_agentic(task.id)

    print(f"\n🧭 DECISION TRACE:")
    for step in result.get("trace", []):
        stage = step.get("stage", "?").upper()
        agent = step.get("agent", "?")
        verdict = step.get("vote") or step.get("decision") or step.get("ruling") \
            or step.get("verdict") or step.get("output_preview", "")
        print(f"   • [{stage}] @{agent}: {str(verdict)[:80]}")

    print(f"\n🏁 OUTCOME: {result.get('outcome', '?').upper()}")
    if result.get("output"):
        print(f"\n📄 CABINET DELIVERABLE:\n   {result['output'][:400]}")

    u = orch.llm_usage
    print(f"\n💸 LLM usage this run: {u['input_tokens']}+{u['output_tokens']} tokens, "
          f"${u['cost']:.5f}")


def main():
    """Run all demos."""
    print("\n" + "🎩" * 30)
    print("     MAGAgents - FULL DEMO")
    print("🎩" * 30)

    demo_trump_style()
    demo_doge()
    demo_firing()
    demo_tariffs()
    demo_orchestrator()
    demo_agentic()
    
    print("\n" + "=" * 60)
    print("🇺🇸 DEMO COMPLETE!")
    print("=" * 60)
    print("\nMake AI Agents Great Again! #MAGA")
    print()


if __name__ == "__main__":
    main()
