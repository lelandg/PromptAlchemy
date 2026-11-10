# Changelog

All notable changes to PromptAlchemy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-11-09

### Added
- MIT `LICENSE` file. The README links it instead of carrying its own copy of
  the text, which had named a different copyright holder.
- Free security scanning in CI: gitleaks for secrets and osv-scanner for
  known-vulnerable dependencies and actions. Also Dependabot for pip and
  GitHub Actions.

### Fixed
- Raised dependency floors to clear known advisories. litellm is now
  `>=1.100.4` with every release affected by GHSA-7hp6-4w63-5g45 excluded, and
  there are new floors for certifi, httpx2 and httpcore2 (transitive).
- The `cli`, `core` and `gui` packages re-export the real version from
  `core/version.py`. Each used to carry a stale `1.0.0`.
- The README states the supported Python range as 3.10 to 3.14, which is what
  the current dependencies need.

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
