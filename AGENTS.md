# PromptAlchemy — agent guide

PromptAlchemy enhances LLM prompts through litellm. The repo ships a PySide6
GUI (`main.py`) and a CLI (`python3 -m cli.main`). Global house rules apply
(`~/.config/agents/AGENTS.md`); this file adds only what is specific to this
repo.

## Hard rules

- None beyond the global rules. Keep API keys in keyring or the encrypted
  file store (`core/security.py`). Never write them to logs or config.

## Gotchas

- The version lives in `core/version.py` (`__version__` and
  `__version_info__`). The GUI title bar, CLI header, `--help`, and
  `--version` import from there. `cli/__init__.py` holds a stale, unused
  `__version__`; do not treat it as the version source.
- `core/config.py` auto-imports ImageAI auth on first run. It reads the
  sibling `ImageAI/config.json` in the platform config dir and, under WSL,
  globs `/mnt/c/Users/*/AppData/Roaming/ImageAI/config.json`. A blank
  ImageAI config is skipped; a populated one sets `auth_mode` and provider
  keys silently.
- Google Cloud auth needs the `gcloud` CLI on PATH; there is no SDK-only
  fallback.

## Conventions

- Register new providers in `core/llm_models.py`. Add new enhancement modes
  to the control-panel presets.
- Use `pathlib.Path` for all file operations. Use `QSettings` for Qt UI
  persistence; app settings go through `ConfigManager` (`core/config.py`).
- Every CLI option has a short and a long form. The CLI accepts stdin and
  returns meaningful exit codes.
- Show a status dialog for long-running GUI operations.

## Build / test

- GUI: `python3 main.py`. CLI: `python3 -m cli.main --help`.
- No test suite; `test_model_params.py` is a manual script.

## Pointers

- Architecture summary: `Docs/Project_Summary.md`.
- Auth pattern reference: the ImageAI repo (`../ImageAI`).

## Scanning & review

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependency, code, and secret
scanning" and "Model delegation & cross-provider review". It is not restated
here; read it there. What is specific to this repo:

- CI runs `gitleaks` and `osv-scanner` on every PR, every push to `main`, and
  weekly (`.github/workflows/security.yml`). There are no npm jobs: this repo
  has no `package.json`, so `pip`/`requirements.txt` is the whole dependency
  surface and `osv-scanner` is what reads it.
- Dependabot config is committed, with grouped security PRs (`.github/dependabot.yml`).
- SHA-pinned actions get **no Dependabot alerts**: GitHub generates them only
  for actions on semantic versions (docs: "About Dependabot alerts"). So no
  security-update PR can ever fire for a pinned action, an
  `applies-to: security-updates` group over github-actions is dead config, and
  the weekly version update is their only automatic remediation -- which is why
  the github-actions block carries no semver-major ignore. DETECTION comes from
  osv-scanner's `github/actions` plugin, which is NOT in its default plugin set
  and so is named explicitly in `security.yml`.
- Dependabot **alerts** are a per-repo GitHub setting; a config file does not
  turn them on. Without them the config above governs version updates only.
  Check it by HTTP STATUS, not by exit code -- `gh api` exits 0 on success
  and 1 on any failure, and never exits 404 or 403:
  `gh api -i -X GET repos/lelandg/PromptAlchemy/vulnerability-alerts | head -1`
  204 = on, 404 = off, 403 = the token has no admin on this repo, which is
  NOT the same as off. Enable: same path with `-X PUT`.
- Alerts and automatic security **updates** are two switches, not one. Alerts
  only report; the half that opens PRs is `automated-security-fixes` (same API
  shape). It is deliberately OFF here: this repo took its first scan with a
  pre-existing advisory backlog, and enabling it would open that backlog as
  PRs at once. Turn it on per repo once the backlog is cleared.
- PR reviewers configured for this repo: **Codex** (run locally against the
  committed branch before opening the PR) and **CodeRabbit**
  (`coderabbitai[bot]`). How to read their checks -- which one re-reviews a
  push, why a green check does not mean "no findings", and which label skips
  which bot -- is in the global policy cited above and is deliberately not
  repeated here.
