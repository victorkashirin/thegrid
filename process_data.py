from pathlib import Path
import json
import os
import requests
import time
from datetime import datetime

from config import (
    MANIFESTS_DIR,
    MANIFESTS_CACHE_FILE,
    PARSED_PLUGINS_FILE,
    CACHE_DIR,
    IMAGE_BASE_URL,
    IMAGE_FORMAT,
    REQUEST_TIMEOUT,
    DOWNLOAD_DELAY,
    MINIMUM_VERSION,
    EXCLUDED_PLUGINS,
    CACHE_EXPIRY_DAYS,
    PIXELS_PER_HP
)
from logger import get_logger, log_operation_start, log_operation_complete, log_error, log_warning, log_progress
from exceptions import NetworkError, DataParsingError, FileProcessingError


def get_remote_file_size(url: str) -> int:
    """
    Gets the file size of a remote file using a HEAD request.

    Args:
        url (str): The URL to check

    Returns:
        int: The file size in bytes, or -1 if the request fails
    """
    logger = get_logger()
    try:
        response = requests.head(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return int(response.headers.get("content-length", -1))
    except requests.RequestException as e:
        log_error(f"Failed to get remote file size for {url}", e, logger)
        return -1


def parse_plugin_json_to_list(path: Path) -> list:
    """
    Parses a JSON string representing plugin information and outputs a list of
    dictionaries, one for each module.

    Args:
        path (Path): The path to the JSON file to parse.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
              plugin name, plugin slug, module name, module slug, description,
              and tags for a specific module. Returns an empty list if parsing
              fails or if there are no modules.
    """
    logger = get_logger()
    try:
        with open(path, "r") as f:
            data = json.load(f)
        
        version = data.get("version")
        if version < MINIMUM_VERSION:
            return []
        
        plugin_name = data.get("name")
        plugin_slug = data.get("slug")

        if plugin_slug in EXCLUDED_PLUGINS:
            return []

        modules = data.get("modules", [])
        output_list = []

        for module in modules:
            if module.get("hidden") == True:
                continue
            if module.get("deprecated") == True:
                continue
            module_info = {
                "plugin_name": plugin_name,
                "plugin_slug": plugin_slug,
                "module_name": module.get("name"),
                "module_slug": module.get("slug"),
                "description": module.get("description"),
                "tags": module.get("tags", []),
            }
            output_list.append(module_info)
        return output_list
    except json.JSONDecodeError as e:
        log_error(f"Error decoding JSON from {path}", e, logger)
        return []
    except FileNotFoundError as e:
        log_error(f"File not found: {path}", e, logger)
        return []


def parse_all_plugins(folder: Path) -> list:
    """
    Parses all JSON files in the specified folder and returns a list of
    dictionaries containing plugin and module information.
    Args:
        folder (Path): The folder containing the JSON files.
    Returns:
        list: A list of dictionaries, where each dictionary contains the
              plugin name, plugin slug, module name, module slug, description,
              and tags for a specific module.
    """
    logger = get_logger()
    log_operation_start("Parsing all plugin manifests", logger)
    
    all_plugins = []
    json_files = list(folder.rglob("*.json"))
    
    for i, path in enumerate(json_files):
        plugin_list = parse_plugin_json_to_list(path)
        all_plugins.extend(plugin_list)
        
        if i % 50 == 0:  # Log progress every 50 files
            log_progress(i + 1, len(json_files), "Parsing manifests", logger)
    
    log_operation_complete(f"Parsed {len(json_files)} manifest files, found {len(all_plugins)} modules", logger)
    return all_plugins


def get_build_timestamps():
    logger = get_logger()
    try:
        with open(MANIFESTS_CACHE_FILE, "r") as f:
            manifest_cache = json.load(f)
        return dict(
            [
                (slug, data.get("buildTimestamp", -1))
                for (slug, data) in manifest_cache.items()
            ]
        )
    except FileNotFoundError as e:
        log_error(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}", e, logger)
        return {}
    except json.JSONDecodeError as e:
        log_error(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}", e, logger)
        return {}


def get_days_diff(plugin_slug: str, build_timestamps: dict) -> int:
    if plugin_slug not in build_timestamps:
        return 1000000
    return (datetime.now() - datetime.fromtimestamp(build_timestamps[plugin_slug])).days


def download_images(plugins: list):
    """
    Downloads images for each plugin and module in the parsed plugins list.
    Images are saved in the cache folder, organized by plugin slug.
    """
    logger = get_logger()
    log_operation_start("Downloading module images", logger)

    CACHE_DIR.mkdir(exist_ok=True)
    build_timestamps = get_build_timestamps()

    downloaded_count = 0
    skipped_count = 0

    for i, module_data in enumerate(plugins):
        plugin_slug = module_data["plugin_slug"]
        module_slug = module_data["module_slug"]
        image_url = f"{IMAGE_BASE_URL}/{plugin_slug}/{module_slug}.{IMAGE_FORMAT}"
        plugin_folder = CACHE_DIR / plugin_slug
        plugin_folder.mkdir(exist_ok=True)
        image_path = plugin_folder / f"{module_slug}.{IMAGE_FORMAT}"

        # Check if local file exists and compare sizes
        if os.path.exists(image_path):
            if get_days_diff(plugin_slug, build_timestamps) > CACHE_EXPIRY_DAYS:
                skipped_count += 1
                continue
            local_size = os.path.getsize(image_path)
            remote_size = get_remote_file_size(image_url)

            if remote_size != -1 and local_size == remote_size:
                logger.debug(f"Skipping {image_path} - sizes match ({local_size} bytes)")
                skipped_count += 1
                continue

        try:
            response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
                time.sleep(DOWNLOAD_DELAY)
            logger.debug(f"Downloaded: {image_path}")
            downloaded_count += 1
        except requests.RequestException as e:
            log_error(f"Failed to download {image_url}", e, logger)

        # Log progress every 100 images
        if i % 100 == 0:
            log_progress(i + 1, len(plugins), "Downloading images", logger)

    log_operation_complete(f"Image download complete: {downloaded_count} downloaded, {skipped_count} skipped", logger)


if __name__ == "__main__":
    logger = get_logger()
    log_operation_start("VCV Module Search data processing", logger)
    
    all_plugins = parse_all_plugins(MANIFESTS_DIR)
    
    with open(PARSED_PLUGINS_FILE, "w") as f:
        json.dump(all_plugins, f, indent=4)
    logger.info(f"Saved {len(all_plugins)} plugins to {PARSED_PLUGINS_FILE}")
    
    download_images(all_plugins)
    
    log_operation_complete("VCV Module Search data processing", logger)
