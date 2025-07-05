"""
Data parsing module for VCV Rack Module Search.

This module handles JSON parsing and filtering of VCV Rack plugin manifests.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from config import MINIMUM_VERSION, EXCLUDED_PLUGINS
from logger import get_logger, log_error, log_progress


class PluginDataParser:
    """Handles parsing and filtering of VCV Rack plugin manifests."""
    
    def __init__(self):
        self.logger = get_logger()
    
    def parse_plugin_manifest(self, manifest_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a plugin manifest file and extract module information.
        
        Args:
            manifest_path: Path to the plugin manifest JSON file
            
        Returns:
            List of module dictionaries with filtered and validated data
            
        Raises:
            DataParsingError: If JSON is invalid or required fields are missing
        """
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            log_error(f"Error decoding JSON from {manifest_path}", e, self.logger)
            return []
        except FileNotFoundError as e:
            log_error(f"File not found: {manifest_path}", e, self.logger)
            return []
        
        return self._extract_module_data(data)
    
    def _extract_module_data(self, plugin_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and filter module data from plugin manifest.
        
        Args:
            plugin_data: Raw plugin manifest data
            
        Returns:
            List of filtered module dictionaries
        """
        # Check plugin version
        version = plugin_data.get("version")
        if version < MINIMUM_VERSION:
            return []
        
        # Check if plugin is excluded
        plugin_slug = plugin_data.get("slug")
        if plugin_slug in EXCLUDED_PLUGINS:
            return []
        
        plugin_name = plugin_data.get("name")
        modules = plugin_data.get("modules", [])
        
        return [
            self._create_module_info(plugin_name, plugin_slug, module)
            for module in modules
            if self._is_valid_module(module)
        ]
    
    def _is_valid_module(self, module: Dict[str, Any]) -> bool:
        """
        Check if a module should be included in the output.
        
        Args:
            module: Module data dictionary
            
        Returns:
            True if module should be included, False otherwise
        """
        return not (module.get("hidden") or module.get("deprecated"))
    
    def _create_module_info(self, plugin_name: str, plugin_slug: str, module: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized module information dictionary.
        
        Args:
            plugin_name: Name of the plugin
            plugin_slug: Slug of the plugin
            module: Raw module data
            
        Returns:
            Standardized module information dictionary
        """
        return {
            "plugin_name": plugin_name,
            "plugin_slug": plugin_slug,
            "module_name": module.get("name"),
            "module_slug": module.get("slug"),
            "description": module.get("description"),
            "tags": module.get("tags", []),
        }
    
    def parse_all_manifests(self, manifests_dir: Path) -> List[Dict[str, Any]]:
        """
        Parse all plugin manifests in the specified directory.
        
        Args:
            manifests_dir: Directory containing plugin manifest files
            
        Returns:
            List of all valid modules from all plugins
        """
        all_modules = []
        json_files = list(manifests_dir.rglob("*.json"))
        
        for i, manifest_path in enumerate(json_files):
            modules = self.parse_plugin_manifest(manifest_path)
            all_modules.extend(modules)
            
            # Log progress every 50 files
            if i % 50 == 0:
                log_progress(i + 1, len(json_files), "Parsing manifests", self.logger)
        
        return all_modules