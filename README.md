# PromptAlchemy

## **Transform simple prompts into sophisticated, structured LLM prompts**

> **PromptAlchemy** is a cross-platform application that enhances your LLM prompts using advanced prompt engineering techniques.
> 
> **Supports GUI and CLI interfaces, multiple LLM providers via litellm, and includes project management and history tracking.**

![Prompt Alchemist 01.png|33%](Prompt%20Alchemist%2001.png)

## Features

- **Multi-Mode Enhancement**: Configure reasoning modes (Standard, Deep Think, Ultra Think, Chain of Thought, Step by Step)
- **Verbosity Control**: From minimal to comprehensive output styles
- **Tool Integration**: Specify tools (web, code, pdf, image, calculator, file)
- **Self-Reflection & Meta-Fixing**: Enable advanced prompt optimization
- **Multi-Provider Support**: OpenAI (GPT-5, GPT-4.1), Anthropic (Claude Opus 4.1, Sonnet 4.5), Google Gemini (2.5 Pro/Flash), Ollama, LM Studio
- **Cloud Authentication**: Google Cloud Application Default Credentials (ADC) support for Gemini
- **File Attachments**: Attach multiple files via MIME types (text, images, PDFs)
- **Project Collections**: Organize enhancements into projects
- **Full History**: Browse, search, and reload past enhancements
- **Cross-Platform**: Windows, Linux, macOS support
- **Secure Storage**: API keys stored in system keyring when available
- **100% Open Source**: MIT License - commercial use allowed

## Screenshots

### Main Enhancement Interface
The Enhance tab provides a comprehensive control panel with:
- **Role Selection**: Define the AI's role (e.g., "senior backend engineer", "product designer")
- **Reasoning Mode**: Choose from Standard, Deep Think, Ultra Think, Chain of Thought, or Step by Step
- **Verbosity**: Control output length from minimal to comprehensive
- **Tools**: Select which tools to mention (web, code, pdf, image, calculator, file)
- **Self-Reflect & Meta-Fix**: Toggle advanced prompt optimization features
- **Inputs & Deliverables**: Specify additional context and expected outputs
- **File Attachments**: Drag and drop multiple files

### History Browser
- Double-click any entry to load it
- Search and filter by provider/model
- Full prompt preview
- Export history to JSON/JSONL

### Project Management
- Create collections of related prompts
- Tag and organize projects
- Export entire projects
- Quick load to enhancement interface

### Settings
- Secure API key management
- Default enhancement preferences
- Per-provider configuration

## Installation

### Requirements
- Python 3.8+
- Windows, macOS, or Linux

### Quick Start

#### Option 1: Windows (PowerShell)
```powershell
# Clone repository
cd D:\Documents\Code\GitHub
git clone https://github.com/yourusername/PromptAlchemy.git
cd PromptAlchemy

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run GUI
python main.py
```

#### Option 2: Linux/macOS/WSL
```bash
# Clone repository
git clone https://github.com/yourusername/PromptAlchemy.git
cd PromptAlchemy

# Create virtual environment
python3 -m venv .venv_linux
source .venv_linux/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run GUI
python3 main.py
```

## Configuration

### Setting Up API Keys

#### Via GUI
1. Open PromptAlchemy
2. Navigate to **Settings** tab
3. Enter your API key for each provider
4. Click **Save**

#### Via CLI
```bash
# Set OpenAI key
python -m cli.main config set-key openai sk-your-key-here

# Set Anthropic key
python -m cli.main config set-key anthropic sk-ant-your-key-here

# Set Google Gemini key
python -m cli.main config set-key gemini your-google-key-here
```

### Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google Gemini**: https://makersuite.google.com/app/apikey

### Google Cloud Authentication (Alternative)

For Google Gemini, you can use Google Cloud Application Default Credentials instead of API keys:

#### Setup via GUI
1. Navigate to **Settings** tab → **Google Cloud Authentication**
2. Select **"Google Cloud Account"** from the dropdown
3. Follow the setup instructions:
   - Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
   - Run: `gcloud auth application-default login`
   - Set project: `gcloud config set project YOUR_PROJECT_ID`
   - Enable Vertex AI API: https://console.cloud.google.com/apis/library
4. Click **"Check Google Cloud Status"** to verify authentication

