"""MAGAgents LLM integration layer (pluggable, optional).

Public API:
    from llm import LLMClient, load_config
    client = LLMClient(load_config())
    if client.enabled:
        result = client.chat_as("trump_president", system="...", user="...")
"""

from .config import load_config, LLMConfig
from .client import LLMClient, ChatResult, LLMUnavailable

__all__ = [
    "load_config",
    "LLMConfig",
    "LLMClient",
    "ChatResult",
    "LLMUnavailable",
]
