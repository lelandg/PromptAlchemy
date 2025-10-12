"""Configuration management for PromptAlchemy."""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Any

from .constants import APP_NAME, PROVIDER_KEY_URLS
from .security import secure_storage

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration and persistence."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / "config.json"
        self.state_path = self.config_dir / "state.json"
        self.config = self._load_config()

        # Try to import ImageAI auth if available
        self._import_imageai_auth()

    def _get_config_dir(self) -> Path:
        """Get platform-specific configuration directory."""
        system = platform.system()
        home = Path.home()

        if system == "Windows":
            base = Path(os.getenv("APPDATA", home / "AppData" / "Roaming"))
            return base / APP_NAME
        elif system == "Darwin":  # macOS
            return home / "Library" / "Application Support" / APP_NAME
        else:  # Linux/Unix
            base = Path(os.getenv("XDG_CONFIG_HOME", home / ".config"))
            return base / APP_NAME

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from disk."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding="utf-8"))
            except (OSError, IOError, json.JSONDecodeError):
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "providers": {},
            "default_provider": "openai",
            "default_model": "gpt-4o-mini",
            "enhancement_defaults": {
                "role": "an expert assistant",
                "reasoning": "Standard",
                "verbosity": "medium",
                "tools": ["web", "code"],
                "self_reflect": True,
                "meta_fix": True
            }
        }

    def _import_imageai_auth(self) -> None:
        """Try to import authentication from ImageAI if available."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Try multiple locations for ImageAI config
            imageai_config_paths = []

            # 1. Same parent directory (Linux/Mac standard location)
            imageai_config_dir = self._get_config_dir().parent / "ImageAI"
            imageai_config_paths.append(imageai_config_dir / "config.json")

            # 2. Windows AppData location (for WSL cross-platform access)
            system = platform.system()
            if system == "Linux" and "microsoft" in platform.uname().release.lower():
                # We're in WSL, check Windows AppData
                try:
                    import glob
                    windows_appdata_pattern = "/mnt/c/Users/*/AppData/Roaming/ImageAI/config.json"
                    windows_configs = glob.glob(windows_appdata_pattern)
                    imageai_config_paths.extend([Path(p) for p in windows_configs])
                except Exception as e:
                    logger.debug(f"Error checking Windows AppData: {e}")

            # Find first existing config with actual data
            imageai_config_path = None
            imageai_config = None
            for path in imageai_config_paths:
                if path.exists():
                    try:
                        test_config = json.loads(path.read_text(encoding="utf-8"))
                        # Check if config has any useful data (not just empty {})
                        if test_config and (test_config.get("providers") or test_config.get("auth_mode") or test_config.get("gcloud_project_id")):
                            imageai_config_path = path
                            imageai_config = test_config
                            logger.info(f"Found ImageAI config with data at: {path}")
                            break
                        else:
                            logger.debug(f"Config at {path} is empty, skipping")
                    except Exception as e:
                        logger.debug(f"Error reading config at {path}: {e}")

            if not imageai_config_path or not imageai_config:
                logger.debug("No ImageAI config with data found for import")
                return

            # Track if we imported anything
            imported = False

            # Import provider API keys from file-based storage if not already present
            providers = imageai_config.get("providers", {})
            for provider, provider_config in providers.items():
                # Only import if we don't already have this key
                if not self.get_api_key(provider):
                    if "api_key" in provider_config and provider_config["api_key"]:
                        self.set_api_key(provider, provider_config["api_key"])
                        imported = True

            # Import Google Cloud auth settings
            if "auth_mode" in imageai_config:
                # Only import if we don't have auth configured
                if not self.config.get("auth_mode"):
                    auth_mode = imageai_config["auth_mode"]
                    # Normalize auth_mode values
                    if auth_mode in ["api_key", "API Key"]:
                        self.config["auth_mode"] = "api-key"
                    elif auth_mode == "Google Cloud Account":
                        self.config["auth_mode"] = "gcloud"
                    else:
                        self.config["auth_mode"] = auth_mode
                    imported = True

            # Import Google Cloud project ID
            if "gcloud_project_id" in imageai_config:
                if not self.config.get("gcloud_project_id"):
                    self.config["gcloud_project_id"] = imageai_config["gcloud_project_id"]
                    imported = True

            # Import Google Cloud auth validation status
            if "gcloud_auth_validated" in imageai_config:
                if not self.config.get("gcloud_auth_validated"):
                    self.config["gcloud_auth_validated"] = imageai_config["gcloud_auth_validated"]
                    imported = True

            # Save if we imported anything
            if imported:
                self.save()
        except Exception as e:
            # Log but don't fail - not critical
            import logging
            logging.debug(f"Failed to import ImageAI auth: {e}")
            pass

    def save(self) -> None:
        """Save current configuration to disk."""
        try:
            self.config_path.write_text(
                json.dumps(self.config, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}", exc_info=True)
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        providers = self.config.get("providers", {})
        return providers.get(provider, {})

    def set_provider_config(self, provider: str, config: Dict[str, Any]) -> None:
        """Set provider-specific configuration."""
        if "providers" not in self.config:
            self.config["providers"] = {}
        self.config["providers"][provider] = config

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        # Try keyring first (most secure)
        key = secure_storage.retrieve_key(provider)
        if key:
            return key

        # Check provider-specific config
        provider_config = self.get_provider_config(provider)
        if "api_key" in provider_config:
            return provider_config["api_key"]

        return None

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a provider."""
        logger.info(f"Setting API key for provider: {provider}")

        # Try to store in keyring first (most secure)
        stored_in_keyring = secure_storage.store_key(provider, api_key)

        # If keyring storage failed or not available, fall back to file storage
        if not stored_in_keyring:
            logger.debug(f"Keyring not available, using file storage for {provider}")
            provider_config = self.get_provider_config(provider)
            provider_config["api_key"] = api_key
            self.set_provider_config(provider, provider_config)
        else:
            logger.debug(f"API key stored in keyring for {provider}")

    def get_auth_mode(self, provider: str = "gemini") -> str:
        """
        Get authentication mode for a provider.

        Args:
            provider: Provider name (default: gemini for Google)

        Returns:
            Authentication mode: 'api-key' or 'gcloud'
        """
        if provider in ["gemini", "google"]:
            return self.config.get("auth_mode", "api-key")
        return "api-key"

    def set_auth_mode(self, provider: str, mode: str) -> None:
        """
        Set authentication mode for a provider.

        Args:
            provider: Provider name
            mode: Auth mode ('api-key' or 'gcloud')
        """
        if provider in ["gemini", "google"]:
            self.config["auth_mode"] = mode

    def get_auth_validated(self, provider: str = "gemini") -> bool:
        """
        Check if authentication has been validated for a provider.

        Args:
            provider: Provider name

        Returns:
            True if auth is validated
        """
        if provider in ["gemini", "google"]:
            return self.config.get("gcloud_auth_validated", False)
        return False

    def set_auth_validated(self, provider: str, validated: bool) -> None:
        """
        Set authentication validation status for a provider.

        Args:
            provider: Provider name
            validated: Whether auth is validated
        """
        if provider in ["gemini", "google"]:
            self.config["gcloud_auth_validated"] = validated
            # Also store the project ID if available
            if validated:
                try:
                    from .gcloud_utils import get_gcloud_project_id
                    project_id = get_gcloud_project_id()
                    if project_id:
                        self.config["gcloud_project_id"] = project_id
                except Exception:
                    pass

    def get_gcloud_project_id(self) -> Optional[str]:
        """Get the stored Google Cloud project ID."""
        return self.config.get("gcloud_project_id")

    def set_gcloud_project_id(self, project_id: str) -> None:
        """Set the Google Cloud project ID."""
        self.config["gcloud_project_id"] = project_id

    def get_enhancement_defaults(self) -> Dict[str, Any]:
        """Get default enhancement settings."""
        return self.config.get("enhancement_defaults", self._get_default_config()["enhancement_defaults"])

    def set_enhancement_defaults(self, defaults: Dict[str, Any]) -> None:
        """Set default enhancement settings."""
        self.config["enhancement_defaults"] = defaults

    def get_projects_dir(self) -> Path:
        """Get directory for project collections."""
        projects_dir = self.config_dir / "projects"
        projects_dir.mkdir(parents=True, exist_ok=True)
        return projects_dir

    def get_history_path(self) -> Path:
        """Get path to history file."""
        return self.config_dir / "history.jsonl"

    def save_ui_state(self, state: Dict[str, Any]) -> None:
        """Save UI state."""
        self.state_path.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8"
        )

    def load_ui_state(self) -> Dict[str, Any]:
        """Load UI state."""
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (OSError, IOError, json.JSONDecodeError):
                return {}
        return {}


def get_api_key_url(provider: str) -> str:
    """Get the API key documentation URL for a provider."""
    provider = (provider or "openai").strip().lower()
    return PROVIDER_KEY_URLS.get(provider, PROVIDER_KEY_URLS["openai"])
