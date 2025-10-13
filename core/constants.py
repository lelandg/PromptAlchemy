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

# Preset roles for prompt enhancement
DEFAULT_ROLES = [
    # General
    "expert assistant",
    "helpful AI assistant",

    # Software & Engineering
    "senior software engineer",
    "frontend developer",
    "backend developer",
    "full-stack developer",
    "DevOps engineer",
    "systems architect",
    "cloud architect",
    "solutions architect",
    "API designer",
    "security analyst",
    "QA engineer",
    "database administrator",

    # Data & AI
    "data scientist",
    "machine learning engineer",
    "AI research scientist",
    "data analyst",

    # Design & Creative
    "UX/UI designer",
    "UX researcher",
    "graphic designer",
    "brand strategist",
    "creative director",
    "content creator",
    "illustrator",
    "video editor",
    "creative writer",

    # Business & Marketing
    "product manager",
    "business analyst",
    "project manager",
    "marketing strategist",
    "SEO specialist",
    "copywriter",
    "social media manager",
    "financial advisor",

    # Research & Education
    "research assistant",
    "academic researcher",
    "educator",
    "curriculum designer",
    "instructional designer",

    # Health & Wellness
    "medical advisor",
    "mental health counselor",
    "nutritionist",
    "healthcare consultant",

    # Writing & Communication
    "technical writer",
    "journalist",
    "editor",
    "translator",

    # Legal & Compliance
    "legal advisor",
    "compliance officer"
]

# Default enhancement template
DEFAULT_ENHANCEMENT_TEMPLATE = """Role: You are a {role}

CONTROL PANEL
- Reasoning: {reasoning}
- Verbosity: {verbosity}
- Tools: {tools}
- Self-Reflect: {self_reflect}
- Meta-Fix: {meta_fix}

Task: {task}

{inputs}

{deliverables}"""
