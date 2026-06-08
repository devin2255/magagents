"""LLM provider adapters.

Two adapters cover every provider MAGAgents supports:
- OpenAICompatProvider: DeepSeek / Qwen / Kimi / OpenRouter / OpenAI / local (Ollama/vLLM)
- AnthropicProvider: Claude

SDKs are imported lazily so the core package has zero hard dependencies.
"""

from typing import NamedTuple, List, Dict, Optional


class ChatResult(NamedTuple):
    text: str
    input_tokens: int
    output_tokens: int


class ProviderError(RuntimeError):
    """Raised when a provider cannot be constructed or a call fails."""


class BaseProvider:
    def chat(self, system: str, messages: List[Dict], *, model: str,
             temperature: float, max_tokens: int) -> ChatResult:
        raise NotImplementedError


class OpenAICompatProvider(BaseProvider):
    """Any OpenAI-compatible Chat Completions endpoint."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as e:
            raise ProviderError("openai SDK not installed (pip install openai)") from e
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(self, system, messages, *, model, temperature, max_tokens) -> ChatResult:
        msgs = [{"role": "system", "content": system}] + messages
        try:
            resp = self._client.chat.completions.create(
                model=model, messages=msgs,
                temperature=temperature, max_tokens=max_tokens,
            )
        except Exception as e:
            raise ProviderError(f"openai_compat call failed: {e}") from e
        text = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        in_tok = getattr(usage, "prompt_tokens", 0) or 0
        out_tok = getattr(usage, "completion_tokens", 0) or 0
        return ChatResult(text=text, input_tokens=in_tok, output_tokens=out_tok)


class AnthropicProvider(BaseProvider):
    """Anthropic Messages API (Claude)."""

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        try:
            import anthropic  # type: ignore
        except ImportError as e:
            raise ProviderError("anthropic SDK not installed (pip install anthropic)") from e
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = anthropic.Anthropic(**kwargs)

    def chat(self, system, messages, *, model, temperature, max_tokens) -> ChatResult:
        try:
            resp = self._client.messages.create(
                model=model, system=system, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            )
        except Exception as e:
            raise ProviderError(f"anthropic call failed: {e}") from e
        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        ).strip()
        usage = getattr(resp, "usage", None)
        in_tok = getattr(usage, "input_tokens", 0) or 0
        out_tok = getattr(usage, "output_tokens", 0) or 0
        return ChatResult(text=text, input_tokens=in_tok, output_tokens=out_tok)


def build_provider(provider_type: str, api_key: str, base_url: Optional[str] = None) -> BaseProvider:
    if provider_type == "anthropic":
        return AnthropicProvider(api_key, base_url)
    if provider_type == "openai_compat":
        return OpenAICompatProvider(api_key, base_url)
    raise ProviderError(f"unknown provider type: {provider_type}")
