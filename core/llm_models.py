"""
Centralized LLM provider and model definitions.
Single source of truth for all LLM model lists across the application.

When adding new models or providers, update this file ONLY.
All UI components and configuration will automatically use the updated lists.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LLMProvider:
    """Represents an LLM provider with available models and configuration."""
    id: str
    display_name: str
    models: List[str]
    enabled_by_default: bool = True
    requires_api_key: bool = True
    supports_cloud_auth: bool = False  # NEW: Cloud authentication support
    endpoint: Optional[str] = None
    prefix: str = ''  # LiteLLM prefix (e.g., 'gemini/', 'ollama/')


# Define all LLM providers and their models
# Models are ordered from newest/most capable to older/smaller
LLM_PROVIDERS = {
    'openai': LLMProvider(
        id='openai',
        display_name='OpenAI',
        models=[
            'gpt-5-chat-latest',    # NEWEST: GPT-5 (latest)
            'gpt-4o',
            'gpt-4.1',              # NEW: GPT-4.1
            'gpt-4.1-mini',         # NEW: GPT-4.1 Mini
            'gpt-4.1-nano',         # NEW: GPT-4.1 Nano
            'gpt-4o-mini',
            'gpt-4-turbo',
            'gpt-4',
            'gpt-3.5-turbo'
        ],
        enabled_by_default=True,
        requires_api_key=True,
        supports_cloud_auth=False,
        prefix=''  # No prefix for OpenAI
    ),

    'anthropic': LLMProvider(
        id='anthropic',
        display_name='Anthropic',
        models=[
            'claude-sonnet-4-5',    # NEWEST: Sonnet 4.5 (released Sept 2025)
            'claude-opus-4-1',      # NEW: Opus 4.1
            'claude-opus-4',
            'claude-sonnet-4',
            'claude-3-7-sonnet',
            'claude-3-5-sonnet',
            'claude-3-5-haiku',
            'claude-3-opus',
            'claude-3-sonnet',
            'claude-3-haiku'
        ],
        enabled_by_default=True,
        requires_api_key=True,
        supports_cloud_auth=False,
        prefix='anthropic/'  # LiteLLM requires anthropic/ prefix
    ),

    'gemini': LLMProvider(
        id='gemini',
        display_name='Google Gemini',
        models=[
            'gemini-2.5-pro',           # NEW: Gemini 2.5 Pro
            'gemini-2.5-flash',         # NEW: Gemini 2.5 Flash
            'gemini-2.5-flash-lite',    # NEW: Gemini 2.5 Flash Lite
            'gemini-2.0-flash-exp',
            'gemini-exp-1206',
            'gemini-2.0-flash',
            'gemini-2.0-pro',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.0-pro'
        ],
        enabled_by_default=True,
        requires_api_key=True,
        supports_cloud_auth=True,   # NEW: Supports Google Cloud auth
        prefix='gemini/'
    ),

    'ollama': LLMProvider(
        id='ollama',
        display_name='Ollama (Local)',
        models=[
            'llama3.2:latest',
            'llama3.1:8b',
            'llama3.1:70b',
            'mistral:7b',
            'mixtral:8x7b',
            'phi3:medium',
            'qwen2.5:72b',
            'deepseek-r1:70b'
        ],
        enabled_by_default=False,
        requires_api_key=False,
        supports_cloud_auth=False,
        endpoint='http://localhost:11434',
        prefix='ollama/'
    ),

    'lmstudio': LLMProvider(
        id='lmstudio',
        display_name='LM Studio (Local)',
        models=[
            'local-model',
            'custom-model'
        ],
        enabled_by_default=False,
        requires_api_key=False,
        supports_cloud_auth=False,
        endpoint='http://localhost:1234/v1',
        prefix='openai/'  # LM Studio uses OpenAI-compatible API
    )
}


# Helper functions for easy access

def get_provider_models(provider_id: str) -> List[str]:
    """
    Get model list for a provider.

    Args:
        provider_id: Provider identifier (e.g., 'openai', 'anthropic')

    Returns:
        List of model names for the provider
    """
    provider_id_lower = provider_id.lower()
    return LLM_PROVIDERS[provider_id_lower].models if provider_id_lower in LLM_PROVIDERS else []


def get_all_provider_ids() -> List[str]:
    """
    Get all provider IDs.

    Returns:
        List of provider identifiers
    """
    return list(LLM_PROVIDERS.keys())


def get_provider_display_name(provider_id: str) -> str:
    """
    Get display name for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        Human-readable display name
    """
    provider_id_lower = provider_id.lower()
    return LLM_PROVIDERS[provider_id_lower].display_name if provider_id_lower in LLM_PROVIDERS else provider_id


def get_provider_config(provider_id: str) -> Optional[LLMProvider]:
    """
    Get full provider configuration.

    Args:
        provider_id: Provider identifier

    Returns:
        LLMProvider object or None if not found
    """
    provider_id_lower = provider_id.lower()
    return LLM_PROVIDERS.get(provider_id_lower)


def get_provider_prefix(provider_id: str) -> str:
    """
    Get LiteLLM prefix for a provider.

    Args:
        provider_id: Provider identifier

    Returns:
        LiteLLM prefix string (e.g., 'gemini/', 'ollama/')
    """
    provider_id_lower = provider_id.lower()
    return LLM_PROVIDERS[provider_id_lower].prefix if provider_id_lower in LLM_PROVIDERS else ''


def get_enabled_providers() -> List[str]:
    """
    Get list of providers enabled by default.

    Returns:
        List of provider IDs that are enabled by default
    """
    return [pid for pid, provider in LLM_PROVIDERS.items() if provider.enabled_by_default]


def supports_cloud_auth(provider_id: str) -> bool:
    """
    Check if provider supports cloud authentication.

    Args:
        provider_id: Provider identifier

    Returns:
        True if provider supports cloud auth (e.g., Google Cloud)
    """
    provider_id_lower = provider_id.lower()
    provider = LLM_PROVIDERS.get(provider_id_lower)
    return provider.supports_cloud_auth if provider else False


def format_model_name(provider_id: str, model: str) -> str:
    """
    Format model name with provider prefix for litellm.

    Args:
        provider_id: Provider identifier
        model: Model name

    Returns:
        Formatted model name for litellm (e.g., 'gemini/gemini-1.5-pro')
    """
    prefix = get_provider_prefix(provider_id)
    return f"{prefix}{model}" if prefix else model
