"""
File utilities module for VCV Rack Module Search.

This module provides common file operations and JSON handling utilities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from logger import get_logger, log_error
from exceptions import FileProcessingError


class FileUtils:
    """Utility class for common file operations."""

    def __init__(self):
        self.logger = get_logger()

    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Load JSON data from a file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data as a dictionary

        Raises:
            FileProcessingError: If file cannot be read or parsed
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError as e:
            log_error(f"File not found: {file_path}", e, self.logger)
            raise FileProcessingError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            log_error(f"Error decoding JSON from {file_path}", e, self.logger)
            raise FileProcessingError(f"Error decoding JSON from {file_path}")

    def save_json(self, data: Any, file_path: Path, indent: int = None) -> None:
        """
        Save data to a JSON file.

        Args:
            data: Data to save
            file_path: Path where to save the file
            indent: JSON indentation level (None for compact)

        Raises:
            FileProcessingError: If file cannot be written
        """
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=indent)
            self.logger.debug(f"Saved JSON data to {file_path}")
        except IOError as e:
            log_error(f"Error writing JSON to {file_path}", e, self.logger)
            raise FileProcessingError(f"Error writing JSON to {file_path}")

    def ensure_directory_exists(self, directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Path to the directory
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
        except OSError as e:
            log_error(f"Error creating directory {directory}", e, self.logger)
            raise FileProcessingError(f"Error creating directory {directory}")

    def copy_file(self, source: Path, destination: Path) -> None:
        """
        Copy a file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Raises:
            FileProcessingError: If file cannot be copied
        """
        import shutil

        try:
            # Ensure destination directory exists
            self.ensure_directory_exists(destination.parent)

            shutil.copy2(source, destination)
            self.logger.debug(f"Copied {source} to {destination}")
        except (IOError, OSError) as e:
            log_error(f"Error copying {source} to {destination}", e, self.logger)
            raise FileProcessingError(f"Error copying {source} to {destination}")

    def file_exists(self, file_path: Path) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return file_path.exists() and file_path.is_file()

    def get_file_size(self, file_path: Path) -> int:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes

        Raises:
            FileProcessingError: If file cannot be accessed
        """
        try:
            return file_path.stat().st_size
        except OSError as e:
            log_error(f"Error getting file size for {file_path}", e, self.logger)
            raise FileProcessingError(f"Error getting file size for {file_path}")

    def list_files_with_pattern(self, directory: Path, pattern: str) -> List[Path]:
        """
        List all files in a directory matching a pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern to match

        Returns:
            List of matching file paths
        """
        try:
            return list(directory.rglob(pattern))
        except OSError as e:
            log_error(f"Error listing files in {directory} with pattern {pattern}", e, self.logger)
            return []