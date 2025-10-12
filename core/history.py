"""History management for PromptAlchemy."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages enhancement history."""

    def __init__(self, history_path: Path):
        """
        Initialize history manager.

        Args:
            history_path: Path to history file (JSONL format)
        """
        self.history_path = history_path
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def add_entry(self, entry: Dict[str, Any]) -> None:
        """
        Add an entry to history.

        Args:
            entry: Enhancement entry dictionary
        """
        try:
            # Ensure timestamp
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now().isoformat()

            # Append to JSONL file
            with open(self.history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            logger.info("Added entry to history")
        except Exception as e:
            logger.error(f"Failed to add history entry: {e}")

    def get_all_entries(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all history entries.

        Args:
            limit: Maximum number of entries to return (most recent first)

        Returns:
            List of history entries
        """
        entries = []

        if not self.history_path.exists():
            return entries

        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in history: {line[:50]}")
                            continue

            # Sort by timestamp (most recent first)
            entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Apply limit if specified
            if limit:
                entries = entries[:limit]

            return entries

        except Exception as e:
            logger.error(f"Failed to read history: {e}")
            return []

    def search_entries(
        self,
        query: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search history entries.

        Args:
            query: Text to search in prompts
            provider: Filter by provider
            model: Filter by model
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)

        Returns:
            List of matching history entries
        """
        all_entries = self.get_all_entries()
        filtered = []

        for entry in all_entries:
            # Apply filters
            if provider and entry.get("provider") != provider:
                continue

            if model and entry.get("model") != model:
                continue

            if start_date and entry.get("timestamp", "") < start_date:
                continue

            if end_date and entry.get("timestamp", "") > end_date:
                continue

            if query:
                query_lower = query.lower()
                original = entry.get("original_prompt", "").lower()
                enhanced = entry.get("enhanced_prompt", "").lower()
                if query_lower not in original and query_lower not in enhanced:
                    continue

            filtered.append(entry)

        return filtered

    def get_entry_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific entry by index.

        Args:
            index: Entry index (0 = most recent)

        Returns:
            History entry or None if not found
        """
        entries = self.get_all_entries()
        if 0 <= index < len(entries):
            return entries[index]
        return None

    def clear_history(self) -> None:
        """Clear all history."""
        try:
            if self.history_path.exists():
                self.history_path.unlink()
            logger.info("History cleared")
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")

    def export_history(self, output_path: Path, format: str = "json") -> None:
        """
        Export history to a file.

        Args:
            output_path: Path to output file
            format: Export format ('json' or 'jsonl')
        """
        entries = self.get_all_entries()

        try:
            if format == "json":
                output_path.write_text(
                    json.dumps(entries, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
            else:  # jsonl
                with open(output_path, "w", encoding="utf-8") as f:
                    for entry in entries:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            logger.info(f"Exported {len(entries)} entries to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            raise
