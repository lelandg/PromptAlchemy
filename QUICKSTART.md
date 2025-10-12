# PromptAlchemy - Quick Start Guide

## Install (30 seconds)

```bash
# Linux/macOS/WSL
git clone <repository>
cd PromptAlchemy
python3 -m venv .venv_linux
source .venv_linux/bin/activate
pip install -r requirements.txt

# Windows (PowerShell)
git clone <repository>
cd PromptAlchemy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Set Up API Key (1 minute)

```bash
# OpenAI (recommended for first try)
python -m cli.main config set-key openai sk-your-key-here

# Get key: https://platform.openai.com/api-keys
```

## First Enhancement (GUI)

```bash
# Launch GUI
python3 main.py  # or python main.py on Windows
```

1. Select **OpenAI** / **gpt-4o-mini** (fast & cheap)
2. Enter prompt: "Create a todo app"
3. Click **Enhance Prompt**
4. Copy enhanced prompt to use with ChatGPT/Claude/etc.

## First Enhancement (CLI)

```bash
# Simple
python -m cli.main enhance "Create a todo app"

# With options
python -m cli.main enhance "Build an API" \
  --role "senior backend engineer" \
  --reasoning "Deep Think" \
  --verbosity detailed

# From file
echo "Create a REST API" > prompt.txt
python -m cli.main enhance -i prompt.txt -o enhanced.txt
cat enhanced.txt
```

## Common Commands

```bash
# List providers
python -m cli.main providers

# View history
python -m cli.main history list --limit 5

# Create project
python -m cli.main project create "My Project"

# Enhance and save to project
python -m cli.main enhance "Some prompt" --project "My Project"
```

## Pro Tips

1. **Start Simple**: Use default settings first
2. **Iterate**: Load from history and re-enhance with different settings
3. **Projects**: Group related prompts for easy access
4. **Tools**: Only select tools you actually need
5. **Verbosity**: Use "concise" for quick iterations, "comprehensive" for final prompts
6. **Local Models**: Try Ollama for free, unlimited usage

## Troubleshooting

**"litellm not found"**
```bash
pip install litellm
```

**"API key not configured"**
```bash
python -m cli.main config set-key openai sk-...
```

**GUI won't start (Linux)**
```bash
# Install Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0  # Ubuntu/Debian
sudo dnf install qt6-qtbase-gui                     # Fedora
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [Prompts/PromptAlchemy_Creation_Instructions.md](Prompts/PromptAlchemy_Creation_Instructions.md) to see how this was created
- Explore [Docs/Project_Summary.md](Docs/Project_Summary.md) for architecture details

## Support

Open an issue on GitHub or check the README for more help.

---

**Ready in under 2 minutes!**
