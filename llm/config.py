"""Load and resolve MAGAgents LLM model configuration.

Degrades gracefully:
- If PyYAML isn't installed or config/models.yaml is missing, a built-in
  default config is used (with `enabled` effectively driven by env keys).
- Per-agent resolution merges (low->high): default < agents.<id> < env overrides.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "models.yaml"
ENV_PATH = PROJECT_ROOT / ".env"


def load_dotenv_if_present(path: Path = ENV_PATH) -> None:
    """Zero-dependency .env loader. Existing env vars take precedence."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val

# Built-in fallback so the layer works even without a yaml file / PyYAML.
_BUILTIN = {
    "enabled": "auto",
    "default": {"provider": "deepseek", "model": "deepseek-chat",
                "temperature": 0.8, "max_tokens": 1024},
    "providers": {
        "deepseek": {"type": "openai_compat", "base_url": "https://api.deepseek.com",
                     "api_key_env": "DEEPSEEK_API_KEY",
                     "price_per_1k": {"input": 0.00014, "output": 0.00028}},
        "anthropic": {"type": "anthropic", "api_key_env": "ANTHROPIC_API_KEY",
                      "price_per_1k": {"input": 0.003, "output": 0.015}},
    },
    "agents": {},
}


@dataclass
class AgentModel:
    """Fully resolved model settings for one agent."""
    agent_id: str
    provider: str
    model: str
    temperature: float = 0.8
    max_tokens: int = 1024
    # provider-level info
    provider_type: str = "openai_compat"
    base_url: Optional[str] = None
    api_key_env: str = ""
    price_per_1k: dict = field(default_factory=lambda: {"input": 0.0, "output": 0.0})


@dataclass
class LLMConfig:
    raw: dict
    enabled_mode: str  # auto | on | off

    def _provider_block(self, name: str) -> dict:
        return (self.raw.get("providers") or {}).get(name, {})

    def resolve_agent(self, agent_id: str) -> AgentModel:
        """Merge default < agents.<id> < env overrides into an AgentModel."""
        base = dict(self.raw.get("default") or {})
        base.update((self.raw.get("agents") or {}).get(agent_id, {}))

        env_key = agent_id.upper()
        provider = os.environ.get(f"MAGAGENTS_AGENT_{env_key}_PROVIDER", base.get("provider", "deepseek"))
        model = os.environ.get(f"MAGAGENTS_AGENT_{env_key}_MODEL", base.get("model", "deepseek-chat"))

        pb = self._provider_block(provider)
        return AgentModel(
            agent_id=agent_id,
            provider=provider,
            model=model,
            temperature=float(base.get("temperature", 0.8)),
            max_tokens=int(base.get("max_tokens", 1024)),
            provider_type=pb.get("type", "openai_compat"),
            base_url=pb.get("base_url"),
            api_key_env=pb.get("api_key_env", ""),
            price_per_1k=pb.get("price_per_1k") or {"input": 0.0, "output": 0.0},
        )

    def provider_names(self) -> list:
        return list((self.raw.get("providers") or {}).keys())


def load_config(path: Path = CONFIG_PATH) -> LLMConfig:
    """Load models.yaml (or built-in fallback).

    Note: this does NOT read .env (keeps config pure for tests). App entry
    points call `load_dotenv_if_present()` explicitly before constructing a client.
    """
    raw = None
    try:
        import yaml  # type: ignore
        if path.exists():
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        raw = None
    if not raw:
        raw = dict(_BUILTIN)

    enabled_mode = os.environ.get("MAGAGENTS_LLM_ENABLED", raw.get("enabled", "auto")).lower()
    if enabled_mode not in ("auto", "on", "off"):
        enabled_mode = "auto"
    return LLMConfig(raw=raw, enabled_mode=enabled_mode)
