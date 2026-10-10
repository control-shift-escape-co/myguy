"""Model construction — one place that knows about providers and the gateway."""

from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from agent.config import AgentConfig


def build_model(cfg: AgentConfig, **kwargs) -> BaseChatModel:
    """init_chat_model handles provider wiring; base_url reroutes to Kong when set."""
    args: dict = {"model_provider": cfg.model_provider, **kwargs}
    if cfg.llm_base_url:
        args["base_url"] = cfg.llm_base_url
        # Kong's /llm endpoint speaks the OpenAI wire format.
        args["model_provider"] = "openai"
    return init_chat_model(cfg.model_name, **args)
