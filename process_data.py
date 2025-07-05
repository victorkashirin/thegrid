"""
Main data processing module for VCV Rack Module Search.

This module orchestrates the parsing of plugin manifests and downloading of module images.
"""

from typing import List, Dict, Any

from config import (
    MANIFESTS_DIR,
    PARSED_PLUGINS_FILE
)
from logger import get_logger, log_operation_start, log_operation_complete
from data_parser import PluginDataParser
from image_downloader import ImageDownloader
from timestamp_manager import TimestampManager
from file_utils import FileUtils


class ModuleDataProcessor:
    """Main processor for VCV Rack module data."""

    def __init__(self):
        self.logger = get_logger()
        self.data_parser = PluginDataParser()
        self.timestamp_manager = TimestampManager()
        self.file_utils = FileUtils()

    def process_plugins(self) -> List[Dict[str, Any]]:
        """
        Main processing pipeline for plugin data.

        Returns:
            List of processed module dictionaries
        """
        log_operation_start("VCV Module Search data processing", self.logger)

        # Parse all plugin manifests
        all_modules = self.data_parser.parse_all_manifests(MANIFESTS_DIR)

        # Save parsed data
        self.file_utils.save_json(all_modules, PARSED_PLUGINS_FILE, indent=4)
        self.logger.info(f"Saved {len(all_modules)} modules to {PARSED_PLUGINS_FILE}")

        # Download images
        self._download_module_images(all_modules)

        log_operation_complete("VCV Module Search data processing", self.logger)
        return all_modules

    def _download_module_images(self, modules: List[Dict[str, Any]]) -> None:
        """
        Download images for all processed modules.

        Args:
            modules: List of module dictionaries
        """
        build_timestamps = self.timestamp_manager.get_build_timestamps()
        image_downloader = ImageDownloader(build_timestamps)
        image_downloader.download_module_images(modules)


if __name__ == "__main__":
    processor = ModuleDataProcessor()
    processor.process_plugins()