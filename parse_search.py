from pathlib import Path
import json
import os
import requests
import time

folder = "/Users/victorkashirin/code/Rack/vcv-rack-library/manifests"


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


def download_images():
      """
      Downloads images for each plugin and module in the parsed plugins list.
      Images are saved in the 'images' folder, organized by plugin slug.
      """
      with open("parsed_plugins.json", "r") as f:
        plugins = json.load(f)

      images_folder = Path("images")
      images_folder.mkdir(exist_ok=True)

      for moduleData in plugins:
        plugin_slug = moduleData["plugin_slug"]
        module_slug = moduleData["module_slug"]
        image_url = f"https://library.vcvrack.com/screenshots/100/{plugin_slug}/{module_slug}.webp"
        plugin_folder = images_folder / plugin_slug
        plugin_folder.mkdir(exist_ok=True)
        image_path = plugin_folder / f"{module_slug}.webp"

        if os.path.exists(image_path):
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
    with open('parsed_plugins.json', 'w') as f:
        json.dump(parse_all_plugins(folder), f, indent=4)
    # download_images()