#### Setup via CLI
```bash
# Install Google Cloud CLI (one-time setup)
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate (one-time setup)
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Use with PromptAlchemy
python -m cli.main enhance "Your prompt" \
  -p gemini -m gemini-2.5-pro \
  --auth-mode gcloud
```

**Benefits of Google Cloud Auth:**
- No API key management needed
- Uses your Google Cloud quotas and billing
- Seamless integration with existing GCP projects
- Better for team/enterprise environments

### Local Models (No API Key Required)

#### Ollama
1. Install Ollama: https://ollama.ai
2. Pull models: `ollama pull llama3.2`
3. Select "Ollama (Local)" in PromptAlchemy

#### LM Studio
1. Install LM Studio: https://lmstudio.ai
2. Start local server on port 1234
3. Select "LM Studio (Local)" in PromptAlchemy

## Usage

### GUI Mode

Launch the GUI:
```bash
python main.py          # Windows
python3 main.py         # Linux/macOS
```

#### Basic Workflow
1. **Select Provider/Model**: Choose from dropdown
2. **Configure Control Panel**:
   - Role: "product manager for indie creators"
   - Reasoning: Ultra Think
   - Verbosity: medium
   - Tools: web, code, pdf
   - Enable Self-Reflect and Meta-Fix
3. **Enter Prompt**: "Create a YouTube Topic Scout app"
4. **Add Details** (Optional):
   - Inputs: "solo YouTube creators, 1-100k subs"
   - Deliverables: "PRD, architecture, code"
5. **Attach Files** (Optional): Click "Add Files" to attach context
6. **Click "Enhance Prompt"**
7. **Copy/Save/Export**: Use toolbar buttons

