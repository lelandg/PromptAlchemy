# PromptAlchemy Creation Instructions

**A Self-Documenting Software Creation Prompt**

This document contains the original instructions used to create PromptAlchemy. It serves as an example of AI-assisted software development where the specification itself is a form of executable documentation. With AI, this prompt becomes software.

## Original Request

Create a Python LLM prompt enhancer using litellm with the following specifications:

### Core Requirements

1. **Project Setup**
   - Create `./CLAUDE.md` with appropriate project settings
   - 100% open source with commercial use allowed (MIT License)
   - 100% cross-platform (Windows, Linux, macOS)
   - Support Python 3.8+

2. **Authentication & Configuration**
   - Support all authentication methods that ../ImageAI does (except image providers)
   - Extract authentication classes from ImageAI for reuse
   - If user has ImageAI configured, automatically import authentication
   - Store API keys securely using system keyring (with file fallback)
   - Platform-specific configuration storage:
     - Windows: `%APPDATA%\PromptAlchemy\`
     - macOS: `~/Library/Application Support/PromptAlchemy/`
     - Linux: `~/.config/PromptAlchemy/`

3. **LLM Provider Support**
   - OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo, etc.)
   - Anthropic Claude (Sonnet 4.5, Opus 4, etc.)
   - Google Gemini (2.0 Flash, 1.5 Pro, etc.)
   - Ollama (local models, no API key required)
   - LM Studio (local models, no API key required)
   - Use litellm for universal provider abstraction

### Enhancement Modes

Based on the reference screenshots (detailed below), implement the following control panel options:

#### Screenshot 1: brave_ipEfu4regV.png
Shows a "CONTROL PANEL" with these options:
- **Role**: "You are a product + full-stack app planner for indie creators."
- **Reasoning**: "ULTRA THINK" (dropdown or selection)
- **Verbosity**: "medium" (options: minimal, concise, medium, detailed, comprehensive)
- **Tools**: web, code, pdf, image (multi-select checkboxes)
- **Self-Reflect**: on (toggle checkbox)
- **Meta-Fix**: on (toggle checkbox)
- Plus button to add more control panel items

#### Screenshot 2: brave_c2UoKEH9Tu.png
Shows task planning section:
- **Task**: "Plan and scaffold a minimal app called 'YouTube Topic Scout' that finds trending ideas, scores them, and generates a script outline"
- **Inputs Section**:
  - Users: solo YouTube creators (1-100k subs), niches vary
  - Core loop: search a niche → fetch trending data → output 1-page brief + outline
  - Scoring signals (starter): search volume trend, CTR proxy (title comps), competition roughness, freshness recency
  - Non-negotiables: privacy-friendly, explainable scoring, simple UI
  - Tech prefs: Next.js + TypeScript, Tailwind, Prisma + SQLite (local); can swap DB later
  - Tone: practical, no fluff

#### Screenshot 3: TOXkbBiCpw.png
Shows deliverables section:
- **Deliverables**:
  1. PRD: 1-page PDF + Markdown (goal, users, JTBDs, MVP features vs 2.0, success metrics)
  2. Competitor research: exactly 2 one-line positioning (YT Trends, vidIQ)
  3. Architecture: Mermaid diagram + brief data-flow; DB schema as SQL CREATE TABLE for core entities
  4. API spec: OpenAPI YAML for endpoints (/topics, /score, /outline)
  5. UI: 3 lo-fi wireframes (PNG) — Home (query), Results (scored list), Brief (outline view)
  6. Starter code: a single Next.js page (index.tsx) with static DB schema (Prisma schema, seed script) + README (install/run)

### File Attachment Support

- Support multiple file attachments via MIME types
- No size limits unless imposed by litellm or model
- Handle text files (embedded as text)
- Handle images (embedded as base64)
- Handle PDFs and other files (metadata/summary)

### User Interface

#### GUI (PySide6)
Create a comprehensive GUI with the following tabs:

1. **Enhance Tab**
   - Control Panel (all settings from screenshots)
   - Original Prompt text area
   - Inputs and Deliverables fields (optional)
   - File attachment area with add/remove buttons
   - Enhanced Prompt output area (read-only)
   - Buttons: Enhance, Copy to Clipboard, Save to File, Save to Project

2. **History Tab**
   - Table view of all enhancements
   - Columns: Timestamp, Provider/Model, Original Prompt (preview), Tokens Used
   - Double-click to load entry
   - Full prompt preview panel
   - Search/filter capabilities
   - Buttons: Load to Enhance Tab, Export History, Clear History

3. **Projects Tab**
   - Project list sidebar
   - Project details panel (name, description, tags)
   - Prompts in project list
   - Double-click prompt to load
   - Buttons: New Project, Delete Project, Export Project

4. **Settings Tab**
   - API key input fields for each provider (password-masked)
   - Save buttons per provider
   - Default enhancement settings (role, reasoning, verbosity, tools)
   - Configuration storage location display

**GUI Features**:
- Status dialogs for long operations
- Auto-save/restore UI state (window size, positions)
- Use QSettings for Qt-specific persistence
- Progress indication during enhancement
- Error dialogs with helpful messages

#### CLI
Full command-line interface with short and long options:

```bash
# Examples
promptalchemy enhance "Create a todo app" -p openai -m gpt-4o-mini
promptalchemy enhance -i prompt.txt -o enhanced.txt
promptalchemy history list --limit 10
promptalchemy project create "My Project"
promptalchemy config set-key openai sk-...
promptalchemy providers
```

All CLI options must support both short (`-s`) and long (`--some-param`) forms.

### Project Collections

- Create collections of related prompt enhancements
- Store in `projects/` subdirectory
- Each project has:
  - Metadata (name, description, created date, tags)
  - Collection of prompts (JSONL format)
- Export projects to single JSON file
- Support adding enhancements to projects from both GUI and CLI

### History Tracking

- Auto-save all enhancements to history (JSONL format)
- Store:
  - Original prompt
  - Enhanced prompt
  - Provider and model used
  - All control panel settings
  - Timestamp
  - Tokens used (if available)
- Full-text search capability
- Filter by provider/model/date
- Export to JSON/JSONL

### Auto-Save & State Management

- Save UI state to AppData folder + `/PromptAlchemy`
- Create directory if it doesn't exist
- Persist:
  - Window size and position
  - Last used provider/model
  - Last used control panel settings
  - Tab selection
  - Splitter positions

### Virtual Environments

- `.gitignore` includes:
  - `.venv` (for PowerShell/Windows)
  - `.venv_linux` (for WSL/Linux)
  - PyCharm files (`.idea/`)
- README includes instructions for creating virtual environments
- Use `python3` for Linux/WSL testing
- Use `python` for Windows/PowerShell

### Testing Instructions

The application should be testable in WSL using:
```bash
python3 -m venv .venv_linux
source .venv_linux/bin/activate
pip install -r requirements.txt
python3 main.py  # GUI
python3 -m cli.main --help  # CLI
```

### Suggested Enhancements

The README should include a section suggesting future enhancements:
- Prompt templates library
- Batch processing
- Prompt versioning/diff
- A/B testing different settings
- Cloud sync
- Prompt marketplace
- Cost tracking
- Streaming support
- Plugin system
- Prompt chaining

## Screenshot Details

Since you may not have access to the screenshots, here's what they showed:

### Screenshot 1: Control Panel Interface
A clean, white card-style UI showing:
- Title: "Role: You are a product + full-stack app planner for indie creators."
- CONTROL PANEL section with:
  - Reasoning: ULTRA THINK (appears to be a selectable option)
  - Verbosity: medium (with a caret suggesting dropdown)
  - Tools: web, code, pdf, image (comma-separated list, likely checkboxes)
  - Self-Reflect: on (toggle)
  - Meta-Fix: on (toggle with cursor visible)
- A plus button at the bottom, suggesting ability to add more controls

### Screenshot 2: Task & Inputs Section
Shows a more detailed prompt structure:
- **Task header**: "Plan and scaffold a minimal app called 'YouTube Topic Scout'..."
- **Inputs section** with bullet points:
  - Users: describing target audience
  - Core loop: describing main functionality
  - Scoring signals: listing metrics
  - Non-negotiables: requirements
  - Tech prefs: technology stack
  - Tone: writing style guidance

### Screenshot 3: Deliverables Section
Continuation showing:
- **Deliverables header** listing 6 numbered items:
  1. PRD (Product Requirements Document)
  2. Competitor research
  3. Architecture (diagrams and schemas)
  4. API spec (OpenAPI YAML)
  5. UI wireframes
  6. Starter code (Next.js with specific files)
- Each item has detailed specifications in parentheses

## Meta-Commentary

This document demonstrates an interesting concept: **prompts as software**. The instructions you're reading were themselves given to an AI, which then generated a complete, working application.

Key insights:
1. **Specificity Matters**: Detailed screenshots and requirements lead to better results
2. **Structure Helps**: Breaking down requirements into logical sections aids implementation
3. **Examples Guide**: Providing specific examples (CLI commands, file paths) improves accuracy
4. **Iteration Potential**: This prompt could be refined further based on the initial results

## File Metadata

- **Created**: 2025-10-12
- **Purpose**: Document the creation of PromptAlchemy
- **Format**: Markdown (GitHub-flavored)
- **Status**: Complete specification that generated working software
- **Lines of Code Generated**: ~3000+ across 20+ files
- **Time to Generate**: Tracked from start to finish

## Usage

To reproduce PromptAlchemy or create a similar application:
1. Provide this document to an AI coding assistant
2. Review the generated code
3. Test and iterate
4. Extend with your own requirements

The fact that you're reading this in a working application proves the concept: with sufficient detail and AI assistance, documentation can directly become software.

---

*"Any sufficiently detailed specification is indistinguishable from code."* - Adapted from Clarke's Third Law
