#!/usr/bin/env python3
"""
MAGAgents - Comprehensive Test Suite
Tests all core functionality
"""

import sys
import json
import time
import unittest
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trump_style import TrumpStyleFormatter, TruthSocialAPI
from doge_auditor import DOGEAuditor, AgentPerformance
from firing_mechanism import FiringMechanism, FiringCertificate
from tariff_negotiator import TariffNegotiator, TradeOffer
from orchestrator import MAGAgentsOrchestrator, AgentState


class TestTrumpStyleFormatter(unittest.TestCase):
    """Test Trump style message formatting."""
    
    def test_format_adds_keywords(self):
        """Test that formatting adds Trump keywords."""
        message = "The system is working"
        formatted = TrumpStyleFormatter.format(message, intensity=1.0)
        
        # Should contain at least one Trump keyword
        trump_words = ["TREMENDOUS", "HUGE", "BEST", "SAD", "FAKE NEWS"]
        has_trump_word = any(word in formatted for word in trump_words)
        self.assertTrue(has_trump_word or "!!!" in formatted)
    
    def test_format_firing(self):
        """Test firing message format."""
        message = TrumpStyleFormatter.format_firing("test_agent", "inefficiency")
        
        self.assertIn("test_agent", message)
        self.assertIn("FIRED", message.upper())
        self.assertIn("!!!", message)
    
    def test_format_doge_report(self):
        """Test DOGE report format."""
        message = TrumpStyleFormatter.format_doge_report(123.45, 3)
        
        self.assertIn("123.45", message)
        self.assertIn("3", message)
        self.assertIn("DOGE", message)
    
    def test_truth_social_api(self):
        """Test Truth Social API."""
        api = TruthSocialAPI()
        
        post = api.post("trump_president", "Test message", trump_style=True)
        
        self.assertEqual(post["agent_id"], "trump_president")
        self.assertIn("id", post)
        self.assertEqual(len(api.posts), 1)


