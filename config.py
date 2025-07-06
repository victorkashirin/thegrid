"""
Configuration management for VCV Rack Module Search.

This module centralizes all configuration constants, paths, and settings
used throughout the application.
"""

from pathlib import Path
from typing import List

# Base directories
BASE_DIR = Path(__file__).parent
LIBRARY_DIR = BASE_DIR / "library"
MANIFESTS_DIR = LIBRARY_DIR / "manifests"
CACHE_DIR = BASE_DIR / "cache"
SITE_DIR = BASE_DIR / "site"

# File paths
MANIFESTS_CACHE_FILE = LIBRARY_DIR / "manifests-cache.json"
PARSED_PLUGINS_FILE = BASE_DIR / "parsed_plugins.json"
SEARCH_FILE = BASE_DIR / "search_file.json"
SITE_SEARCH_FILE = SITE_DIR / "search_file.json"
INDEX_HTML_FILE = BASE_DIR / "index.html"
SITE_INDEX_HTML_FILE = SITE_DIR / "index.html"

# Git repository configuration
VCV_LIBRARY_REPO_URL = "https://github.com/VCVRack/library.git"

# Image processing constants
PIXELS_PER_HP = 15  # 15 pixels = 1HP
IMAGE_BASE_URL = "https://library.vcvrack.com/screenshots/100"
IMAGE_FORMAT = "webp"

# Network configuration
REQUEST_TIMEOUT = 10  # seconds
DOWNLOAD_DELAY = 0.1  # seconds between downloads

# Module filtering
MINIMUM_VERSION = "2.0.0"
EXCLUDED_PLUGINS: List[str] = ["KRTPluginA"]

# Cache configuration
CACHE_EXPIRY_DAYS = 2  # Only re-download images if plugin was updated within this period

# Search file structure
SEARCH_HEADERS = [
    "plugin_slug",
    "plugin_name",
    "module_name",
    "module_slug",
    "description",
    "tags",
    "timestamp",
    "size"
]

# Site deployment
SITE_IMAGES_DIR = SITE_DIR / "images"