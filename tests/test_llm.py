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


if __name__ == "__main__":
    unittest.main(verbosity=2)
