"""
Search file generation module for VCV Rack Module Search.

This module creates the optimized search data structure for the web interface.
"""

import math
from typing import List, Dict, Any
from PIL import Image

from config import (
    PARSED_PLUGINS_FILE,
    SEARCH_FILE,
    CACHE_DIR,
    PIXELS_PER_HP,
    SEARCH_HEADERS
)
from logger import get_logger, log_operation_start, log_operation_complete, log_error
from timestamp_manager import TimestampManager
from file_utils import FileUtils


class SearchFileGenerator:
    """Generates optimized search data file for the web interface."""

    def __init__(self):
        self.logger = get_logger()
        self.timestamp_manager = TimestampManager()
        self.file_utils = FileUtils()

    def generate_search_file(self) -> None:
        """Generate optimized search data file."""
        log_operation_start("Generating search file", self.logger)

        # Load module data
        modules = self._load_module_data()

        # Get module timestamps
        module_timestamps = self.timestamp_manager.get_module_timestamps()

        # Process modules with timestamps and sizes
        processed_modules = self._process_modules(modules, module_timestamps)

        # Convert to optimized array format
        search_data = self._create_search_data(processed_modules)

        # Save search file
        self.file_utils.save_json(search_data, SEARCH_FILE)

        log_operation_complete(f"Generated search file with {len(processed_modules)} modules", self.logger)

    def _load_module_data(self) -> List[Dict[str, Any]]:
        """
        Load and validate module data from parsed plugins file.

        Returns:
            List of module dictionaries

        Raises:
            FileProcessingError: If file cannot be loaded
        """
        return self.file_utils.load_json(PARSED_PLUGINS_FILE)

    def _process_modules(self, modules: List[Dict[str, Any]], module_timestamps: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """
        Process modules by adding timestamps and calculating sizes.

        Args:
            modules: List of module dictionaries
            module_timestamps: Nested dictionary of module timestamps

        Returns:
            List of processed module dictionaries
        """
        processed_modules = []

        for i, module in enumerate(modules):
            plugin_slug = module["plugin_slug"]
            module_slug = module["module_slug"]

            # Get module timestamp
            timestamp = self.timestamp_manager.get_module_timestamp(
                plugin_slug, module_slug, module_timestamps
            )

            # Calculate module size
            module_size = self._calculate_module_size(plugin_slug, module_slug)

            # Create processed module data
            processed_module = module.copy()
            processed_module["timestamp"] = timestamp
            processed_module["size"] = module_size

            processed_modules.append(processed_module)

            # Log progress every 100 modules
            if i % 100 == 0:
                self.logger.info(f"Processed {i + 1}/{len(modules)} modules")

        return processed_modules

    def _calculate_module_size(self, plugin_slug: str, module_slug: str) -> int:
        """
        Calculate module size in HP from image width.

        Args:
            plugin_slug: Plugin identifier
            module_slug: Module identifier

        Returns:
            Module size in HP, or None if image cannot be processed
        """
        try:
            image_path = CACHE_DIR / plugin_slug / f"{module_slug}.webp"
            if image_path.exists():
                with Image.open(image_path) as img:
                    width = img.width
                    return math.ceil(width / PIXELS_PER_HP)
        except Exception as e:
            log_error(f"Error processing image for {plugin_slug}/{module_slug}", e, self.logger)

        return None

    def _create_search_data(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert module data to optimized search format.

        Args:
            modules: List of processed module dictionaries

        Returns:
            Optimized search data structure
        """
        # Convert to array format for smaller file size
        data_arrays = []
        for module in modules:
            data_array = [
                module["plugin_slug"],
                module["plugin_name"],
                module["module_name"],
                module["module_slug"],
                module["description"],
                module["tags"],
                module["timestamp"],
                module["size"]
            ]
            data_arrays.append(data_array)

        return {
            "headers": SEARCH_HEADERS,
            "data": data_arrays
        }


if __name__ == "__main__":
    generator = SearchFileGenerator()
    generator.generate_search_file()