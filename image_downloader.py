"""
Image downloading module for VCV Rack Module Search.

This module handles downloading and caching of module images.
"""

import time
from pathlib import Path
from typing import List, Dict, Any
import requests

from config import (
    CACHE_DIR,
    IMAGE_BASE_URL,
    IMAGE_FORMAT,
    REQUEST_TIMEOUT,
    DOWNLOAD_DELAY,
    CACHE_EXPIRY_DAYS
)
from logger import get_logger, log_operation_start, log_operation_complete, log_error, log_progress
from exceptions import NetworkError


class ImageDownloader:
    """Handles downloading and caching of VCV Rack module images."""

    def __init__(self, build_timestamps: Dict[str, int]):
        self.logger = get_logger()
        self.build_timestamps = build_timestamps
        self.downloaded_count = 0
        self.skipped_count = 0

    def download_module_images(self, modules: List[Dict[str, Any]]) -> None:
        """
        Download images for all modules in the provided list.

        Args:
            modules: List of module dictionaries containing plugin_slug and module_slug
        """
        log_operation_start("Downloading module images", self.logger)

        CACHE_DIR.mkdir(exist_ok=True)
        self.downloaded_count = 0
        self.skipped_count = 0

        for i, module in enumerate(modules):
            self._download_module_image(module)

            # Log progress every 100 images
            if i % 100 == 0:
                log_progress(i + 1, len(modules), "Downloading images", self.logger)

        log_operation_complete(
            f"Image download complete: {self.downloaded_count} downloaded, {self.skipped_count} skipped",
            self.logger
        )

    def _download_module_image(self, module: Dict[str, Any]) -> None:
        """
        Download a single module image if needed.

        Args:
            module: Module dictionary containing plugin_slug and module_slug
        """
        plugin_slug = module["plugin_slug"]
        module_slug = module["module_slug"]

        image_url = f"{IMAGE_BASE_URL}/{plugin_slug}/{module_slug}.{IMAGE_FORMAT}"
        plugin_folder = CACHE_DIR / plugin_slug
        plugin_folder.mkdir(exist_ok=True)
        image_path = plugin_folder / f"{module_slug}.{IMAGE_FORMAT}"

        if self._should_skip_download(image_path, image_url, plugin_slug):
            self.skipped_count += 1
            return

        try:
            self._download_image(image_url, image_path)
            self.downloaded_count += 1
        except NetworkError as e:
            log_error(f"Failed to download {image_url}", e, self.logger)

    def _should_skip_download(self, image_path: Path, image_url: str, plugin_slug: str) -> bool:
        """
        Determine if an image download should be skipped.

        Args:
            image_path: Local path where image would be saved
            image_url: URL of the remote image
            plugin_slug: Plugin slug for timestamp checking

        Returns:
            True if download should be skipped, False otherwise
        """
        if not image_path.exists():
            return False

        # Check if plugin hasn't been updated recently
        if self._get_days_since_update(plugin_slug) > CACHE_EXPIRY_DAYS:
            return True

        # Compare file sizes
        local_size = image_path.stat().st_size
        remote_size = self._get_remote_file_size(image_url)

        if remote_size != -1 and local_size == remote_size:
            self.logger.debug(f"Skipping {image_path} - sizes match ({local_size} bytes)")
            return True

        return False

    def _get_days_since_update(self, plugin_slug: str) -> int:
        """
        Get the number of days since a plugin was last updated.

        Args:
            plugin_slug: Plugin slug to check

        Returns:
            Number of days since last update, or a large number if unknown
        """
        from datetime import datetime

        if plugin_slug not in self.build_timestamps:
            return 1000000  # Very large number to indicate unknown

        timestamp = self.build_timestamps[plugin_slug]
        return (datetime.now() - datetime.fromtimestamp(timestamp)).days

    def _get_remote_file_size(self, url: str) -> int:
        """
        Get the file size of a remote file using a HEAD request.

        Args:
            url: URL to check

        Returns:
            File size in bytes, or -1 if the request fails
        """
        try:
            response = requests.head(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return int(response.headers.get("content-length", -1))
        except requests.RequestException as e:
            log_error(f"Failed to get remote file size for {url}", e, self.logger)
            return -1

    def _download_image(self, url: str, local_path: Path) -> None:
        """
        Download an image from a URL and save it locally.

        Args:
            url: URL of the image to download
            local_path: Local path to save the image

        Raises:
            NetworkError: If the download fails
        """
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            with open(local_path, "wb") as img_file:
                img_file.write(response.content)

            time.sleep(DOWNLOAD_DELAY)
            self.logger.debug(f"Downloaded: {local_path}")

        except requests.RequestException as e:
            raise NetworkError(f"Failed to download {url}: {e}")