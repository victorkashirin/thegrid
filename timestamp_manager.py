"""
Timestamp management module for VCV Rack Module Search.

This module handles reading and processing build timestamps from manifest cache.
"""

import json
from typing import Dict

from config import MANIFESTS_CACHE_FILE
from logger import get_logger, log_error
from exceptions import FileProcessingError


class TimestampManager:
    """Handles reading and processing build timestamps from VCV library manifest cache."""

    def __init__(self):
        self.logger = get_logger()

    def get_build_timestamps(self) -> Dict[str, int]:
        """
        Load build timestamps from the manifest cache file.

        Returns:
            Dictionary mapping plugin slugs to their build timestamps

        Raises:
            FileProcessingError: If cache file cannot be read or parsed
        """
        try:
            with open(MANIFESTS_CACHE_FILE, "r") as f:
                manifest_cache = json.load(f)

            return {
                slug: data.get("buildTimestamp", -1)
                for slug, data in manifest_cache.items()
            }

        except FileNotFoundError as e:
            log_error(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}", e, self.logger)
            return {}
        except json.JSONDecodeError as e:
            log_error(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}", e, self.logger)
            return {}

    def get_module_timestamps(self) -> Dict[str, Dict[str, int]]:
        """
        Load module creation timestamps from the manifest cache file.

        Returns:
            Nested dictionary mapping plugin slugs to module slugs to creation timestamps

        Raises:
            FileProcessingError: If cache file cannot be read or parsed
        """
        try:
            with open(MANIFESTS_CACHE_FILE, "r") as f:
                manifest_cache = json.load(f)

            module_timestamps = {}
            for plugin_slug, plugin_data in manifest_cache.items():
                modules = plugin_data.get("modules", {})
                module_timestamps[plugin_slug] = {
                    module_slug: module_data.get("creationTimestamp")
                    for module_slug, module_data in modules.items()
                }

            return module_timestamps

        except FileNotFoundError as e:
            log_error(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}", e, self.logger)
            raise FileProcessingError(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}")
        except json.JSONDecodeError as e:
            log_error(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}", e, self.logger)
            raise FileProcessingError(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}")

    def get_module_timestamp(self, plugin_slug: str, module_slug: str, module_timestamps: Dict[str, Dict[str, int]]) -> int:
        """
        Get the creation timestamp for a specific module.

        Args:
            plugin_slug: Plugin identifier
            module_slug: Module identifier
            module_timestamps: Nested dictionary of timestamps

        Returns:
            Creation timestamp for the module, or None if not found
        """
        try:
            return module_timestamps[plugin_slug][module_slug]
        except KeyError:
            log_error(f"Missing timestamp for {plugin_slug}/{module_slug}", logger=self.logger)
            return None