#### Project Workflow
1. Enhance prompts as normal
2. Click "Save to Project"
3. Enter project name (creates if doesn't exist)
4. Access from **Projects** tab
5. Export entire project as JSON

#### History
- All enhancements automatically saved
- Browse from **History** tab
- Double-click to load any entry
- Search by text, filter by provider/model
- Export history to JSON/JSONL

### CLI Mode

#### Basic Enhancement
```bash
# Simple enhancement
python -m cli.main enhance "Create a todo app"

# Specify provider and model
python -m cli.main enhance "Build an API" -p openai -m gpt-4o

# Custom settings
python -m cli.main enhance "Design a database" \
  --role "senior database architect" \
  --reasoning "Deep Think" \
  --verbosity detailed \
  --tools web code

# Use Google Cloud authentication
python -m cli.main enhance "Analyze this data" \
  -p gemini -m gemini-2.5-pro \
  --auth-mode gcloud
```

#### File Input/Output
```bash
# Read from file
python -m cli.main enhance -i prompt.txt

# Write to file
python -m cli.main enhance "Build a web app" -o enhanced.txt

# Both
python -m cli.main enhance -i input.txt -o output.txt

# Pipe from stdin
echo "Create a REST API" | python -m cli.main enhance
```

#### File Attachments
```bash
# Attach single file
python -m cli.main enhance "Analyze this code" -a main.py

# Attach multiple files
python -m cli.main enhance "Review these files" \
  -a file1.py -a file2.py -a readme.md
```

#### Projects
```bash
# Create project
python -m cli.main project create "My Project" -d "Description"

# List projects
python -m cli.main project list

# Show project details
python -m cli.main project show "My Project"

# Export project
python -m cli.main project export "My Project" output.json

# Save enhancement to project
python -m cli.main enhance "Some prompt" --project "My Project"
```

#### History
```bash
# List recent history
python -m cli.main history list --limit 10

# Search history
python -m cli.main history list -q "database" -p openai

# Show specific entry
python -m cli.main history show 0

# Export history
python -m cli.main history export history.json

# Clear history
python -m cli.main history clear
```

#### Providers
```bash
# List available providers and models
python -m cli.main providers
```

### All CLI Options

```
enhancement options:
  prompt              Prompt to enhance
  -i, --input        Input file containing prompt
  -o, --output       Output file for enhanced prompt
  -p, --provider     LLM provider (default: openai)
  --auth-mode        Authentication mode (api-key|gcloud) for cloud providers
  -m, --model        Model name
  -r, --role         Role specification
  --reasoning        Reasoning mode (Standard|Deep Think|Ultra Think|Chain of Thought|Step by Step)
  -v, --verbosity    Verbosity level (minimal|concise|medium|detailed|comprehensive)
  -t, --tools        Tools to include (web code pdf image calculator file)
  --self-reflect     Enable self-reflection
  --no-self-reflect  Disable self-reflection
  --meta-fix         Enable meta-fixing
  --no-meta-fix      Disable meta-fixing
  --inputs           Additional inputs specification
  --deliverables     Deliverables specification
  -a, --attach       Attach files (can be used multiple times)
  --temperature      Model temperature (default: 0.7)
  --project          Save to project collection
```

## Configuration Storage

PromptAlchemy stores configuration and data in platform-specific locations:

- **Windows**: `%APPDATA%\PromptAlchemy\`
- **macOS**: `~/Library/Application Support/PromptAlchemy/`
- **Linux**: `~/.config/PromptAlchemy/`

### Stored Files
- `config.json` - Application settings, provider configs
- `state.json` - UI window state and positions
- `history.jsonl` - Enhancement history (JSONL format)
- `projects/` - Project collections

### API Key Security
- Keys are stored in system keyring when available (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- Falls back to encrypted file storage if keyring unavailable
- Keys are never logged or displayed in plain text

## Import from ImageAI

If you have ImageAI installed, PromptAlchemy will automatically import your API keys on first run. No manual configuration needed!

## Advanced Features

### Custom Enhancement Templates
Edit `core/constants.py` to customize the enhancement template structure.

### Rate Limiting
Automatic per-provider rate limiting prevents API quota issues:
- OpenAI: 50 calls/minute
- Anthropic: 50 calls/minute
- Google Gemini: 60 calls/minute

### Attachment Support
Supported file types:
- **Text files**: `.txt`, `.md`, `.py`, `.js`, etc. (embedded as text)
- **Images**: `.png`, `.jpg`, `.gif`, etc. (embedded as base64)
- **PDFs**: Included with metadata

## Troubleshooting

### "litellm not found"
```bash
pip install litellm
```

### "API key not configured"
Set your API key in Settings tab or via CLI:
```bash
python -m cli.main config set-key openai your-key-here
```

### "Keyring not available"
Install keyring for secure storage:
```bash
pip install keyring
```
Falls back to file storage automatically if unavailable.

### GUI won't start on Linux
Install Qt dependencies:
```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install qt6-qtbase-gui
```

## Development

### Project Structure
```
PromptAlchemy/
├── core/              Core functionality
│   ├── config.py      Configuration management
│   ├── enhancer.py    Enhancement engine
│   ├── history.py     History tracking
│   ├── projects.py    Project management
│   ├── llm_models.py  Provider/model definitions
│   ├── security.py    API key storage, rate limiting
│   └── constants.py   Application constants
├── gui/               PySide6 GUI
│   ├── main_window.py Main application window
│   ├── tabs/          Tab widgets
│   └── dialogs/       Dialog windows
├── cli/               Command-line interface
│   └── main.py        CLI entry point
├── main.py            GUI entry point
└── requirements.txt   Python dependencies
```

### Adding New Providers
Edit `core/llm_models.py` and add to `LLM_PROVIDERS` dictionary.

### Running Tests
```bash
# Create test virtual environment
python -m venv .venv_linux
source .venv_linux/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test CLI
python -m cli.main providers

# Test GUI
python main.py
```

## License

MIT License - 100% open source, commercial use allowed.

Copyright (c) 2025 PromptAlchemy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Acknowledgments

- Built with [litellm](https://github.com/BerriAI/litellm) for universal LLM access
- GUI powered by [PySide6](https://doc.qt.io/qtforpython-6/)
- Inspired by advanced prompt engineering practices

## Suggested Enhancements

Future improvements could include:
- **Prompt Templates**: Pre-built templates for common tasks
- **Batch Processing**: Process multiple prompts at once
- **Prompt Versioning**: Track prompt iterations
- **A/B Testing**: Compare different enhancement settings
- **Cloud Sync**: Sync history/projects across devices
- **Prompt Marketplace**: Share and discover prompt patterns
- **Cost Tracking**: Monitor API usage and costs
- **Streaming Support**: Real-time enhancement preview
- **Plugin System**: Extend with custom enhancers
- **Prompt Chains**: Link multiple enhancements together

---

**Made with alchemy for your prompts**
