# Changelog

All notable changes to PromptAlchemy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-12

### Added
- Central version management in `core/version.py`
- Version display in GUI title bar
- Version display in CLI header and `--version` flag
- This CHANGELOG.md file to track version history
- Help tab in GUI with comprehensive documentation

### Changed
- GUI title now shows version number
- CLI description and help output now show version number
- Improved organization of version information

### Fixed
- Consistent version numbering across all application components

## [0.1.0] - 2025-10-11

### Added
- Initial release of PromptAlchemy
- Cross-platform GUI application (PySide6)
- Command-line interface (CLI)
- Multi-mode prompt enhancement (Role, Reasoning, Verbosity, Tools, Self-Reflect, Meta-Fix)
- LiteLLM integration supporting all major providers (OpenAI, Anthropic, Google, Ollama, LM Studio)
- Secure API key storage via keyring
- Google Cloud authentication support
- File attachment support with MIME type handling
- Project management for organizing prompt enhancements
- History tracking with search and filter capabilities
- Cross-platform configuration storage
- Export/import functionality for history and projects
- Custom role management with sorting
- Keyboard shortcuts and hotkeys
- Auto-save UI state persistence
