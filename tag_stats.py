"""
Tag statistics analyzer for VCV Rack Module Search.

This module analyzes tag usage across all modules and provides statistics
for understanding tag distribution and popularity.
"""

import json
from collections import Counter
from typing import List, Dict, Any, Tuple
from pathlib import Path

from config import PARSED_PLUGINS_FILE
from logger import get_logger, log_operation_start, log_operation_complete
from file_utils import FileUtils


class TagStatsAnalyzer:
    """Analyzes tag usage statistics across all modules."""

    def __init__(self):
        self.logger = get_logger()
        self.file_utils = FileUtils()

    def analyze_tag_statistics(self) -> None:
        """
        Analyze and display tag usage statistics.
        
        Loads module data, extracts all tags, counts occurrences,
        and displays results sorted by popularity.
        """
        log_operation_start("Analyzing tag statistics", self.logger)
        
        # Load module data
        modules = self._load_module_data()
        
        # Extract all tags
        all_tags = self._extract_all_tags(modules)
        
        # Count and display tag statistics
        self._display_tag_statistics(all_tags)
        
        log_operation_complete("Tag statistics analysis", self.logger)

    def _load_module_data(self) -> List[Dict[str, Any]]:
        """
        Load module data from parsed plugins file.
        
        Returns:
            List of module dictionaries
            
        Raises:
            FileProcessingError: If file cannot be loaded
        """
        return self.file_utils.load_json(PARSED_PLUGINS_FILE)

    def _extract_all_tags(self, modules: List[Dict[str, Any]]) -> List[str]:
        """
        Extract all tags from module data.
        
        Args:
            modules: List of module dictionaries
            
        Returns:
            List of all tags found across all modules
        """
        all_tags = []
        for module in modules:
            if 'tags' in module and module['tags']:
                all_tags.extend(module['tags'])
        
        self.logger.info(f"Extracted {len(all_tags)} total tags from {len(modules)} modules")
        return all_tags

    def _display_tag_statistics(self, all_tags: List[str]) -> None:
        """
        Count tag occurrences and display statistics.
        
        Args:
            all_tags: List of all tags to analyze
        """
        tag_counter = Counter(all_tags)
        unique_tags = len(tag_counter)
        
        self.logger.info(f"Found {unique_tags} unique tags")
        
        # Display results sorted by popularity
        print(f"Tag Statistics ({unique_tags} unique tags):")
        print("-" * 40)
        
        for tag, count in tag_counter.most_common():
            print(f"{tag}: {count}")

    def get_tag_statistics(self) -> Dict[str, int]:
        """
        Get tag statistics as a dictionary.
        
        Returns:
            Dictionary mapping tag names to occurrence counts
        """
        modules = self._load_module_data()
        all_tags = self._extract_all_tags(modules)
        tag_counter = Counter(all_tags)
        
        return dict(tag_counter)


if __name__ == "__main__":
    analyzer = TagStatsAnalyzer()
    analyzer.analyze_tag_statistics()
