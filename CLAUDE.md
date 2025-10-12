# PromptAlchemy - Claude Code Project Configuration

*Last Updated: 2025-10-12*

## Project Overview

PromptAlchemy is a cross-platform Python application for enhancing LLM prompts using litellm. It provides both GUI (PySide6) and CLI interfaces for transforming simple prompts into sophisticated, structured prompts with configurable enhancement modes.

## Key Features
- **Multi-Mode Enhancement**: Control panel settings (Role, Reasoning, Verbosity, Tools, Self-Reflect, Meta-Fix)
- **LiteLLM Integration**: Support for all major LLM providers (OpenAI, Anthropic, Google, Ollama, LM Studio)
- **Authentication**: Secure keyring-based API key storage + Google Cloud auth support
- **File Attachments**: Multiple file support via MIME types
- **Projects**: Collections of prompt enhancements with history
- **Cross-Platform**: Windows, Linux, macOS support
- **100% Open Source**: Commercial use allowed

## Project Structure

```
PromptAlchemy/
├── core/               # Core functionality
│   ├── __init__.py
│   ├── config.py       # Configuration management
│   ├── security.py     # API key storage, rate limiting
│   ├── llm_models.py   # LLM provider definitions
│   ├── enhancer.py     # Prompt enhancement engine
│   └── history.py      # History tracking
├── gui/                # PySide6 GUI components
│   ├── __init__.py
│   ├── main_window.py  # Main application window
│   ├── tabs/           # Tab widgets
│   └── dialogs/        # Dialog windows
├── cli/                # Command-line interface
│   ├── __init__.py
│   └── main.py
├── providers/          # LLM provider implementations
│   ├── __init__.py
│   └── base.py
├── Docs/               # Documentation
├── Prompts/            # Self-documenting prompts
├── .venv/              # Python virtual env (PowerShell)
├── .venv_linux/        # Python virtual env (WSL/Linux)
├── main.py             # GUI entry point
├── requirements.txt    # Python dependencies
├── .gitignore
├── CLAUDE.md           # This file
└── README.md           # User documentation
```

## Development Guidelines

### Code Style
- **Type Hints**: Use Python type hints throughout
- **Docstrings**: All public functions/classes must have docstrings
- **Error Handling**: Graceful fallbacks, informative error messages
- **Cross-Platform**: Test path handling on Windows/Linux/macOS
- **Security**: Never log API keys, use secure storage

### Authentication Architecture
- **Primary**: Keyring-based secure storage (when available)
- **Fallback**: File-based encrypted storage
- **Cloud Auth**: Google Cloud SDK integration for gcloud auth
- **Import from ImageAI**: Automatically detect and import auth config if available

### GUI Design Principles
- **Status Dialogs**: Show progress for long-running operations
- **Auto-Save**: Persist UI state to user AppData folder
- **History**: Full history tab with double-click to load, search/filter
- **Settings**: Comprehensive defaults for all enhancement modes
- **Projects**: Organize enhancements into collections

### CLI Design Principles
- **Short & Long Options**: All params support both (e.g., `-m`/`--model`)
- **File Output**: Support writing enhanced prompts to files
- **Piping**: Accept input from stdin
- **Exit Codes**: Meaningful exit codes for automation

## Testing Instructions

### WSL/Linux Testing
```bash
# Create virtual environment
python3 -m venv .venv_linux
source .venv_linux/bin/activate
pip install -r requirements.txt

# Run GUI
python3 main.py

# Run CLI
python3 -m cli.main --help
```

### PowerShell Testing
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run GUI
python main.py

# Run CLI
python -m cli.main --help
```

## Dependencies

### Core
- `litellm` - LLM provider abstraction
- `PySide6` - Cross-platform GUI framework
- `keyring` - Secure credential storage (optional)
- `cryptography` - Encryption for file-based storage

### Optional
- `google-cloud-aiplatform` - Google Cloud authentication
- `google-auth` - Google authentication libraries

## Configuration Storage

### Platform-Specific Locations
- **Windows**: `%APPDATA%\PromptAlchemy\`
- **macOS**: `~/Library/Application Support/PromptAlchemy/`
- **Linux**: `~/.config/PromptAlchemy/`

### Stored Data
- `config.json` - Application settings, provider configs
- `history.jsonl` - Enhancement history (JSONL format)
- `projects/` - Project collections
- `state.json` - UI state (window size, last used settings)

## Code Map

### Core Classes
- **ConfigManager**: Platform-specific config persistence
- **SecureKeyStorage**: API key management with keyring
- **RateLimiter**: Provider-specific rate limiting
- **PromptEnhancer**: Main enhancement engine using litellm
- **HistoryManager**: Track and retrieve enhancement history
- **ProjectManager**: Manage collections of enhancements

### GUI Components
- **MainWindow**: Tabbed interface (Enhance, History, Projects, Settings)
- **EnhanceTab**: Main prompt enhancement interface
- **HistoryTab**: Browse and reload past enhancements
- **ProjectsTab**: Manage prompt collections
- **SettingsTab**: Configure defaults, API keys, providers
- **StatusDialog**: Progress indication for operations

### CLI Components
- **CLIMain**: Argument parsing and command routing
- **EnhanceCommand**: Execute prompt enhancement from CLI
- **HistoryCommand**: Query history from CLI
- **ProjectCommand**: Manage projects from CLI

## Known Limitations
- Google Cloud auth requires gcloud CLI installed
- Some providers have different rate limits
- File attachment support depends on model capabilities

## References
- LiteLLM Docs: https://docs.litellm.ai/
- PySide6 Docs: https://doc.qt.io/qtforpython-6/
- ImageAI Reference: ../ImageAI/ (for auth patterns)

## Development Notes
- When adding new providers, update `core/llm_models.py`
- When adding new enhancement modes, update control panel presets
- All file operations should use `pathlib.Path`
- Use QSettings for Qt-specific UI persistence
