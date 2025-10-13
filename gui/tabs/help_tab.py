"""Help tab with auto-generated documentation."""

import sys
from pathlib import Path
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton,
    QLineEdit, QLabel, QToolButton, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QFont, QTextDocument, QTextCursor, QTextCharFormat,
    QColor, QKeySequence, QShortcut
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import ConfigManager
from core.llm_models import get_all_provider_ids, get_provider_models, get_provider_display_name
from core.constants import REASONING_MODES, VERBOSITY_LEVELS, TOOL_OPTIONS


class HelpContentGenerator:
    """Generates HTML help content from various sources."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.base_dir = Path(__file__).parent.parent.parent

    def generate_html(self) -> str:
        """Generate complete HTML help documentation."""
        html = self._html_header()
        html += self._section_quick_start()
        html += self._section_features()
        html += self._section_control_panel()
        html += self._section_keyboard_shortcuts()
        html += self._section_providers()
        html += self._section_configuration()
        html += self._section_troubleshooting()
        html += self._section_about()
        html += self._html_footer()
        return html

    def _html_header(self) -> str:
        """Generate HTML header with CSS."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 15px 20px;
            background: #f9f9f9;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 8px;
            margin: 0 0 15px 0;
            font-size: 1.8em;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 6px;
            margin: 20px 0 10px 0;
            font-size: 1.4em;
        }
        .section-content {
            margin-left: 10px;
        }
        h3 {
            color: #7f8c8d;
            margin: 15px 0 8px 0;
            font-size: 1.1em;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 8px;
            margin: 10px 0;
        }
        .feature-card {
            background: white;
            padding: 8px 10px;
            border-radius: 5px;
            border-left: 3px solid #3498db;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .feature-card strong {
            color: #2c3e50;
            display: inline;
            margin-right: 8px;
        }
        .feature-card-desc {
            display: inline;
            color: #555;
        }
        .shortcut-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .shortcut-table th {
            background: #3498db;
            color: white;
            padding: 8px 10px;
            text-align: left;
            font-size: 0.95em;
        }
        .shortcut-table td {
            padding: 6px 10px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 0.9em;
        }
        .shortcut-table tr:hover {
            background: #f8f9fa;
        }
        .kbd {
            background: #34495e;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.85em;
            white-space: nowrap;
        }
        .provider-list {
            background: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .provider-item {
            margin: 6px 0;
            padding: 6px;
            border-left: 3px solid #27ae60;
        }
        .provider-item strong {
            display: inline;
            margin-right: 8px;
        }
        .provider-models {
            color: #7f8c8d;
            font-size: 0.85em;
            display: inline;
        }
        .info-box, .warning-box, .tip-box {
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid;
        }
        .info-box {
            background: #e8f4f8;
            border-color: #3498db;
        }
        .warning-box {
            background: #fff3cd;
            border-color: #ffc107;
        }
        .tip-box {
            background: #d4edda;
            border-color: #28a745;
        }
        code {
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }
        pre code {
            background: transparent;
            color: inherit;
        }
        ul, ol {
            padding-left: 25px;
            margin: 8px 0;
        }
        li {
            margin: 4px 0;
        }
        p {
            margin: 8px 0;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>PromptAlchemy Help</h1>
    <p style="margin: 0 0 15px 0;"><strong>Version 1.0.0</strong> | Transform simple prompts into sophisticated, structured LLM prompts</p>
"""

    def _html_footer(self) -> str:
        """Generate HTML footer."""
        return """
    <hr style="margin-top: 30px; border: none; border-top: 2px solid #ecf0f1;">
    <p style="text-align: center; color: #7f8c8d; font-size: 0.9em; margin: 10px 0;">
        Made with alchemy for your prompts | MIT License | 100% Open Source
    </p>
</body>
</html>
"""

    def _section_quick_start(self) -> str:
        """Generate quick start section."""
        return """
    <h2 id="quick-start">Quick Start</h2>
    <div class="section-content">
    <div class="tip-box">
        <strong>First Time Setup:</strong>
        <ol style="margin: 5px 0;">
            <li>Go to <strong>Settings</strong> tab</li>
            <li>Enter your API key for your preferred provider</li>
            <li>Click <strong>Save</strong></li>
            <li>Return to <strong>Enhance</strong> tab and start!</li>
        </ol>
    </div>

    <h3>Basic Workflow</h3>
    <ol>
        <li><strong>Select Provider/Model:</strong> Choose your LLM provider</li>
        <li><strong>Configure Control Panel:</strong> Set role, reasoning, verbosity, tools</li>
        <li><strong>Enter Your Prompt:</strong> Type or paste your original prompt</li>
        <li><strong>Add Context (Optional):</strong> Specify inputs and deliverables</li>
        <li><strong>Attach Files (Optional):</strong> Add context files, images, or PDFs</li>
        <li><strong>Click "Enhance Prompt":</strong> Or press <span class="kbd">Ctrl+Enter</span></li>
        <li><strong>Copy/Save:</strong> Use <span class="kbd">Ctrl+C</span> or <span class="kbd">Ctrl+S</span></li>
    </ol>
    </div>
"""

    def _section_features(self) -> str:
        """Generate features overview section."""
        features = [
            ("Multi-Mode Enhancement", "Configure reasoning depth from Standard to Ultra Think with Chain of Thought options."),
            ("Verbosity Control", "Choose output style from minimal to comprehensive based on your needs."),
            ("Tool Integration", "Specify which tools the LLM should use: web search, code execution, PDF processing, and more."),
            ("Self-Reflection", "Enable AI self-review for improved prompt quality (uses 20-30% more tokens)."),
            ("Meta-Fixing", "Automatically correct common prompt issues and optimize structure."),
            ("File Attachments", "Attach multiple files (text, images, PDFs) to provide context to your prompts."),
            ("Project Collections", "Organize related prompts into projects for better organization."),
            ("Full History", "Browse, search, and reload all past enhancements with filtering and export options."),
            ("Multi-Provider", "Support for OpenAI, Anthropic, Google Gemini, Ollama, LM Studio, and more via litellm."),
            ("Secure Storage", "API keys stored in system keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)."),
            ("Cloud Authentication", "Google Cloud Application Default Credentials (ADC) support for Gemini models."),
            ("Cross-Platform", "Works on Windows, macOS, and Linux with native UI integration."),
        ]

        cards = ""
        for title, desc in features:
            cards += f"""
        <div class="feature-card">
            <strong>{title}:</strong>
            <span class="feature-card-desc">{desc}</span>
        </div>
"""

        return f"""
    <h2 id="features">Features Overview</h2>
    <div class="section-content">
    <div class="feature-grid">
        {cards}
    </div>
    </div>
"""

    def _section_control_panel(self) -> str:
        """Generate control panel reference."""
        reasoning_items = "".join([f"<li><strong>{mode}</strong></li>" for mode in REASONING_MODES])
        verbosity_items = "".join([f"<li><strong>{level}</strong></li>" for level in VERBOSITY_LEVELS])
        tools_items = "".join([f"<li><strong>{tool}</strong></li>" for tool in TOOL_OPTIONS])

        return f"""
    <h2 id="control-panel">Control Panel Reference</h2>
    <div class="section-content">

    <h3>Provider / Model</h3>
    <p>Select the LLM provider and specific model. Different models have different capabilities, costs, and response styles.</p>

    <h3>Role</h3>
    <p>Define the role or persona for the LLM. Examples: "senior software engineer", "product manager", "technical writer". Type a custom role and click <strong>+</strong> to save it.</p>

    <h3>Reasoning Mode</h3>
    <p>Controls the depth and style of reasoning:</p>
    <ul style="margin: 5px 0;">{reasoning_items}</ul>

    <h3>Verbosity Level</h3>
    <p>Controls the expected detail level:</p>
    <ul style="margin: 5px 0;">{verbosity_items}</ul>

    <h3>Tools</h3>
    <p>Specify which tools the LLM should mention or use:</p>
    <ul style="margin: 5px 0;">{tools_items}</ul>

    <h3>Self-Reflect Option</h3>
    <p><strong>Benefits:</strong> Improved quality, identifies ambiguities. <strong>Trade-offs:</strong> +20-30% tokens, longer processing. <strong>Recommendation:</strong> Enable for complex prompts.</p>

    <h3>Meta-Fix Option</h3>
    <p><strong>Benefits:</strong> Corrects common issues, improves clarity. <strong>Trade-offs:</strong> May alter intent slightly. <strong>Recommendation:</strong> Enable for draft prompts.</p>

    <h3>Inputs & Deliverables</h3>
    <p><strong>Inputs:</strong> Additional context or constraints. <strong>Deliverables:</strong> Expected output format (e.g., "PRD document", "Python code").</p>

    <h3>File Attachments</h3>
    <p>Attach text files (.txt, .md, .py), images (.png, .jpg), or PDFs. Click "Add Files" to browse, "Remove" to detach. Requires multimodal model support for images.</p>
    </div>
"""

    def _section_keyboard_shortcuts(self) -> str:
        """Generate keyboard shortcuts section."""
        shortcuts = [
            ("Enhance Prompt", "Ctrl+Enter", "Start prompt enhancement"),
            ("Copy Enhanced", "Ctrl+C", "Copy enhanced prompt to clipboard"),
            ("Save to File", "Ctrl+S", "Save enhanced prompt to file"),
            ("New Project", "Ctrl+N", "Create a new project"),
            ("Refresh History", "F5", "Refresh history list"),
            ("Switch to Enhance", "Alt+1", "Navigate to Enhance tab"),
            ("Switch to History", "Alt+2", "Navigate to History tab"),
            ("Switch to Projects", "Alt+3", "Navigate to Projects tab"),
            ("Switch to Settings", "Alt+4", "Navigate to Settings tab"),
            ("Switch to Help", "Alt+5", "Navigate to Help tab (this page)"),
            ("Find in Help", "Ctrl+F", "Search for text in help"),
            ("Increase Font", "+", "Increase help text size"),
            ("Decrease Font", "-", "Decrease help text size"),
        ]

        rows = ""
        for action, shortcut, desc in shortcuts:
            rows += f"""
            <tr>
                <td>{action}</td>
                <td><span class="kbd">{shortcut}</span></td>
                <td>{desc}</td>
            </tr>
"""

        return f"""
    <h2 id="keyboard-shortcuts">Keyboard Shortcuts</h2>
    <div class="section-content">
    <table class="shortcut-table">
        <thead>
            <tr>
                <th>Action</th>
                <th>Shortcut</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    </div>
"""

    def _section_providers(self) -> str:
        """Generate LLM providers section."""
        providers_html = ""
        for provider_id in get_all_provider_ids():
            display_name = get_provider_display_name(provider_id)
            models = get_provider_models(provider_id)
            models_str = ", ".join(models[:5])
            if len(models) > 5:
                models_str += f" (+{len(models) - 5} more)"

            providers_html += f"""
        <div class="provider-item">
            <strong>{display_name}:</strong>
            <span class="provider-models">{models_str}</span>
        </div>
"""

        return f"""
    <h2 id="providers">LLM Providers & Models</h2>
    <div class="section-content">
    <p>PromptAlchemy supports multiple LLM providers via <strong>litellm</strong>. Configure API keys in the Settings tab.</p>

    <div class="provider-list">
        {providers_html}
    </div>

    <h3>Getting API Keys</h3>
    <ul>
        <li><strong>OpenAI:</strong> <a href="https://platform.openai.com/api-keys">platform.openai.com/api-keys</a></li>
        <li><strong>Anthropic:</strong> <a href="https://console.anthropic.com/settings/keys">console.anthropic.com/settings/keys</a></li>
        <li><strong>Google Gemini:</strong> <a href="https://makersuite.google.com/app/apikey">makersuite.google.com/app/apikey</a></li>
    </ul>

    <h3>Local Models (No API Key)</h3>
    <p><strong>Ollama:</strong> Install from <a href="https://ollama.ai">ollama.ai</a>, pull models with <code>ollama pull llama3.2</code></p>
    <p><strong>LM Studio:</strong> Install from <a href="https://lmstudio.ai">lmstudio.ai</a>, start server on port 1234</p>
    </div>
"""

    def _section_configuration(self) -> str:
        """Generate configuration section."""
        config_path = str(self.config.config_dir)

        return f"""
    <h2 id="configuration">Configuration & Storage</h2>
    <div class="section-content">

    <h3>Configuration Location</h3>
    <div class="info-box">
        <strong>Current Config Directory:</strong><br>
        <code>{config_path}</code>
    </div>

    <h3>Platform-Specific Locations</h3>
    <ul>
        <li><strong>Windows:</strong> <code>%APPDATA%\\PromptAlchemy\\</code></li>
        <li><strong>macOS:</strong> <code>~/Library/Application Support/PromptAlchemy/</code></li>
        <li><strong>Linux:</strong> <code>~/.config/PromptAlchemy/</code></li>
    </ul>

    <h3>Stored Files</h3>
    <ul>
        <li><strong>config.json:</strong> Application settings, provider configurations, custom roles</li>
        <li><strong>state.json:</strong> UI window state, positions, last used settings</li>
        <li><strong>history.jsonl:</strong> Enhancement history in JSONL format</li>
        <li><strong>projects/:</strong> Directory containing project collections</li>
    </ul>

    <h3>API Key Security</h3>
    <p>API keys stored in system keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service) with encrypted file storage fallback. Keys never logged or displayed.</p>

    <h3>Rate Limiting</h3>
    <p>Automatic per-provider rate limiting: <strong>OpenAI:</strong> 50/min, <strong>Anthropic:</strong> 50/min, <strong>Google Gemini:</strong> 60/min</p>
    </div>
"""

    def _section_troubleshooting(self) -> str:
        """Generate troubleshooting section."""
        return """
    <h2 id="troubleshooting">Troubleshooting</h2>
    <div class="section-content">

    <h3>Common Issues</h3>

    <div class="warning-box">
        <strong>API key not configured:</strong> Go to Settings tab and enter your API key for the selected provider.
    </div>

    <div class="warning-box">
        <strong>Enhancement failed/timeout:</strong> Check internet connection, verify API key is correct, ensure you haven't exceeded rate limits.
    </div>

    <div class="warning-box">
        <strong>Keyring not available:</strong> Install keyring package: <code>pip install keyring</code>. Falls back to encrypted file storage automatically.
    </div>

    <div class="warning-box">
        <strong>Google Cloud auth failed:</strong> Ensure Google Cloud CLI installed, run <code>gcloud auth application-default login</code>, set project, enable Vertex AI API.
    </div>

    <div class="warning-box">
        <strong>GUI won't start on Linux:</strong> Install Qt dependencies: <code>sudo apt install libxcb-xinerama0 libxcb-cursor0</code> (Ubuntu/Debian) or <code>sudo dnf install qt6-qtbase-gui</code> (Fedora)
    </div>

    <h3>Getting Help</h3>
    <p>Check README.md in the installation directory, report bugs on GitHub, or check application logs in the config directory.</p>
    </div>
"""

    def _section_about(self) -> str:
        """Generate about section."""
        return """
    <h2 id="about">About & License</h2>
    <div class="section-content">

    <h3>PromptAlchemy</h3>
    <p><strong>Version:</strong> 1.0.0 | A cross-platform application for enhancing LLM prompts using advanced prompt engineering.</p>

    <h3>Key Technologies</h3>
    <p><strong>litellm</strong> (LLM abstraction), <strong>PySide6</strong> (Qt GUI), <strong>keyring</strong> (secure storage), <strong>cryptography</strong> (encryption)</p>

    <h3>License</h3>
    <div class="info-box">
        <strong>MIT License</strong> - 100% Open Source, commercial use allowed, free forever.
    </div>

    <h3>Acknowledgments</h3>
    <ul>
        <li>Built with <a href="https://github.com/BerriAI/litellm">litellm</a> for universal LLM access</li>
        <li>GUI powered by <a href="https://doc.qt.io/qtforpython-6/">PySide6</a></li>
        <li>Inspired by advanced prompt engineering practices</li>
    </ul>

    <p style="text-align: center; margin-top: 20px; font-size: 1.1em; color: #3498db;">
        <strong>Made with alchemy for your prompts</strong>
    </p>
    </div>
"""


class SidebarNav(QWidget):
    """Sidebar navigation widget."""

    def __init__(self, browser: QTextBrowser):
        super().__init__()
        self.browser = browser
        self.init_ui()

    def init_ui(self):
        """Initialize sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Title
        title = QLabel("Contents")
        title.setStyleSheet("font-weight: bold; padding: 5px; background: #3498db; color: white;")
        layout.addWidget(title)

        # Navigation links
        sections = [
            ("Quick Start", "quick-start"),
            ("Features", "features"),
            ("Control Panel", "control-panel"),
            ("Shortcuts", "keyboard-shortcuts"),
            ("Providers", "providers"),
            ("Configuration", "configuration"),
            ("Troubleshooting", "troubleshooting"),
            ("About", "about"),
        ]

        for label, anchor in sections:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 5px 10px;
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    background: #e8f4f8;
                }
            """)
            btn.clicked.connect(lambda checked, a=anchor: self.navigate_to(a))
            layout.addWidget(btn)

        layout.addStretch()

    def navigate_to(self, anchor: str):
        """Navigate to section."""
        self.browser.scrollToAnchor(anchor)


class HelpTab(QWidget):
    """Help tab widget with auto-generated documentation."""

    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config = config
        self.generator = HelpContentGenerator(config)
        self.search_index = 0
        self.search_results = []
        self.current_font_size = 10
        self.sidebar_on_right = False
        self.init_ui()

    def init_ui(self):
        """Initialize the help tab UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)

        # Font size controls
        font_label = QLabel("Font:")
        toolbar.addWidget(font_label)

        self.decrease_font_btn = QToolButton()
        self.decrease_font_btn.setText("-")
        self.decrease_font_btn.setToolTip("Decrease font size")
        self.decrease_font_btn.clicked.connect(self.decrease_font)
        toolbar.addWidget(self.decrease_font_btn)

        self.increase_font_btn = QToolButton()
        self.increase_font_btn.setText("+")
        self.increase_font_btn.setToolTip("Increase font size")
        self.increase_font_btn.clicked.connect(self.increase_font)
        toolbar.addWidget(self.increase_font_btn)

        toolbar.addSpacing(10)

        # Sidebar toggle
        self.sidebar_toggle_btn = QPushButton("Sidebar →")
        self.sidebar_toggle_btn.setToolTip("Toggle sidebar position (left/right)")
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar_position)
        toolbar.addWidget(self.sidebar_toggle_btn)

        toolbar.addStretch()

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Regenerate help content")
        refresh_btn.clicked.connect(self.refresh_content)
        toolbar.addWidget(refresh_btn)

        main_layout.addLayout(toolbar)

        # Search bar (hidden by default)
        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(5, 0, 5, 5)

        search_layout.addWidget(QLabel("Find:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search help...")
        self.search_input.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_input)

        self.search_status = QLabel("")
        search_layout.addWidget(self.search_status)

        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self.find_next)
        search_layout.addWidget(next_btn)

        close_search_btn = QPushButton("✕")
        close_search_btn.setMaximumWidth(30)
        close_search_btn.clicked.connect(self.hide_search)
        search_layout.addWidget(close_search_btn)

        self.search_widget.hide()
        main_layout.addWidget(self.search_widget)

        # Splitter for sidebar and content
        self.splitter = QSplitter(Qt.Horizontal)

        # Sidebar navigation
        self.sidebar = QFrame()
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Text browser for HTML display
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)

        # Disable text selection on drag to allow scrolling (Wacom tablet fix)
        self.browser.setTextInteractionFlags(
            Qt.TextBrowserInteraction | Qt.TextSelectableByKeyboard
        )

        # Create sidebar nav after browser exists
        self.sidebar_nav = SidebarNav(self.browser)
        sidebar_layout.addWidget(self.sidebar_nav)

        # Add to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.browser)
        self.splitter.setSizes([200, 800])

        main_layout.addWidget(self.splitter)

        # Setup keyboard shortcuts
        self.setup_shortcuts()

        # Generate and set content
        self.refresh_content()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+F for search
        find_shortcut = QShortcut(QKeySequence.Find, self)
        find_shortcut.activated.connect(self.show_search)

        # Esc to hide search
        esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_shortcut.activated.connect(self.hide_search)

        # + to increase font
        increase_shortcut = QShortcut(QKeySequence(Qt.Key_Plus), self)
        increase_shortcut.activated.connect(self.increase_font)

        # - to decrease font
        decrease_shortcut = QShortcut(QKeySequence(Qt.Key_Minus), self)
        decrease_shortcut.activated.connect(self.decrease_font)

    def refresh_content(self):
        """Refresh the help content."""
        html_content = self.generator.generate_html()
        self.browser.setHtml(html_content)
        self.apply_font_size()

    def show_search(self):
        """Show search bar and focus input."""
        self.search_widget.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def hide_search(self):
        """Hide search bar and clear highlights."""
        self.search_widget.hide()
        self.search_input.clear()
        self.search_status.clear()
        # Clear all highlights by refreshing content
        self.refresh_content()

    def find_next(self):
        """Find next occurrence of search text."""
        search_text = self.search_input.text()
        if not search_text:
            return

        # Use QTextBrowser's find functionality
        found = self.browser.find(search_text)

        if found:
            self.search_status.setText("✓")
            self.search_status.setStyleSheet("color: green;")
        else:
            # Try from beginning
            cursor = self.browser.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.browser.setTextCursor(cursor)

            found = self.browser.find(search_text)
            if found:
                self.search_status.setText("↻ Wrapped")
                self.search_status.setStyleSheet("color: blue;")
            else:
                self.search_status.setText("✗ Not found")
                self.search_status.setStyleSheet("color: red;")

    def increase_font(self):
        """Increase font size."""
        self.current_font_size = min(20, self.current_font_size + 1)
        self.apply_font_size()

    def decrease_font(self):
        """Decrease font size."""
        self.current_font_size = max(8, self.current_font_size - 1)
        self.apply_font_size()

    def apply_font_size(self):
        """Apply current font size to browser."""
        font = self.browser.font()
        font.setPointSize(self.current_font_size)
        self.browser.setFont(font)

    def toggle_sidebar_position(self):
        """Toggle sidebar between left and right."""
        self.sidebar_on_right = not self.sidebar_on_right

        # Remove widgets
        self.splitter.widget(0).setParent(None)
        self.splitter.widget(0).setParent(None)

        # Re-add in new order
        if self.sidebar_on_right:
            self.splitter.addWidget(self.browser)
            self.splitter.addWidget(self.sidebar)
            self.sidebar_toggle_btn.setText("← Sidebar")
            self.splitter.setSizes([800, 200])
        else:
            self.splitter.addWidget(self.sidebar)
            self.splitter.addWidget(self.browser)
            self.sidebar_toggle_btn.setText("Sidebar →")
            self.splitter.setSizes([200, 800])