class TestDOGEAuditor(unittest.TestCase):
    """Test DOGE efficiency auditor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        self.doge = DOGEAuditor(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_record_task_completion(self):
        """Test recording task completion."""
        self.doge.record_task_completion(
            agent_id="test_agent",
            tokens=1000,
            cost=0.01,
            response_time=60.0,
            success=True
        )
        
        self.assertIn("test_agent", self.doge.agent_history)
        perf = self.doge.agent_history["test_agent"]
        self.assertEqual(perf.tasks_completed, 1)
        self.assertEqual(perf.total_tokens, 1000)
    
    def test_efficiency_calculation(self):
        """Test efficiency score calculation."""
        # Record multiple tasks
        for i in range(5):
            self.doge.record_task_completion(
                agent_id="efficient_agent",
                tokens=1000,
                cost=0.01,
                response_time=60.0,
                success=True
            )
        
        perf = self.doge.agent_history["efficient_agent"]
        self.assertGreater(perf.efficiency_score, 80)
    
    def test_firing_recommendations(self):
        """Test firing recommendations."""
        # Create underperforming agent
        for i in range(10):
            self.doge.record_task_completion(
                agent_id="bad_agent",
                tokens=10000,  # Excessive tokens
                cost=0.1,
                response_time=500.0,  # Too slow
                success=False  # Failed
            )
        
        recommendations = self.doge.get_firing_recommendations()
        self.assertIn("bad_agent", recommendations)
    
    def test_daily_report(self):
        """Test daily report generation."""
        # Add some data
        self.doge.record_task_completion("agent1", 1000, 0.01, 60, True)
        self.doge.record_task_completion("agent2", 500, 0.005, 45, True)
        
        report = self.doge.generate_daily_report()
        
        self.assertIsNotNone(report.date)
        self.assertIsInstance(report.total_waste, float)


class TestFiringMechanism(unittest.TestCase):
    """Test firing mechanism."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_firing_data"
        self.test_dir.mkdir(exist_ok=True)
        self.firing = FiringMechanism(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_fire_agent(self):
        """Test firing an agent."""
        cert = self.firing.fire_agent(
            agent_id="test_agent",
            reason="INEFFICIENCY",
            fired_by="trump_president",
            efficiency_score=25.0,
            violations=["slow_response", "excessive_tokens"]
        )
        
        self.assertIsNotNone(cert)
        self.assertEqual(cert.agent_id, "test_agent")
        self.assertEqual(cert.reason, "INEFFICIENCY")
        self.assertTrue(self.firing.is_agent_fired("test_agent"))
    
    def test_cannot_rehire_immediately(self):
        """Test that fired agents can't be rehired immediately."""
        self.firing.fire_agent("test_agent", "test")
        
        # Should not be able to rehire immediately
        self.assertFalse(self.firing.can_rehire("test_agent"))
    
    def test_firing_stats(self):
        """Test firing statistics."""
        self.firing.fire_agent("agent1", "test1")
        self.firing.fire_agent("agent2", "test2")
        
        stats = self.firing.get_firing_stats()
        
        self.assertEqual(stats["total_fired"], 2)
        self.assertEqual(stats["currently_unemployed"], 2)


class TestTariffNegotiator(unittest.TestCase):
    """Test tariff negotiation system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.negotiator = TariffNegotiator()
    
    def test_create_offer(self):
        """Test creating trade offer."""
        offer = self.negotiator.create_offer(
            from_agent="agent1",
            to_agent="agent2",
            resource_type="tokens",
            amount=1000.0
        )
        
        self.assertEqual(offer.from_agent, "agent1")
        self.assertEqual(offer.to_agent, "agent2")
        self.assertEqual(offer.amount, 1000.0)
        self.assertGreater(offer.tariff_rate, 0)
        self.assertGreater(offer.total_cost, offer.amount)
    
    def test_accept_offer(self):
        """Test accepting trade offer."""
        offer = self.negotiator.create_offer(
            "agent1", "agent2", "tokens", 1000.0
        )
        
        result = self.negotiator.respond_to_offer(offer.offer_id, "accept")
        
        self.assertEqual(result.status.value, "accepted")
    
    def test_reject_offer(self):
        """Test rejecting trade offer."""
        offer = self.negotiator.create_offer(
            "agent1", "agent2", "tokens", 1000.0
        )
        
        result = self.negotiator.respond_to_offer(offer.offer_id, "reject")
        
        self.assertEqual(result.status.value, "rejected")
    
    def test_counter_offer(self):
        """Test counter offer."""
        offer = self.negotiator.create_offer(
            "agent1", "agent2", "tokens", 1000.0
        )
        
        result = self.negotiator.respond_to_offer(
            offer.offer_id, "counter", counter_tariff=0.05
        )
        
        self.assertEqual(result.status.value, "countered")
        self.assertEqual(result.tariff_rate, 0.05)
    
    def test_trade_summary(self):
        """Test trade summary."""
        # Create and accept some trades
        for i in range(3):
            offer = self.negotiator.create_offer(
                "agent1", "agent2", "tokens", 1000.0
            )
            self.negotiator.respond_to_offer(offer.offer_id, "accept")
        
        summary = self.negotiator.get_trade_summary()
        
        self.assertEqual(summary["total_trades"], 3)
        self.assertEqual(summary["accepted"], 3)


class TestOrchestrator(unittest.TestCase):
    """Test main orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_orchestrator_data"
        self.test_dir.mkdir(exist_ok=True)
        self.orch = MAGAgentsOrchestrator(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_create_task(self):
        """Test task creation."""
        task = self.orch.create_task(
            title="Test Task",
            description="Test Description",
            priority="high"
        )
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.state, AgentState.PENDING)
        self.assertEqual(task.priority, "high")
    
    def test_state_transition(self):
        """Test state transition."""
        task = self.orch.create_task("Test")
        
        result = self.orch.transition_state(task.id, AgentState.CONGRESS)
        
        self.assertTrue(result)
        self.assertEqual(self.orch.get_task(task.id).state, AgentState.CONGRESS)
    
    def test_invalid_transition(self):
        """Test invalid state transition."""
        task = self.orch.create_task("Test")
        
        # Can't go from PENDING to DONE directly
        result = self.orch.transition_state(task.id, AgentState.DONE)
        
        self.assertFalse(result)
    
    def test_fire_agent(self):
        """Test agent firing through orchestrator."""
        # First add some bad performance
        for i in range(10):
            self.orch.doge.record_task_completion(
                "bad_agent", 10000, 0.1, 500, False
            )
        
        cert = self.orch.fire_agent("bad_agent", "Poor performance")
        
        self.assertIsNotNone(cert)
        self.assertTrue(self.orch.firing.is_agent_fired("bad_agent"))
    
    def test_veto_task(self):
        """Test task veto."""
        task = self.orch.create_task("Test Bill")
        self.orch.transition_state(task.id, AgentState.CONGRESS)
        self.orch.transition_state(task.id, AgentState.POTUS)
        
        result = self.orch.veto_task(task.id, "Too expensive")
        
        self.assertTrue(result)
        self.assertEqual(self.orch.get_task(task.id).state, AgentState.VETOED)
    
    def test_approve_task(self):
        """Test task approval."""
        task = self.orch.create_task("Test Bill")
        self.orch.transition_state(task.id, AgentState.CONGRESS)
        self.orch.transition_state(task.id, AgentState.POTUS)
        
        result = self.orch.approve_task(task.id)
        
        self.assertTrue(result)
        self.assertEqual(self.orch.get_task(task.id).state, AgentState.CABINET)
    
    def test_system_summary(self):
        """Test system summary."""
        # Create some tasks
        for i in range(3):
            self.orch.create_task(f"Task {i}")
        
        summary = self.orch.get_system_summary()
        
        self.assertEqual(summary["total_tasks"], 3)
        self.assertIn("doge_summary", summary)
        self.assertIn("firing_stats", summary)


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent / "test_integration_data"
        self.test_dir.mkdir(exist_ok=True)
        self.orch = MAGAgentsOrchestrator(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete workflow from creation to completion."""
        # 1. Create task
        task = self.orch.create_task("Build API", "Create REST API")
        self.assertEqual(task.state, AgentState.PENDING)
        
        # 2. Move to Congress
        self.orch.transition_state(task.id, AgentState.CONGRESS)
        task = self.orch.get_task(task.id)
        self.assertEqual(task.state, AgentState.CONGRESS)
        
        # 3. Move to POTUS
        self.orch.transition_state(task.id, AgentState.POTUS)
        task = self.orch.get_task(task.id)
        self.assertEqual(task.state, AgentState.POTUS)
        
        # 4. POTUS approves
        self.orch.approve_task(task.id)
        task = self.orch.get_task(task.id)
        self.assertEqual(task.state, AgentState.CABINET)
        
        # 5. Record some progress
        self.orch.record_task_progress(
            task.id, "defense", 1000, 0.01, True, 60.0
        )
        
        # 6. Complete task
        self.orch.transition_state(task.id, AgentState.DOING)
        self.orch.transition_state(task.id, AgentState.DONE)
        task = self.orch.get_task(task.id)
        self.assertEqual(task.state, AgentState.DONE)
        self.assertEqual(task.tokens_used, 1000)
    
    def test_firing_workflow(self):
        """Test agent firing workflow."""
        # Create underperforming agent
        for i in range(15):
            self.orch.doge.record_task_completion(
                "underperformer",
                tokens=8000,
                cost=0.08,
                response_time=400.0,
                success=False
            )
        
        # Verify agent is flagged for firing
        recommendations = self.orch.doge.get_firing_recommendations()
        self.assertIn("underperformer", recommendations)
        
        # Fire the agent
        cert = self.orch.fire_agent("underperformer", "INEFFICIENCY")
        self.assertIsNotNone(cert)
        
        # Verify firing
        self.assertTrue(self.orch.firing.is_agent_fired("underperformer"))
        
        # Check Truth Social posts
        trump_posts = [p for p in self.orch.truth_social.posts 
                      if p["agent_id"] == "trump_president"]
        self.assertGreater(len(trump_posts), 0)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTrumpStyleFormatter))
    suite.addTests(loader.loadTestsFromTestCase(TestDOGEAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestFiringMechanism))
    suite.addTests(loader.loadTestsFromTestCase(TestTariffNegotiator))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
