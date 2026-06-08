"""Unified LLM client with per-agent model routing and graceful degradation."""

import os
from typing import Optional, List, Dict

from .config import LLMConfig, AgentModel
from .providers import build_provider, BaseProvider, ChatResult, ProviderError

__all__ = ["LLMClient", "ChatResult", "LLMUnavailable"]


class LLMUnavailable(RuntimeError):
    """Raised when an LLM call is attempted but no working backend is available."""


class LLMClient:
    """Routes each agent to its configured provider/model.

    `enabled` is False when:
      - MAGAGENTS_LLM_ENABLED=off, or
      - mode is auto and no configured provider has its API key set in env.
    Callers should check `enabled` and fall back to template mode when False.
    """

    def __init__(self, config: LLMConfig, provider_factory=build_provider):
        self.config = config
        self._factory = provider_factory
        self._cache: Dict[str, BaseProvider] = {}

    # ---- availability ---------------------------------------------------
    def _provider_has_key(self, provider_name: str) -> bool:
        pb = (self.config.raw.get("providers") or {}).get(provider_name, {})
        env = pb.get("api_key_env", "")
        return bool(env and os.environ.get(env))

    @property
    def enabled(self) -> bool:
        mode = self.config.enabled_mode
        if mode == "off":
            return False
        any_key = any(self._provider_has_key(p) for p in self.config.provider_names())
        if mode == "on":
            return True  # caller explicitly wants LLM; errors surface on use
        return any_key  # auto

    # ---- core call ------------------------------------------------------
    def _get_provider(self, am: AgentModel) -> BaseProvider:
        if am.provider in self._cache:
            return self._cache[am.provider]
        api_key = os.environ.get(am.api_key_env, "")
        if not api_key:
            raise LLMUnavailable(
                f"no API key for provider '{am.provider}' (set {am.api_key_env})"
            )
        try:
            prov = self._factory(am.provider_type, api_key, am.base_url)
        except ProviderError as e:
            raise LLMUnavailable(str(e)) from e
        self._cache[am.provider] = prov
        return prov

    def chat_as(self, agent_id: str, system: str, user: str,
                history: Optional[List[Dict]] = None, **overrides) -> ChatResult:
        """Run a single chat turn as `agent_id`. Retries once on provider error."""
        am = self.config.resolve_agent(agent_id)
        provider = self._get_provider(am)
        messages = list(history or [])
        messages.append({"role": "user", "content": user})

        temperature = overrides.get("temperature", am.temperature)
        max_tokens = overrides.get("max_tokens", am.max_tokens)
        model = overrides.get("model", am.model)

        last_err = None
        for _attempt in range(2):
            try:
                return provider.chat(system, messages, model=model,
                                     temperature=temperature, max_tokens=max_tokens)
            except ProviderError as e:
                last_err = e
        raise LLMUnavailable(f"chat_as({agent_id}) failed: {last_err}")

    # ---- cost accounting ------------------------------------------------
    def cost_of(self, agent_id: str, input_tokens: int, output_tokens: int) -> float:
        am = self.config.resolve_agent(agent_id)
        price = am.price_per_1k or {}
        return (input_tokens / 1000.0) * float(price.get("input", 0.0)) \
            + (output_tokens / 1000.0) * float(price.get("output", 0.0))
