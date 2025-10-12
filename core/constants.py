"""Constants for PromptAlchemy application."""

APP_NAME = "PromptAlchemy"
APP_VERSION = "1.0.0"

# Provider API key documentation URLs
PROVIDER_KEY_URLS = {
    'openai': 'https://platform.openai.com/api-keys',
    'anthropic': 'https://console.anthropic.com/settings/keys',
    'google': 'https://aistudio.google.com/apikey',
    'gemini': 'https://aistudio.google.com/apikey',
    'stability': 'https://platform.stability.ai/account/keys',
    'cohere': 'https://dashboard.cohere.com/api-keys',
    'mistral': 'https://console.mistral.ai/api-keys',
    'groq': 'https://console.groq.com/keys',
}

# Enhancement modes
REASONING_MODES = [
    "Standard",
    "Deep Think",
    "Ultra Think",
    "Chain of Thought",
    "Step by Step"
]

VERBOSITY_LEVELS = [
    "minimal",
    "concise",
    "medium",
    "detailed",
    "comprehensive"
]

TOOL_OPTIONS = [
    "web",
    "code",
    "pdf",
    "image",
    "calculator",
    "file"
]

# Default enhancement template
DEFAULT_ENHANCEMENT_TEMPLATE = """Role: You are {role}

CONTROL PANEL
- Reasoning: {reasoning}
- Verbosity: {verbosity}
- Tools: {tools}
- Self-Reflect: {self_reflect}
- Meta-Fix: {meta_fix}

Task: {task}

{inputs}

{deliverables}"""
