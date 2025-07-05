from pathlib import Path
import json
import os
import requests
import time
from datetime import datetime

folder = "./library/manifests"


def get_remote_file_size(url: str) -> int:
    """
    Gets the file size of a remote file using a HEAD request.

    Args:
        url (str): The URL to check

    Returns:
        int: The file size in bytes, or -1 if the request fails
    """
    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()
        return int(response.headers.get("content-length", -1))
    except requests.RequestException:
        return -1


def parse_plugin_json_to_list(path: Path) -> list:
    """
    Parses a JSON string representing plugin information and outputs a list of
    dictionaries, one for each module.

    Args:
        json_string (str): The JSON string to parse.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
              plugin name, plugin slug, module name, module slug, description,
              and tags for a specific module. Returns an empty list if parsing
              fails or if there are no modules.
    """
    try:
        data = json.load(open(path, "r"))
        version = data.get("version")
        if version < "2.0.0":
            return []
        plugin_name = data.get("name")
        plugin_slug = data.get("slug")

        if plugin_slug in ["KRTPluginA"]:
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
        print(f"Error decoding JSON: {e}")
        return []


def parse_all_plugins(folder: str) -> list:
    """
    Parses all JSON files in the specified folder and returns a list of
    dictionaries containing plugin and module information.
    Args:
        folder (str): The folder containing the JSON files.
    Returns:
        list: A list of dictionaries, where each dictionary contains the
              plugin name, plugin slug, module name, module slug, description,
              and tags for a specific module.
    """
    all_plugins = []
    for path in Path(folder).rglob("*.json"):
        plugin_list = parse_plugin_json_to_list(path)
        all_plugins.extend(plugin_list)
    return all_plugins


def get_build_timestamps():
    manifest_cache = json.load(open("library/manifests-cache.json"))
    return dict(
        [
            (slug, data.get("buildTimestamp", -1))
            for (slug, data) in manifest_cache.items()
        ]
    )


def get_days_diff(plugin_slug: str, build_timestamps: dict) -> int:
    if plugin_slug not in build_timestamps:
        return 1000000
    return (datetime.now() - datetime.fromtimestamp(build_timestamps[plugin_slug])).days


def download_images(plugins: list):
    """
    Downloads images for each plugin and module in the parsed plugins list.
    Images are saved in the 'images' folder, organized by plugin slug.
    """

    images_folder = Path("cache")
    images_folder.mkdir(exist_ok=True)

    build_timestamps = get_build_timestamps()

    for moduleData in plugins:
        plugin_slug = moduleData["plugin_slug"]
        module_slug = moduleData["module_slug"]
        image_url = f"https://library.vcvrack.com/screenshots/100/{plugin_slug}/{module_slug}.webp"
        plugin_folder = images_folder / plugin_slug
        plugin_folder.mkdir(exist_ok=True)
        image_path = plugin_folder / f"{module_slug}.webp"

        # Check if local file exists and compare sizes
        if os.path.exists(image_path):
            if get_days_diff(plugin_slug, build_timestamps) > 2:
                continue
            local_size = os.path.getsize(image_path)
            remote_size = get_remote_file_size(image_url)

            if remote_size != -1 and local_size == remote_size:
                print(f"Skipping {image_path} - sizes match ({local_size} bytes)")
                continue

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            with open(image_path, "wb") as img_file:
                img_file.write(response.content)
                time.sleep(0.1)
            print(f"Downloaded: {image_path}")
        except requests.RequestException as e:
            print(f"Failed to download {image_url}: {e}")


if __name__ == "__main__":
    all_plugins = parse_all_plugins(folder)
    with open("parsed_plugins.json", "w") as f:
        json.dump(all_plugins, f, indent=4)
    download_images(all_plugins)
