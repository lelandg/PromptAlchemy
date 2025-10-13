"""Main CLI interface for PromptAlchemy."""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import ConfigManager
from core.enhancer import PromptEnhancer
from core.history import HistoryManager
from core.projects import ProjectManager
from core.llm_models import get_all_provider_ids, get_provider_models, get_provider_display_name
from core.version import __version__

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def setup_argparse() -> argparse.ArgumentParser:
    """Set up argument parser with all CLI options."""
    parser = argparse.ArgumentParser(
        description=f"PromptAlchemy v{__version__} - Transform simple prompts into sophisticated LLM prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance a prompt
  promptalchemy enhance "Create a todo app" -p openai -m gpt-4o-mini

  # Enhance with custom settings
  promptalchemy enhance "Build an API" -r "senior backend engineer" --reasoning "Deep Think"

  # Read from file and output to file
  promptalchemy enhance -i prompt.txt -o enhanced.txt

  # List history
  promptalchemy history list --limit 10

  # Create a project
  promptalchemy project create "My Project"
        """
    )

    parser.add_argument('--version', action='version', version=f'PromptAlchemy v{__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Enhance command
    enhance_parser = subparsers.add_parser('enhance', help='Enhance a prompt')
    enhance_parser.add_argument('prompt', nargs='?', help='Prompt to enhance')
    enhance_parser.add_argument('-i', '--input', type=Path, help='Input file containing prompt')
    enhance_parser.add_argument('-o', '--output', type=Path, help='Output file for enhanced prompt')
    enhance_parser.add_argument('-p', '--provider', default='openai', help='LLM provider (default: openai)')
    enhance_parser.add_argument('--auth-mode', choices=['api-key', 'gcloud'], help='Authentication mode (default: api-key for most, config for gemini)')
    enhance_parser.add_argument('-m', '--model', help='Model name (default: provider default)')
    enhance_parser.add_argument('-r', '--role', help='Role specification')
    enhance_parser.add_argument('--reasoning', choices=['Standard', 'Deep Think', 'Ultra Think', 'Chain of Thought', 'Step by Step'],
                                help='Reasoning mode')
    enhance_parser.add_argument('-v', '--verbosity', choices=['minimal', 'concise', 'medium', 'detailed', 'comprehensive'],
                                help='Verbosity level')
    enhance_parser.add_argument('-t', '--tools', nargs='+', help='Tools to include (e.g., web code pdf)')
    enhance_parser.add_argument('--self-reflect', action='store_true', help='Enable self-reflection')
    enhance_parser.add_argument('--no-self-reflect', action='store_true', help='Disable self-reflection')
    enhance_parser.add_argument('--meta-fix', action='store_true', help='Enable meta-fixing')
    enhance_parser.add_argument('--no-meta-fix', action='store_true', help='Disable meta-fixing')
    enhance_parser.add_argument('--inputs', help='Additional inputs specification')
    enhance_parser.add_argument('--deliverables', help='Deliverables specification')
    enhance_parser.add_argument('-a', '--attach', type=Path, action='append', help='Attach files (can be used multiple times)')
    enhance_parser.add_argument('--temperature', type=float, default=0.7, help='Model temperature (default: 0.7)')
    enhance_parser.add_argument('--project', help='Save to project collection')

    # History command
    history_parser = subparsers.add_parser('history', help='Manage history')
    history_subparsers = history_parser.add_subparsers(dest='history_command')

    history_list = history_subparsers.add_parser('list', help='List history entries')
    history_list.add_argument('-l', '--limit', type=int, help='Maximum number of entries')
    history_list.add_argument('-q', '--query', help='Search query')
    history_list.add_argument('-p', '--provider', help='Filter by provider')
    history_list.add_argument('-m', '--model', help='Filter by model')

    history_show = history_subparsers.add_parser('show', help='Show specific entry')
    history_show.add_argument('index', type=int, help='Entry index (0 = most recent)')

    history_export = history_subparsers.add_parser('export', help='Export history')
    history_export.add_argument('output', type=Path, help='Output file')
    history_export.add_argument('-f', '--format', choices=['json', 'jsonl'], default='json', help='Export format')

    history_clear = history_subparsers.add_parser('clear', help='Clear all history')

    # Project command
    project_parser = subparsers.add_parser('project', help='Manage projects')
    project_subparsers = project_parser.add_subparsers(dest='project_command')

    project_list = project_subparsers.add_parser('list', help='List all projects')

    project_create = project_subparsers.add_parser('create', help='Create a project')
    project_create.add_argument('name', help='Project name')
    project_create.add_argument('-d', '--description', help='Project description')

    project_show = project_subparsers.add_parser('show', help='Show project prompts')
    project_show.add_argument('name', help='Project name')

    project_export = project_subparsers.add_parser('export', help='Export project')
    project_export.add_argument('name', help='Project name')
    project_export.add_argument('output', type=Path, help='Output file')

    # Providers command
    providers_parser = subparsers.add_parser('providers', help='List available providers and models')

    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command')

    config_set_key = config_subparsers.add_parser('set-key', help='Set API key')
    config_set_key.add_argument('provider', help='Provider name')
    config_set_key.add_argument('key', help='API key')

    config_show = config_subparsers.add_parser('show', help='Show configuration')

    return parser


def cmd_enhance(args, config: ConfigManager):
    """Handle enhance command."""
    # Handle auth mode if specified
    if args.auth_mode:
        config.set_auth_mode(args.provider, args.auth_mode)
        config.save()

    # Get prompt
    if args.input:
        prompt = args.input.read_text(encoding='utf-8')
    elif args.prompt:
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read()
    else:
        print("Error: No prompt provided. Use positional argument, -i/--input, or pipe to stdin", file=sys.stderr)
        return 1

    # Get model
    model = args.model
    if not model:
        models = get_provider_models(args.provider)
        model = models[0] if models else 'gpt-4o-mini'

    # Determine self-reflect and meta-fix
    self_reflect = None
    if args.self_reflect:
        self_reflect = True
    elif args.no_self_reflect:
        self_reflect = False

    meta_fix = None
    if args.meta_fix:
        meta_fix = True
    elif args.no_meta_fix:
        meta_fix = False

    # Create enhancer
    enhancer = PromptEnhancer(config)

    try:
        logger.info(f"Enhancing prompt with {args.provider}/{model}...")

        result = enhancer.enhance_prompt(
            original_prompt=prompt,
            provider=args.provider,
            model=model,
            role=args.role,
            reasoning=args.reasoning,
            verbosity=args.verbosity,
            tools=args.tools,
            self_reflect=self_reflect,
            meta_fix=meta_fix,
            inputs=args.inputs,
            deliverables=args.deliverables,
            attachments=args.attach,
            temperature=args.temperature
        )

        enhanced = result['enhanced_prompt']

        # Output
        if args.output:
            args.output.write_text(enhanced, encoding='utf-8')
            logger.info(f"Enhanced prompt saved to {args.output}")
        else:
            print("\n" + "="*80)
            print("ENHANCED PROMPT:")
            print("="*80)
            print(enhanced)
            print("="*80 + "\n")

        # Save to history
        history = HistoryManager(config.get_history_path())
        history.add_entry(result)

        # Save to project if specified
        if args.project:
            project_manager = ProjectManager(config.get_projects_dir())
            project = project_manager.get_project(args.project)
            if not project:
                project = project_manager.create_project(args.project)
            project.add_prompt(result)
            logger.info(f"Saved to project: {args.project}")

        if result.get('tokens_used'):
            logger.info(f"Tokens used: {result['tokens_used']}")

        return 0

    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        return 1


def cmd_history(args, config: ConfigManager):
    """Handle history command."""
    history = HistoryManager(config.get_history_path())

    if args.history_command == 'list':
        entries = history.search_entries(
            query=args.query,
            provider=args.provider,
            model=args.model
        )

        if args.limit:
            entries = entries[:args.limit]

        if not entries:
            print("No history entries found.")
            return 0

        print(f"\nFound {len(entries)} entries:\n")
        for i, entry in enumerate(entries):
            print(f"[{i}] {entry.get('timestamp', 'Unknown')} - {entry.get('provider')}/{entry.get('model')}")
            prompt_preview = entry.get('original_prompt', '')[:60].replace('\n', ' ')
            print(f"    {prompt_preview}...")
            print()

    elif args.history_command == 'show':
        entry = history.get_entry_by_index(args.index)
        if not entry:
            print(f"Entry {args.index} not found.")
            return 1

        print("\n" + "="*80)
        print("ORIGINAL PROMPT:")
        print("="*80)
        print(entry.get('original_prompt', ''))
        print("\n" + "="*80)
        print("ENHANCED PROMPT:")
        print("="*80)
        print(entry.get('enhanced_prompt', ''))
        print("="*80 + "\n")
        print(f"Provider: {entry.get('provider')} / Model: {entry.get('model')}")
        print(f"Timestamp: {entry.get('timestamp')}")
        if entry.get('tokens_used'):
            print(f"Tokens: {entry['tokens_used']}")

    elif args.history_command == 'export':
        history.export_history(args.output, args.format)
        logger.info(f"History exported to {args.output}")

    elif args.history_command == 'clear':
        confirm = input("Are you sure you want to clear all history? (yes/no): ")
        if confirm.lower() == 'yes':
            history.clear_history()
            logger.info("History cleared")
        else:
            print("Cancelled")

    return 0


def cmd_project(args, config: ConfigManager):
    """Handle project command."""
    project_manager = ProjectManager(config.get_projects_dir())

    if args.project_command == 'list':
        projects = project_manager.list_projects()
        if not projects:
            print("No projects found.")
            return 0

        print(f"\nFound {len(projects)} projects:\n")
        for proj in projects:
            print(f"  {proj['name']}")
            if proj.get('description'):
                print(f"    {proj['description']}")
            print(f"    Created: {proj.get('created', 'Unknown')} | Prompts: {proj.get('prompt_count', 0)}")
            if proj.get('tags'):
                print(f"    Tags: {', '.join(proj['tags'])}")
            print()

    elif args.project_command == 'create':
        try:
            project = project_manager.create_project(args.name)
            if args.description:
                project.set_description(args.description)
            logger.info(f"Created project: {args.name}")
        except ValueError as e:
            logger.error(str(e))
            return 1

    elif args.project_command == 'show':
        project = project_manager.get_project(args.name)
        if not project:
            logger.error(f"Project '{args.name}' not found")
            return 1

        prompts = project.get_all_prompts()
        print(f"\nProject: {project.name}")
        print(f"Description: {project.metadata.get('description', 'N/A')}")
        print(f"Prompts: {len(prompts)}\n")

        for i, prompt in enumerate(prompts):
            print(f"[{i}] {prompt.get('timestamp', 'Unknown')}")
            preview = prompt.get('original_prompt', '')[:60].replace('\n', ' ')
            print(f"    {preview}...")
            print()

    elif args.project_command == 'export':
        project = project_manager.get_project(args.name)
        if not project:
            logger.error(f"Project '{args.name}' not found")
            return 1

        project.export(args.output)
        logger.info(f"Project exported to {args.output}")

    return 0


def cmd_providers(args, config: ConfigManager):
    """Handle providers command."""
    print("\nAvailable Providers:\n")

    for provider_id in get_all_provider_ids():
        display_name = get_provider_display_name(provider_id)
        models = get_provider_models(provider_id)

        print(f"{display_name} ({provider_id}):")
        for model in models:
            print(f"  - {model}")
        print()

    return 0


def cmd_config(args, config: ConfigManager):
    """Handle config command."""
    if args.config_command == 'set-key':
        config.set_api_key(args.provider, args.key)
        config.save()
        logger.info(f"API key set for {args.provider}")

    elif args.config_command == 'show':
        print("\nConfiguration:")
        print(f"  Config directory: {config.config_dir}")
        print(f"  Default provider: {config.get('default_provider', 'openai')}")
        print(f"  Default model: {config.get('default_model', 'gpt-4o-mini')}")
        print("\nEnhancement Defaults:")
        defaults = config.get_enhancement_defaults()
        for key, value in defaults.items():
            print(f"  {key}: {value}")

    return 0


def print_header():
    """Print CLI header with version."""
    print(f"\nPromptAlchemy v{__version__} - LLM Prompt Enhancer")
    print("=" * 50 + "\n")


def main():
    """Main CLI entry point."""
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Print header (except for --version flag)
    if not hasattr(args, 'version'):
        print_header()

    # Initialize config
    config = ConfigManager()

    # Route to command handlers
    if args.command == 'enhance':
        return cmd_enhance(args, config)
    elif args.command == 'history':
        return cmd_history(args, config)
    elif args.command == 'project':
        return cmd_project(args, config)
    elif args.command == 'providers':
        return cmd_providers(args, config)
    elif args.command == 'config':
        return cmd_config(args, config)

    return 0


if __name__ == '__main__':
    sys.exit(main())
