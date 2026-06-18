"""Unit tests for provider-agnostic advisor collection clients."""

import pytest
from scripts.collect_advisor_runs import cache_path, model_label, prompt_hash, safe_slug

from arenawealth.experiments.llm_clients import (
    AnthropicMessagesClient,
    AzureOpenAIClient,
    OpenAIChatClient,
    _anthropic_text,
    build_llm_client,
)


def test_azure_client_uses_deployment_from_environment(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "chat")

    client = AzureOpenAIClient.from_env()

    assert client.provider == "azure"
    assert client.model == "chat"
    assert client.api_version


def test_openai_client_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        OpenAIChatClient.from_env("gpt-4o")


def test_anthropic_client_keeps_model_and_version(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")
    monkeypatch.setenv("ANTHROPIC_VERSION", "2023-06-01")

    client = AnthropicMessagesClient.from_env()

    assert client.provider == "anthropic"
    assert client.model == "claude-test"
    assert client.api_version == "2023-06-01"


def test_build_llm_client_rejects_unknown_provider():
    with pytest.raises(ValueError, match="unsupported LLM provider"):
        build_llm_client("local")


def test_anthropic_text_extracts_text_blocks():
    body = {
        "content": [
            {"type": "text", "text": '{"tickers":["MA"]}'},
            {"type": "tool_use", "name": "ignored"},
        ]
    }

    assert _anthropic_text(body) == '{"tickers":["MA"]}'


def test_cache_path_separates_provider_and_model(tmp_path):
    path = cache_path("azure", "chat/test", "quality additions", 2, tmp_path)

    assert path == tmp_path / "azure" / "chat_test" / "quality_additions__run2.json"


def test_model_label_defaults_from_provider_env(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "chat")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test")

    assert model_label("azure", None) == "chat"
    assert model_label("openai", None) == "gpt-test"
    assert model_label("anthropic", None) == "claude-test"
    assert safe_slug("model / x") == "model_x"


def test_model_label_uses_current_final_defaults(monkeypatch):
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)

    assert model_label("openai", None) == "gpt-5.5"
    assert model_label("anthropic", None) == "claude-opus-4-8"


def test_prompt_hash_changes_when_prompt_changes():
    assert prompt_hash("prompt v1") != prompt_hash("prompt v2")
    assert prompt_hash("prompt v1") == prompt_hash("prompt v1")
