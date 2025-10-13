"""Main window for PromptAlchemy GUI."""

import sys
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QPlainTextEdit, QPushButton, QLabel, QComboBox, QCheckBox,
    QLineEdit, QGroupBox, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QProgressDialog, QSpinBox, QDoubleSpinBox, QFormLayout,
    QSplitter, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor, QShortcut, QKeySequence

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.enhancer import PromptEnhancer
from core.history import HistoryManager
from core.projects import ProjectManager
from core.llm_models import get_all_provider_ids, get_provider_models, get_provider_display_name
from core.constants import REASONING_MODES, VERBOSITY_LEVELS, TOOL_OPTIONS, DEFAULT_ROLES
from core.version import __version__
from gui.tabs.help_tab import HelpTab

logger = logging.getLogger(__name__)


class EnhanceWorker(QThread):
    """Background worker for prompt enhancement."""
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, enhancer: PromptEnhancer, **kwargs):
        super().__init__()
        self.enhancer = enhancer
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.enhancer.enhance_prompt(**self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PromptAlchemyMainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.enhancer = PromptEnhancer(self.config)
        self.history_manager = HistoryManager(self.config.get_history_path())
        self.project_manager = ProjectManager(self.config.get_projects_dir())

        self.init_ui()
        self.load_ui_state()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"PromptAlchemy v{__version__} - LLM Prompt Enhancer")
        self.setMinimumSize(1000, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_enhance_tab()
        self.create_history_tab()
        self.create_projects_tab()
        self.create_settings_tab()
        self.create_help_tab()

        # Add global hotkeys
        self.setup_hotkeys()

    def create_enhance_tab(self):
        """Create the main enhancement tab."""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        # Control Panel
        control_group = QGroupBox("Control Panel")
        control_layout = QFormLayout()

        # Provider and Model
        provider_layout = QHBoxLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.setToolTip("Select the LLM provider (OpenAI, Anthropic, Google, etc.)")
        for provider_id in get_all_provider_ids():
            self.provider_combo.addItem(get_provider_display_name(provider_id), provider_id)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)

        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select the specific model to use for enhancement")
        provider_layout.addWidget(self.model_combo, 1)
        control_layout.addRow("Provider / Model:", provider_layout)

        # Role with combo and management
        role_layout = QHBoxLayout()
        self.role_combo = QComboBox()
        self.role_combo.setEditable(True)
        self.role_combo.setInsertPolicy(QComboBox.NoInsert)
        self.role_combo.setToolTip("Define the role or persona for the LLM to assume\n"
                                   "You can select from presets or type a custom role")
        self.populate_roles()
        role_layout.addWidget(self.role_combo, 1)

        add_role_btn = QPushButton("+")
        add_role_btn.setMaximumWidth(30)
        add_role_btn.setToolTip("Add current role to custom roles")
        add_role_btn.clicked.connect(self.add_custom_role)
        role_layout.addWidget(add_role_btn)

        self.role_sort_combo = QComboBox()
        self.role_sort_combo.addItems(["Name ↑", "Name ↓", "Date ↑", "Date ↓"])
        self.role_sort_combo.setMaximumWidth(80)
        self.role_sort_combo.setToolTip("Sort roles")
        self.role_sort_combo.currentTextChanged.connect(self.sort_roles)
        role_layout.addWidget(self.role_sort_combo)

        control_layout.addRow("Role:", role_layout)

        # Reasoning Mode
        self.reasoning_combo = QComboBox()
        self.reasoning_combo.addItems(REASONING_MODES)
        self.reasoning_combo.setToolTip(
            "Control the depth of reasoning:\n"
            "• Standard: Normal reasoning depth\n"
            "• Deep Think: Enhanced analytical thinking\n"
            "• Ultra Think: Maximum reasoning depth\n"
            "• Chain of Thought: Step-by-step logical reasoning\n"
            "• Step by Step: Explicit step-by-step breakdown"
        )
        control_layout.addRow("Reasoning:", self.reasoning_combo)

        # Verbosity
        self.verbosity_combo = QComboBox()
        self.verbosity_combo.addItems(VERBOSITY_LEVELS)
        self.verbosity_combo.setCurrentText("medium")
        self.verbosity_combo.setToolTip(
            "Control response detail level:\n"
            "• minimal: Brief, concise responses\n"
            "• concise: Compact but complete\n"
            "• medium: Balanced detail (recommended)\n"
            "• detailed: Thorough explanations\n"
            "• comprehensive: Maximum detail and examples"
        )
        control_layout.addRow("Verbosity:", self.verbosity_combo)

        # Tools
        tools_layout = QHBoxLayout()
        self.tool_checks = {}
        tool_tooltips = {
            "web": "Web Search Tool\n"
                   "✓ Benefits: Access to current information, facts, news\n"
                   "✗ Risks: May add latency, potential for outdated/incorrect info\n"
                   "⚠ Note: Requires provider support for web search",
            "code": "Code Execution Tool\n"
                    "✓ Benefits: Can run and test code, validate logic\n"
                    "✗ Risks: Security concerns, execution time\n"
                    "⚠ Caution: Only use with trusted prompts",
            "pdf": "PDF Processing Tool\n"
                   "✓ Benefits: Extract text and data from PDF files\n"
                   "✗ Risks: Large files may be slow to process\n"
                   "⚠ Note: Requires file attachment support",
            "image": "Image Analysis Tool\n"
                     "✓ Benefits: Visual understanding, OCR, image description\n"
                     "✗ Risks: Interpretation accuracy varies\n"
                     "⚠ Note: Requires multimodal model support",
            "calculator": "Mathematical Calculator Tool\n"
                         "✓ Benefits: Precise calculations, complex math\n"
                         "✗ Risks: Limited to numerical operations\n"
                         "⚠ Note: Best for computational tasks",
            "file": "File System Tool\n"
                    "✓ Benefits: Read/write files, access local data\n"
                    "✗ Risks: File system access, potential data exposure\n"
                    "⚠ Caution: Use with caution in production"
        }
        for tool in TOOL_OPTIONS:
            cb = QCheckBox(tool)
            cb.setToolTip(tool_tooltips.get(tool, f"Enable {tool} tool"))
            self.tool_checks[tool] = cb
            tools_layout.addWidget(cb)
        tools_layout.addStretch()
        control_layout.addRow("Tools:", tools_layout)

        # Self-Reflect and Meta-Fix
        options_layout = QHBoxLayout()
        self.self_reflect_check = QCheckBox("Self-Reflect")
        self.self_reflect_check.setChecked(True)
        self.self_reflect_check.setToolTip(
            "Self-Reflection Option\n"
            "✓ Benefits:\n"
            "  • Improved prompt quality through self-review\n"
            "  • Identifies ambiguities and gaps\n"
            "  • More thoughtful, nuanced outputs\n"
            "✗ Risks:\n"
            "  • Increased token usage (~20-30%)\n"
            "  • Longer processing time\n"
            "  • May over-complicate simple prompts\n"
            "⚠ Recommended: Enable for complex or critical prompts"
        )
        options_layout.addWidget(self.self_reflect_check)

        self.meta_fix_check = QCheckBox("Meta-Fix")
        self.meta_fix_check.setChecked(True)
        self.meta_fix_check.setToolTip(
            "Meta-Fix Option\n"
            "✓ Benefits:\n"
            "  • Automatically corrects common prompt issues\n"
            "  • Improves clarity and specificity\n"
            "  • Optimizes structure and formatting\n"
            "✗ Risks:\n"
            "  • May alter original intent slightly\n"
            "  • Additional processing overhead\n"
            "  • Can be overly aggressive on simple prompts\n"
            "⚠ Recommended: Enable for first-time or draft prompts"
        )
        options_layout.addWidget(self.meta_fix_check)
        options_layout.addStretch()
        control_layout.addRow("Options:", options_layout)

        control_group.setLayout(control_layout)
        splitter.addWidget(control_group)

        # Prompt Input
        prompt_group = QGroupBox("Original Prompt")
        prompt_layout = QVBoxLayout()
        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        self.prompt_input.setToolTip("Enter the original prompt you want to enhance\nPress Ctrl+Enter to start enhancement")
        prompt_layout.addWidget(self.prompt_input)

        # Inputs and Deliverables
        extras_layout = QHBoxLayout()
        self.inputs_edit = QLineEdit()
        self.inputs_edit.setPlaceholderText("Optional: Additional inputs...")
        self.inputs_edit.setToolTip("Specify any additional context, data, or inputs needed for the task")
        extras_layout.addWidget(QLabel("Inputs:"))
        extras_layout.addWidget(self.inputs_edit)

        self.deliverables_edit = QLineEdit()
        self.deliverables_edit.setPlaceholderText("Optional: Expected deliverables...")
        self.deliverables_edit.setToolTip("Describe the expected output format or deliverables")
        extras_layout.addWidget(QLabel("Deliverables:"))
        extras_layout.addWidget(self.deliverables_edit)
        prompt_layout.addLayout(extras_layout)

        # Attachments
        attach_layout = QHBoxLayout()
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(60)
        attach_layout.addWidget(self.attachments_list)

        attach_buttons = QVBoxLayout()
        add_attach_btn = QPushButton("Add Files")
        add_attach_btn.clicked.connect(self.add_attachments)
        attach_buttons.addWidget(add_attach_btn)

        remove_attach_btn = QPushButton("Remove")
        remove_attach_btn.clicked.connect(self.remove_attachments)
        attach_buttons.addWidget(remove_attach_btn)
        attach_layout.addLayout(attach_buttons)
        prompt_layout.addLayout(attach_layout)

        prompt_group.setLayout(prompt_layout)
        splitter.addWidget(prompt_group)

        # Enhanced Output
        output_group = QGroupBox("Enhanced Prompt")
        output_layout = QVBoxLayout()
        self.enhanced_output = QTextEdit()
        self.enhanced_output.setReadOnly(True)
        output_layout.addWidget(self.enhanced_output)
        output_group.setLayout(output_layout)
        splitter.addWidget(output_group)

        # Set initial splitter sizes (proportional)
        splitter.setSizes([200, 300, 300])

        # Buttons (outside splitter, at bottom)
        button_layout = QHBoxLayout()
        self.enhance_btn = QPushButton("Enhance Prompt")
        self.enhance_btn.setToolTip("Enhance the prompt using the selected provider and settings\nShortcut: Ctrl+Enter")
        self.enhance_btn.clicked.connect(self.enhance_prompt)
        button_layout.addWidget(self.enhance_btn)

        # Add Ctrl+Enter shortcut for enhance button
        enhance_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        enhance_shortcut.activated.connect(self.enhance_prompt)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.setToolTip("Copy the enhanced prompt to clipboard\nShortcut: Ctrl+C")
        self.copy_btn.clicked.connect(self.copy_enhanced)
        button_layout.addWidget(self.copy_btn)

        self.save_btn = QPushButton("Save to File")
        self.save_btn.setToolTip("Save the enhanced prompt to a text or markdown file\nShortcut: Ctrl+S")
        self.save_btn.clicked.connect(self.save_enhanced)
        button_layout.addWidget(self.save_btn)

        save_project_btn = QPushButton("Save to Project")
        save_project_btn.setToolTip("Save this enhancement to a project collection for later reference")
        save_project_btn.clicked.connect(self.save_to_project)
        button_layout.addWidget(save_project_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.tabs.addTab(tab, "Enhance")

        # Initialize models for first provider
        self.on_provider_changed(0)

    def create_history_tab(self):
        """Create the history browser tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search prompts...")
        self.history_search.textChanged.connect(self.refresh_history)
        filter_layout.addWidget(self.history_search)

        filter_layout.addWidget(QLabel("Provider:"))
        self.history_provider_filter = QComboBox()
        self.history_provider_filter.addItem("All", None)
        for provider_id in get_all_provider_ids():
            self.history_provider_filter.addItem(get_provider_display_name(provider_id), provider_id)
        self.history_provider_filter.currentIndexChanged.connect(self.refresh_history)
        filter_layout.addWidget(self.history_provider_filter)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_history)
        filter_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        filter_layout.addWidget(clear_btn)
        layout.addLayout(filter_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Provider/Model", "Original Prompt", "Tokens"])
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.doubleClicked.connect(self.load_history_entry)
        layout.addWidget(self.history_table)

        # Details preview
        details_group = QGroupBox("Selected Entry")
        details_layout = QVBoxLayout()
        self.history_details = QTextEdit()
        self.history_details.setReadOnly(True)
        self.history_details.setMaximumHeight(150)
        details_layout.addWidget(self.history_details)
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Buttons
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Load to Enhance Tab")
        load_btn.clicked.connect(self.load_history_to_enhance)
        btn_layout.addWidget(load_btn)

        export_btn = QPushButton("Export History")
        export_btn.clicked.connect(self.export_history)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.tabs.addTab(tab, "History")

        # Load history on startup
        self.refresh_history()

    def create_projects_tab(self):
        """Create the projects management tab."""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Projects list
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Projects:"))
        self.projects_list = QListWidget()
        self.projects_list.currentItemChanged.connect(self.on_project_selected)
        list_layout.addWidget(self.projects_list)

        # Project buttons
        project_btn_layout = QHBoxLayout()
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.create_project)
        project_btn_layout.addWidget(new_project_btn)

        delete_project_btn = QPushButton("Delete")
        delete_project_btn.clicked.connect(self.delete_project)
        project_btn_layout.addWidget(delete_project_btn)
        list_layout.addLayout(project_btn_layout)

        layout.addLayout(list_layout, 1)

        # Project details
        details_layout = QVBoxLayout()
        self.project_name_label = QLabel("Select a project")
        font = self.project_name_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.project_name_label.setFont(font)
        details_layout.addWidget(self.project_name_label)

        self.project_desc_label = QLabel("")
        details_layout.addWidget(self.project_desc_label)

        details_layout.addWidget(QLabel("Prompts in Project:"))
        self.project_prompts_list = QListWidget()
        self.project_prompts_list.doubleClicked.connect(self.load_project_prompt)
        details_layout.addWidget(self.project_prompts_list)

        export_project_btn = QPushButton("Export Project")
        export_project_btn.clicked.connect(self.export_project)
        details_layout.addWidget(export_project_btn)

        layout.addLayout(details_layout, 2)

        self.tabs.addTab(tab, "Projects")

        # Load projects
        self.refresh_projects()

    def create_settings_tab(self):
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # API Keys section
        api_group = QGroupBox("API Keys")
        api_layout = QFormLayout()

        self.api_key_widgets = {}
        for provider_id in get_all_provider_ids():
            key_layout = QHBoxLayout()
            key_edit = QLineEdit()
            key_edit.setEchoMode(QLineEdit.Password)
            key_edit.setPlaceholderText(f"Enter {get_provider_display_name(provider_id)} API key...")

            # Load existing key
            existing_key = self.config.get_api_key(provider_id)
            if existing_key:
                key_edit.setText(existing_key)

            key_layout.addWidget(key_edit)

            save_btn = QPushButton("Save")
            save_btn.clicked.connect(lambda checked, p=provider_id, e=key_edit: self.save_api_key(p, e.text()))
            key_layout.addWidget(save_btn)

            self.api_key_widgets[provider_id] = key_edit
            api_layout.addRow(f"{get_provider_display_name(provider_id)}:", key_layout)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Google Cloud Authentication section
        gcloud_group = QGroupBox("Google Cloud Authentication (Alternative)")
        gcloud_layout = QVBoxLayout()

        gcloud_help = QLabel(
            "For Google Gemini, you can use Google Cloud authentication instead of an API key.\n"
            "This uses your Google Cloud account credentials."
        )
        gcloud_help.setWordWrap(True)
        gcloud_layout.addWidget(gcloud_help)

        form_layout = QFormLayout()

        # Auth mode selection
        self.auth_mode_combo = QComboBox()
        self.auth_mode_combo.addItems(["API Key", "Google Cloud Account"])
        self.auth_mode_combo.currentTextChanged.connect(self.on_auth_mode_changed)

        # Load current auth mode
        auth_mode_internal = self.config.get_auth_mode("gemini")
        auth_mode_display = "Google Cloud Account" if auth_mode_internal == "gcloud" else "API Key"
        self.auth_mode_combo.setCurrentText(auth_mode_display)

        form_layout.addRow("Auth Mode:", self.auth_mode_combo)

        # Project ID display
        project_id = self.config.get_gcloud_project_id() or "Not set"
        self.project_id_label = QLabel(project_id)
        form_layout.addRow("Project ID:", self.project_id_label)

        # Status display
        self.gcloud_status_label = QLabel("Not checked")
        form_layout.addRow("Status:", self.gcloud_status_label)

        gcloud_layout.addLayout(form_layout)

        # Check status button
        check_status_btn = QPushButton("Check Google Cloud Status")
        check_status_btn.clicked.connect(self.check_gcloud_status)
        gcloud_layout.addWidget(check_status_btn)

        # Setup instructions
        self.gcloud_help_widget = QWidget()
        gcloud_help_layout = QVBoxLayout(self.gcloud_help_widget)
        gcloud_help_layout.setContentsMargins(0, 10, 0, 0)

        help_text = QLabel(
            "<b>Setup Instructions:</b><br>"
            "1. Install Google Cloud CLI: <a href='https://cloud.google.com/sdk/docs/install'>Download</a><br>"
            "2. Run: <code>gcloud auth application-default login</code><br>"
            "3. Set project: <code>gcloud config set project YOUR_PROJECT_ID</code><br>"
            "4. Enable APIs at <a href='https://console.cloud.google.com/apis/library'>Cloud Console</a>"
        )
        help_text.setTextFormat(Qt.RichText)
        help_text.setOpenExternalLinks(True)
        help_text.setWordWrap(True)
        gcloud_help_layout.addWidget(help_text)

        gcloud_layout.addWidget(self.gcloud_help_widget)

        # Initially hide/show based on auth mode
        self.gcloud_help_widget.setVisible(auth_mode_internal == "gcloud")

        gcloud_group.setLayout(gcloud_layout)
        layout.addWidget(gcloud_group)

        # Default settings section
        defaults_group = QGroupBox("Default Settings")
        defaults_layout = QFormLayout()

        defaults = self.config.get_enhancement_defaults()

        self.default_role = QLineEdit()
        self.default_role.setText(defaults.get("role", "an expert assistant"))
        defaults_layout.addRow("Default Role:", self.default_role)

        self.default_reasoning = QComboBox()
        self.default_reasoning.addItems(REASONING_MODES)
        self.default_reasoning.setCurrentText(defaults.get("reasoning", "Standard"))
        defaults_layout.addRow("Default Reasoning:", self.default_reasoning)

        self.default_verbosity = QComboBox()
        self.default_verbosity.addItems(VERBOSITY_LEVELS)
        self.default_verbosity.setCurrentText(defaults.get("verbosity", "medium"))
        defaults_layout.addRow("Default Verbosity:", self.default_verbosity)

        save_defaults_btn = QPushButton("Save Defaults")
        save_defaults_btn.clicked.connect(self.save_defaults)
        defaults_layout.addRow("", save_defaults_btn)

        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)

        layout.addStretch()
        self.tabs.addTab(tab, "Settings")

    def create_help_tab(self):
        """Create the help documentation tab."""
        help_tab = HelpTab(self.config)
        self.tabs.addTab(help_tab, "Help")

    def setup_hotkeys(self):
        """Setup keyboard shortcuts for the application."""
        # Tab navigation hotkeys (Enhance, History, Projects, Settings, Help)
        for i in range(5):
            shortcut = QShortcut(QKeySequence(f"Alt+{i+1}"), self)
            shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))

        # Copy shortcut (Ctrl+C)
        copy_shortcut = QShortcut(QKeySequence.Copy, self)
        copy_shortcut.activated.connect(self.copy_enhanced)

        # Save shortcut (Ctrl+S)
        save_shortcut = QShortcut(QKeySequence.Save, self)
        save_shortcut.activated.connect(self.save_enhanced)

        # Refresh history (F5)
        refresh_shortcut = QShortcut(QKeySequence.Refresh, self)
        refresh_shortcut.activated.connect(self.refresh_history)

        # New project (Ctrl+N)
        new_project_shortcut = QShortcut(QKeySequence.New, self)
        new_project_shortcut.activated.connect(self.create_project)

    def populate_roles(self):
        """Populate role combo with default and custom roles."""
        from datetime import datetime

        self.role_combo.clear()

        # Get custom roles from config
        custom_roles = self.config.get("custom_roles", [])

        # Combine default and custom roles
        all_roles = []

        # Add custom roles with metadata
        for role_data in custom_roles:
            if isinstance(role_data, dict):
                all_roles.append(role_data)
            else:
                # Legacy format - convert to dict
                all_roles.append({
                    "role": role_data,
                    "date_added": datetime.now().isoformat(),
                    "is_custom": True
                })

        # Add default roles
        for role in DEFAULT_ROLES:
            all_roles.append({
                "role": role,
                "date_added": "2025-01-01T00:00:00",
                "is_custom": False
            })

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_roles = []
        for role_data in all_roles:
            role_text = role_data["role"]
            if role_text not in seen:
                seen.add(role_text)
                unique_roles.append(role_data)

        # Store all roles
        self.all_roles = unique_roles

        # Apply current sort
        self.sort_roles(self.role_sort_combo.currentText() if hasattr(self, 'role_sort_combo') else "Name ↑")

    def sort_roles(self, sort_mode: str = "Name ↑"):
        """Sort roles based on the selected mode."""
        if not hasattr(self, 'all_roles'):
            return

        current_text = self.role_combo.currentText()

        if sort_mode == "Name ↑":
            sorted_roles = sorted(self.all_roles, key=lambda x: x["role"].lower())
        elif sort_mode == "Name ↓":
            sorted_roles = sorted(self.all_roles, key=lambda x: x["role"].lower(), reverse=True)
        elif sort_mode == "Date ↑":
            sorted_roles = sorted(self.all_roles, key=lambda x: x["date_added"])
        else:  # Date ↓
            sorted_roles = sorted(self.all_roles, key=lambda x: x["date_added"], reverse=True)

        # Update combo
        self.role_combo.clear()
        for role_data in sorted_roles:
            self.role_combo.addItem(role_data["role"])

        # Restore current selection
        if current_text:
            index = self.role_combo.findText(current_text)
            if index >= 0:
                self.role_combo.setCurrentIndex(index)

    def add_custom_role(self):
        """Add current role to custom roles list."""
        from datetime import datetime

        role_text = self.role_combo.currentText().strip()
        if not role_text:
            QMessageBox.warning(self, "Error", "Please enter a role first.")
            return

        # Check if already exists
        for role_data in self.all_roles:
            if role_data["role"].lower() == role_text.lower():
                QMessageBox.information(self, "Info", "This role already exists in the list.")
                return

        # Add to custom roles
        custom_roles = self.config.get("custom_roles", [])
        new_role = {
            "role": role_text,
            "date_added": datetime.now().isoformat(),
            "is_custom": True
        }
        custom_roles.append(new_role)
        self.config.set("custom_roles", custom_roles)
        self.config.save()

        # Refresh roles list
        self.populate_roles()

        # Select the newly added role
        index = self.role_combo.findText(role_text)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)

        QMessageBox.information(self, "Success", f"Role '{role_text}' added to custom roles!")

    def on_provider_changed(self, index):
        """Handle provider selection change."""
        provider_id = self.provider_combo.currentData()
        models = get_provider_models(provider_id)

        self.model_combo.clear()
        for model in models:
            self.model_combo.addItem(model)

    def add_attachments(self):
        """Add file attachments."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Attach")
        for file_path in files:
            self.attachments_list.addItem(file_path)

    def remove_attachments(self):
        """Remove selected attachments."""
        for item in self.attachments_list.selectedItems():
            self.attachments_list.takeItem(self.attachments_list.row(item))

    def enhance_prompt(self):
        """Enhance the prompt."""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt to enhance.")
            return

        provider_id = self.provider_combo.currentData()
        model = self.model_combo.currentText()

        # Check authentication (API key or cloud auth)
        auth_mode = self.config.get_auth_mode(provider_id)
        if auth_mode == "api-key":
            if not self.config.get_api_key(provider_id):
                QMessageBox.warning(self, "Error", f"API key for {get_provider_display_name(provider_id)} not configured. Please set it in Settings tab.")
                return
        elif auth_mode == "gcloud":
            # For cloud auth, check if authenticated
            from core.gcloud_utils import check_gcloud_auth_status
            is_authed, status_msg = check_gcloud_auth_status()
            if not is_authed:
                QMessageBox.warning(
                    self, "Error",
                    f"Google Cloud authentication required:\n\n{status_msg}\n\n"
                    "Please configure in Settings tab → Google Cloud Authentication."
                )
                return

        # Gather settings
        role = self.role_combo.currentText() or None
        reasoning = self.reasoning_combo.currentText() or None
        verbosity = self.verbosity_combo.currentText() or None
        tools = [tool for tool, cb in self.tool_checks.items() if cb.isChecked()] or None
        self_reflect = self.self_reflect_check.isChecked()
        meta_fix = self.meta_fix_check.isChecked()
        inputs = self.inputs_edit.text() or None
        deliverables = self.deliverables_edit.text() or None

        # Gather attachments
        attachments = []
        for i in range(self.attachments_list.count()):
            attachments.append(Path(self.attachments_list.item(i).text()))

        # Disable button
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setText("Enhancing...")

        # Create progress dialog
        self.progress = QProgressDialog("Enhancing prompt...", None, 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.show()

        # Start worker thread
        self.worker = EnhanceWorker(
            self.enhancer,
            original_prompt=prompt,
            provider=provider_id,
            model=model,
            role=role,
            reasoning=reasoning,
            verbosity=verbosity,
            tools=tools,
            self_reflect=self_reflect,
            meta_fix=meta_fix,
            inputs=inputs,
            deliverables=deliverables,
            attachments=attachments if attachments else None
        )
        self.worker.finished.connect(self.on_enhancement_complete)
        self.worker.error.connect(self.on_enhancement_error)
        self.worker.start()

    def on_enhancement_complete(self, result: Dict[str, Any]):
        """Handle enhancement completion."""
        self.progress.close()
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("Enhance Prompt")

        self.enhanced_output.setPlainText(result['enhanced_prompt'])
        self.current_result = result

        # Save to history
        self.history_manager.add_entry(result)

        # Show success message
        tokens = result.get('tokens_used', 'unknown')
        QMessageBox.information(self, "Success", f"Prompt enhanced successfully!\nTokens used: {tokens}")

        # Refresh history
        self.refresh_history()

    def on_enhancement_error(self, error: str):
        """Handle enhancement error."""
        logger.error(f"Enhancement error in UI: {error}")
        self.progress.close()
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("Enhance Prompt")
        QMessageBox.critical(self, "Error", f"Enhancement failed:\n{error}")

    def copy_enhanced(self):
        """Copy enhanced prompt to clipboard."""
        text = self.enhanced_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "Enhanced prompt copied to clipboard!")

    def save_enhanced(self):
        """Save enhanced prompt to file."""
        text = self.enhanced_output.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "No enhanced prompt to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Enhanced Prompt", "", "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)")
        if file_path:
            Path(file_path).write_text(text, encoding='utf-8')
            QMessageBox.information(self, "Saved", f"Enhanced prompt saved to {file_path}")

    def save_to_project(self):
        """Save current result to a project."""
        if not hasattr(self, 'current_result'):
            QMessageBox.warning(self, "Error", "No enhanced prompt to save.")
            return

        # Get project name from user
        from PySide6.QtWidgets import QInputDialog
        project_name, ok = QInputDialog.getText(self, "Save to Project", "Project name:")
        if ok and project_name:
            project = self.project_manager.get_project(project_name)
            if not project:
                project = self.project_manager.create_project(project_name)

            project.add_prompt(self.current_result)
            QMessageBox.information(self, "Saved", f"Saved to project: {project_name}")
            self.refresh_projects()

    def refresh_history(self):
        """Refresh history table."""
        query = self.history_search.text() or None
        provider = self.history_provider_filter.currentData()

        entries = self.history_manager.search_entries(query=query, provider=provider)

        self.history_table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            self.history_table.setItem(i, 0, QTableWidgetItem(entry.get('timestamp', '')))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{entry.get('provider')}/{entry.get('model')}"))

            prompt_preview = entry.get('original_prompt', '')[:100].replace('\n', ' ')
            self.history_table.setItem(i, 2, QTableWidgetItem(prompt_preview))

            tokens = str(entry.get('tokens_used', 'N/A'))
            self.history_table.setItem(i, 3, QTableWidgetItem(tokens))

    def load_history_entry(self):
        """Load selected history entry to details."""
        row = self.history_table.currentRow()
        if row < 0:
            return

        entries = self.history_manager.get_all_entries()
        if row < len(entries):
            entry = entries[row]
            details = f"Original Prompt:\n{entry.get('original_prompt', '')}\n\n"
            details += f"Enhanced Prompt:\n{entry.get('enhanced_prompt', '')}"
            self.history_details.setPlainText(details)

    def load_history_to_enhance(self):
        """Load history entry to enhance tab."""
        row = self.history_table.currentRow()
        if row < 0:
            return

        entries = self.history_manager.get_all_entries()
        if row < len(entries):
            entry = entries[row]
            self.prompt_input.setPlainText(entry.get('original_prompt', ''))
            self.enhanced_output.setPlainText(entry.get('enhanced_prompt', ''))
            self.tabs.setCurrentIndex(0)

    def clear_history(self):
        """Clear all history."""
        reply = QMessageBox.question(self, "Clear History", "Are you sure you want to clear all history?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            self.refresh_history()

    def export_history(self):
        """Export history to file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export History", "history.json",
                                                   "JSON Files (*.json);;JSONL Files (*.jsonl)")
        if file_path:
            format_type = 'jsonl' if file_path.endswith('.jsonl') else 'json'
            self.history_manager.export_history(Path(file_path), format_type)
            QMessageBox.information(self, "Exported", f"History exported to {file_path}")

    def refresh_projects(self):
        """Refresh projects list."""
        self.projects_list.clear()
        projects = self.project_manager.list_projects()

        if not projects:
            # Add a helpful message when no projects exist
            item = QListWidgetItem("No projects yet. Click 'New Project' to create one.")
            item.setFlags(Qt.ItemIsEnabled)  # Make it non-selectable
            self.projects_list.addItem(item)
        else:
            for project in projects:
                item = QListWidgetItem(f"{project['name']} ({project['prompt_count']} prompts)")
                item.setData(Qt.UserRole, project)
                self.projects_list.addItem(item)

    def on_project_selected(self, current, previous):
        """Handle project selection."""
        if not current:
            return

        project_data = current.data(Qt.UserRole)
        project = self.project_manager.get_project(project_data['name'])

        if project:
            self.project_name_label.setText(project.name)
            self.project_desc_label.setText(project.metadata.get('description', 'No description'))

            self.project_prompts_list.clear()
            prompts = project.get_all_prompts()
            for prompt in prompts:
                preview = prompt.get('original_prompt', '')[:80].replace('\n', ' ')
                item = QListWidgetItem(f"{prompt.get('timestamp', 'Unknown')}: {preview}...")
                item.setData(Qt.UserRole, prompt)
                self.project_prompts_list.addItem(item)

    def create_project(self):
        """Create a new project."""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name:
            try:
                self.project_manager.create_project(name)
                self.refresh_projects()
                QMessageBox.information(self, "Success", f"Project '{name}' created!")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def delete_project(self):
        """Delete selected project."""
        current = self.projects_list.currentItem()
        if not current:
            return

        project_data = current.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Delete Project",
                                    f"Are you sure you want to delete project '{project_data['name']}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.project_manager.delete_project(project_data['name'])
            self.refresh_projects()

    def load_project_prompt(self):
        """Load project prompt to enhance tab."""
        item = self.project_prompts_list.currentItem()
        if item:
            prompt_data = item.data(Qt.UserRole)
            self.prompt_input.setPlainText(prompt_data.get('original_prompt', ''))
            self.enhanced_output.setPlainText(prompt_data.get('enhanced_prompt', ''))
            self.tabs.setCurrentIndex(0)

    def export_project(self):
        """Export selected project."""
        current = self.projects_list.currentItem()
        if not current:
            return

        project_data = current.data(Qt.UserRole)
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Project",
                                                   f"{project_data['name']}.json",
                                                   "JSON Files (*.json)")
        if file_path:
            project = self.project_manager.get_project(project_data['name'])
            if project:
                project.export(Path(file_path))
                QMessageBox.information(self, "Exported", f"Project exported to {file_path}")

    def save_api_key(self, provider: str, key: str):
        """Save API key for provider."""
        if key.strip():
            logger.info(f"Saving API key for provider: {provider}")
            self.config.set_api_key(provider, key)
            self.config.save()
            QMessageBox.information(self, "Saved", f"API key saved for {get_provider_display_name(provider)}")
        else:
            logger.warning(f"Attempted to save empty API key for provider: {provider}")

    def save_defaults(self):
        """Save default settings."""
        defaults = {
            "role": self.default_role.text(),
            "reasoning": self.default_reasoning.currentText(),
            "verbosity": self.default_verbosity.currentText(),
            "tools": ["web", "code"],
            "self_reflect": True,
            "meta_fix": True
        }
        self.config.set_enhancement_defaults(defaults)
        self.config.save()
        QMessageBox.information(self, "Saved", "Default settings saved!")

    def on_auth_mode_changed(self, text: str):
        """Handle authentication mode change."""
        try:
            # Map display value to internal value
            if text == "Google Cloud Account":
                auth_mode = "gcloud"
                if hasattr(self, 'gcloud_help_widget'):
                    self.gcloud_help_widget.setVisible(True)
            else:
                auth_mode = "api-key"
                if hasattr(self, 'gcloud_help_widget'):
                    self.gcloud_help_widget.setVisible(False)

            # Save to config
            self.config.set_auth_mode("gemini", auth_mode)
            self.config.save()

            # Clear auth validation if switching modes
            self.config.set_auth_validated("gemini", False)
            if hasattr(self, 'gcloud_status_label'):
                self.gcloud_status_label.setText("Not checked")
        except Exception as e:
            logger.error(f"Error in on_auth_mode_changed: {e}", exc_info=True)

    def check_gcloud_status(self):
        """Check Google Cloud authentication status."""
        from core.gcloud_utils import check_gcloud_auth_status, get_gcloud_project_id

        self.gcloud_status_label.setText("Checking...")

        is_authed, status_msg = check_gcloud_auth_status()

        if is_authed:
            self.gcloud_status_label.setText(f"✓ {status_msg}")
            self.gcloud_status_label.setStyleSheet("color: green;")

            # Update project ID
            project_id = get_gcloud_project_id()
            if project_id:
                self.project_id_label.setText(project_id)
                self.config.set_gcloud_project_id(project_id)

            # Mark as validated
            self.config.set_auth_validated("gemini", True)
            self.config.save()

            QMessageBox.information(
                self,
                "Authentication OK",
                f"Google Cloud authentication is working!\n\n{status_msg}"
            )
        else:
            self.gcloud_status_label.setText(f"✗ Not authenticated")
            self.gcloud_status_label.setStyleSheet("color: red;")

            # Clear validation
            self.config.set_auth_validated("gemini", False)
            self.config.save()

            QMessageBox.warning(
                self,
                "Authentication Failed",
                f"Google Cloud authentication failed:\n\n{status_msg}\n\n"
                "Please follow the setup instructions below."
            )

    def load_ui_state(self):
        """Load UI state from config."""
        state = self.config.load_ui_state()

        # Restore window geometry
        if "geometry" in state:
            try:
                geometry_bytes = bytes.fromhex(state["geometry"])
                self.restoreGeometry(geometry_bytes)
            except:
                pass

        # Restore window state
        if "windowState" in state:
            try:
                window_state_bytes = bytes.fromhex(state["windowState"])
                self.restoreState(window_state_bytes)
            except:
                pass

        # Restore active tab
        if "active_tab" in state:
            self.tabs.setCurrentIndex(state["active_tab"])

        # Restore control panel settings
        if "provider" in state:
            index = self.provider_combo.findData(state["provider"])
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)

        if "model" in state:
            index = self.model_combo.findText(state["model"])
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

        if "role" in state:
            self.role_combo.setCurrentText(state["role"])

        if "reasoning" in state:
            index = self.reasoning_combo.findText(state["reasoning"])
            if index >= 0:
                self.reasoning_combo.setCurrentIndex(index)

        if "verbosity" in state:
            index = self.verbosity_combo.findText(state["verbosity"])
            if index >= 0:
                self.verbosity_combo.setCurrentIndex(index)

        if "tools" in state:
            for tool, checked in state["tools"].items():
                if tool in self.tool_checks:
                    self.tool_checks[tool].setChecked(checked)

        if "self_reflect" in state:
            self.self_reflect_check.setChecked(state["self_reflect"])

        if "meta_fix" in state:
            self.meta_fix_check.setChecked(state["meta_fix"])

    def closeEvent(self, event):
        """Handle window close event."""
        # Save UI state to config
        state = {
            "geometry": self.saveGeometry().hex(),
            "windowState": self.saveState().hex(),
            "active_tab": self.tabs.currentIndex(),
            "provider": self.provider_combo.currentData(),
            "model": self.model_combo.currentText(),
            "role": self.role_combo.currentText(),
            "reasoning": self.reasoning_combo.currentText(),
            "verbosity": self.verbosity_combo.currentText(),
            "tools": {tool: cb.isChecked() for tool, cb in self.tool_checks.items()},
            "self_reflect": self.self_reflect_check.isChecked(),
            "meta_fix": self.meta_fix_check.isChecked()
        }
        self.config.save_ui_state(state)
        event.accept()
