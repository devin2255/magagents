#!/usr/bin/env python3
"""Tests for the optional LLM integration layer.

These run fully offline using a fake provider/factory — no API keys, no network.
They verify: config resolution, per-agent routing, cost accounting, graceful
degradation, and that the orchestrator still works (template mode) with LLM off.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm.config import load_config
from llm.client import LLMClient, LLMUnavailable
from llm.providers import ChatResult
from llm import agent_runtime


class FakeProvider:
    """Records calls and returns canned text + token usage."""
    def __init__(self, *args, **kwargs):
        self.calls = []

    def chat(self, system, messages, *, model, temperature, max_tokens):
        self.calls.append({"system": system, "messages": messages, "model": model})
        return ChatResult(text=f"[{model}] in character!", input_tokens=11, output_tokens=7)


def fake_factory(provider_type, api_key, base_url=None):
    return FakeProvider(provider_type, api_key, base_url)


class TestConfig(unittest.TestCase):
    def test_resolve_default_and_override(self):
        cfg = load_config()
        am = cfg.resolve_agent("state_dept")  # not listed -> default
        self.assertEqual(am.provider, "deepseek")
        self.assertEqual(am.model, "deepseek-chat")
        # listed agent keeps its own temperature
        trump = cfg.resolve_agent("trump_president")
        self.assertEqual(trump.temperature, 1.0)

    def test_env_override(self):
        os.environ["MAGAGENTS_AGENT_DOGE_MUSK_MODEL"] = "qwen-max"
        os.environ["MAGAGENTS_AGENT_DOGE_MUSK_PROVIDER"] = "qwen"
        try:
            cfg = load_config()
            am = cfg.resolve_agent("doge_musk")
            self.assertEqual(am.provider, "qwen")
            self.assertEqual(am.model, "qwen-max")
        finally:
            del os.environ["MAGAGENTS_AGENT_DOGE_MUSK_MODEL"]
            del os.environ["MAGAGENTS_AGENT_DOGE_MUSK_PROVIDER"]


class TestEnabled(unittest.TestCase):
    def test_disabled_when_off(self):
        os.environ["MAGAGENTS_LLM_ENABLED"] = "off"
        try:
            client = LLMClient(load_config(), provider_factory=fake_factory)
            self.assertFalse(client.enabled)
        finally:
            del os.environ["MAGAGENTS_LLM_ENABLED"]

    def test_enabled_when_key_present(self):
        os.environ["MAGAGENTS_LLM_ENABLED"] = "auto"
        os.environ["DEEPSEEK_API_KEY"] = "sk-test"
        try:
            client = LLMClient(load_config(), provider_factory=fake_factory)
            self.assertTrue(client.enabled)
        finally:
            del os.environ["MAGAGENTS_LLM_ENABLED"]
            del os.environ["DEEPSEEK_API_KEY"]


class TestChatAndCost(unittest.TestCase):
    def setUp(self):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test"
        self.client = LLMClient(load_config(), provider_factory=fake_factory)

    def tearDown(self):
        os.environ.pop("DEEPSEEK_API_KEY", None)

    def test_chat_as_routes_to_model(self):
        res = self.client.chat_as("state_dept", system="sys", user="hi")
        self.assertIn("deepseek-chat", res.text)
        self.assertEqual(res.input_tokens, 11)

    def test_cost_accounting(self):
        cost = self.client.cost_of("state_dept", 1000, 1000)
        # deepseek price 0.00014 in + 0.00028 out per 1k
        self.assertAlmostEqual(cost, 0.00014 + 0.00028, places=6)

    def test_missing_key_raises(self):
        os.environ.pop("DEEPSEEK_API_KEY", None)
        client = LLMClient(load_config(), provider_factory=fake_factory)
        with self.assertRaises(LLMUnavailable):
            client.chat_as("state_dept", system="s", user="u")


class TestAgentRuntime(unittest.TestCase):
    def test_say_returns_text_and_tokens(self):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test"
        try:
            client = LLMClient(load_config(), provider_factory=fake_factory)
            text, in_tok, out_tok = agent_runtime.say(client, "trump_president", "win bigly")
            self.assertIsNotNone(text)
            self.assertEqual((in_tok, out_tok), (11, 7))
        finally:
            os.environ.pop("DEEPSEEK_API_KEY", None)

    def test_say_disabled_returns_none(self):
        os.environ["MAGAGENTS_LLM_ENABLED"] = "off"
        try:
            client = LLMClient(load_config(), provider_factory=fake_factory)
            text, in_tok, out_tok = agent_runtime.say(client, "trump_president", "x")
            self.assertIsNone(text)
            self.assertEqual((in_tok, out_tok), (0, 0))
        finally:
            del os.environ["MAGAGENTS_LLM_ENABLED"]

    def test_soul_loaded_as_system_prompt(self):
        soul = agent_runtime.load_soul("doge_musk")
        self.assertIn("DOGE", soul)
        self.assertIn("SECURITY", soul)  # guardrail appended


class TestOrchestratorFallback(unittest.TestCase):
    """With LLM off, orchestrator must behave exactly as before (template mode)."""
    def test_orchestrator_runs_without_llm(self):
        os.environ["MAGAGENTS_LLM_ENABLED"] = "off"
        try:
            import importlib, orchestrator
            importlib.reload(orchestrator)
            import tempfile
            orch = orchestrator.MAGAgentsOrchestrator(data_dir=Path(tempfile.mkdtemp()))
            self.assertFalse(orch.llm_enabled)
            task = orch.create_task("Test", "desc", "high")
            self.assertIsNotNone(task.id)
            self.assertTrue(len(orch.truth_social.posts) >= 1)
        finally:
            del os.environ["MAGAGENTS_LLM_ENABLED"]


class TestAgenticFlow(unittest.TestCase):
    """P3: run_task_agentic drives a task end-to-end with decisions."""

    def _orch(self):
        import importlib, orchestrator, tempfile
        importlib.reload(orchestrator)
        return orchestrator.MAGAgentsOrchestrator(data_dir=Path(tempfile.mkdtemp())), orchestrator

    def test_agentic_offline_completes(self):
        os.environ["MAGAGENTS_LLM_ENABLED"] = "off"
        try:
            orch, _ = self._orch()
            self.assertFalse(orch.llm_enabled)
            task = orch.create_task("Build API", "REST endpoint", "high")
            result = orch.run_task_agentic(task.id)
            self.assertEqual(result["outcome"], "done")        # offline auto-approves
            self.assertEqual(orch.get_task(task.id).state.name, "DONE")
            self.assertTrue(len(result["trace"]) >= 4)         # congress/potus/cabinet/doge
            self.assertTrue(orch.get_task(task.id).output)
        finally:
            del os.environ["MAGAGENTS_LLM_ENABLED"]

    def test_agentic_records_real_tokens_to_doge(self):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test"
        try:
            import importlib, orchestrator, tempfile
            importlib.reload(orchestrator)
            orch = orchestrator.MAGAgentsOrchestrator(data_dir=Path(tempfile.mkdtemp()))
            orch.llm = LLMClient(load_config(), provider_factory=fake_factory)  # inject fake
            self.assertTrue(orch.llm_enabled)
            task = orch.create_task("Build API", "desc", "high")
            orch.run_task_agentic(task.id)
            # FakeProvider reports 11+7 tokens per call -> usage must be > 0
            self.assertGreater(orch.llm_usage["input_tokens"], 0)
            self.assertGreater(len(orch.doge.agent_history), 0)  # DOGE saw real usage
            # Trace persisted on the task for the dashboard
            self.assertTrue(orch.get_task(task.id).decision_trace)
            self.assertTrue(orch.get_task(task.id).outcome)
        finally:
            os.environ.pop("DEEPSEEK_API_KEY", None)

    def test_budget_circuit_breaker_halts(self):
        os.environ["DEEPSEEK_API_KEY"] = "sk-test"
        try:
            import importlib, orchestrator, tempfile
            importlib.reload(orchestrator)
            orch = orchestrator.MAGAgentsOrchestrator(data_dir=Path(tempfile.mkdtemp()))
            orch.llm = LLMClient(load_config(), provider_factory=fake_factory)
            task = orch.create_task("Expensive task", "desc", "high")
            # Tiny cap -> first recorded usage already exceeds it -> DOGE halts.
            result = orch.run_task_agentic(task.id, max_cost=1e-12)
            self.assertEqual(result["outcome"], "over_budget")
            self.assertEqual(orch.get_task(task.id).outcome, "over_budget")
            self.assertIn("Over budget", orch.get_task(task.id).block)
        finally:
            os.environ.pop("DEEPSEEK_API_KEY", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
