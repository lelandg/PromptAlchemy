"""Project management for organizing prompt enhancements."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Project:
    """Represents a project collection of prompt enhancements."""

    def __init__(self, name: str, path: Path):
        """
        Initialize a project.

        Args:
            name: Project name
            path: Path to project directory
        """
        self.name = name
        self.path = path
        self.metadata_path = path / "project.json"
        self.prompts_path = path / "prompts.jsonl"

        # Create project directory
        self.path.mkdir(parents=True, exist_ok=True)

        # Load or create metadata
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load project metadata."""
        if self.metadata_path.exists():
            try:
                return json.loads(self.metadata_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Default metadata
        return {
            "name": self.name,
            "created": datetime.now().isoformat(),
            "description": "",
            "tags": []
        }

    def _save_metadata(self) -> None:
        """Save project metadata."""
        try:
            self.metadata_path.write_text(
                json.dumps(self.metadata, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to save project metadata: {e}")

    def set_description(self, description: str) -> None:
        """Set project description."""
        self.metadata["description"] = description
        self._save_metadata()

    def add_tags(self, *tags: str) -> None:
        """Add tags to project."""
        current_tags = set(self.metadata.get("tags", []))
        current_tags.update(tags)
        self.metadata["tags"] = sorted(current_tags)
        self._save_metadata()

    def remove_tags(self, *tags: str) -> None:
        """Remove tags from project."""
        current_tags = set(self.metadata.get("tags", []))
        current_tags.difference_update(tags)
        self.metadata["tags"] = sorted(current_tags)
        self._save_metadata()

    def add_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """
        Add a prompt enhancement to the project.

        Args:
            prompt_data: Enhancement data dictionary
        """
        try:
            # Ensure timestamp
            if "timestamp" not in prompt_data:
                prompt_data["timestamp"] = datetime.now().isoformat()

            # Add project reference
            prompt_data["project"] = self.name

            # Append to prompts file
            with open(self.prompts_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(prompt_data, ensure_ascii=False) + "\n")

            logger.info(f"Added prompt to project: {self.name}")
        except Exception as e:
            logger.error(f"Failed to add prompt to project: {e}")

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """Get all prompts in the project."""
        prompts = []

        if not self.prompts_path.exists():
            return prompts

        try:
            with open(self.prompts_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            prompts.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            # Sort by timestamp (most recent first)
            prompts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return prompts

        except Exception as e:
            logger.error(f"Failed to read project prompts: {e}")
            return []

    def export(self, output_path: Path) -> None:
        """
        Export project to a single JSON file.

        Args:
            output_path: Path to output file
        """
        export_data = {
            "metadata": self.metadata,
            "prompts": self.get_all_prompts()
        }

        try:
            output_path.write_text(
                json.dumps(export_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            logger.info(f"Exported project to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            raise


class ProjectManager:
    """Manages project collections."""

    def __init__(self, projects_dir: Path):
        """
        Initialize project manager.

        Args:
            projects_dir: Base directory for projects
        """
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str) -> Project:
        """
        Create a new project.

        Args:
            name: Project name

        Returns:
            New Project instance
        """
        # Sanitize project name for directory
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        project_path = self.projects_dir / safe_name

        if project_path.exists():
            raise ValueError(f"Project '{name}' already exists")

        return Project(name, project_path)

    def get_project(self, name: str) -> Optional[Project]:
        """
        Get an existing project.

        Args:
            name: Project name

        Returns:
            Project instance or None if not found
        """
        # Sanitize project name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        project_path = self.projects_dir / safe_name

        if not project_path.exists():
            return None

        return Project(name, project_path)

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.

        Returns:
            List of project metadata dictionaries
        """
        projects = []

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                metadata_path = project_dir / "project.json"
                if metadata_path.exists():
                    try:
                        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                        # Add prompt count
                        prompts_path = project_dir / "prompts.jsonl"
                        if prompts_path.exists():
                            with open(prompts_path, "r", encoding="utf-8") as f:
                                metadata["prompt_count"] = sum(1 for _ in f)
                        else:
                            metadata["prompt_count"] = 0
                        projects.append(metadata)
                    except Exception:
                        continue

        # Sort by creation date (most recent first)
        projects.sort(key=lambda x: x.get("created", ""), reverse=True)
        return projects

    def delete_project(self, name: str) -> bool:
        """
        Delete a project.

        Args:
            name: Project name

        Returns:
            True if deleted successfully
        """
        project = self.get_project(name)
        if not project:
            return False

        try:
            # Delete all files in project directory
            for file in project.path.iterdir():
                file.unlink()

            # Delete directory
            project.path.rmdir()
            logger.info(f"Deleted project: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False
