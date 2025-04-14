import json
from PIL import Image
import os
import math

MANIFESTS_CACHE = "/Users/victorkashirin/code/Rack/vcv-rack-library/manifests-cache.json"

def get_module_size(plugin_slug, module_slug):
    try:
        image_path = f"images/{plugin_slug}/{module_slug}.webp"
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                width = img.width
                return math.ceil(width / 15)
    except Exception as e:
        print(f"Error processing image for {plugin_slug}/{module_slug}: {e}")
    return None

with open(MANIFESTS_CACHE, 'r') as f:
    manifests = json.load(f)
    
modules = json.load(open("parsed_plugins.json", "r"))

results = []

for module in modules:
    plugin_slug = module["plugin_slug"]
    module_slug = module["module_slug"]
    timestamp = manifests[plugin_slug]["modules"][module_slug]["creationTimestamp"]
    module_size = get_module_size(plugin_slug, module_slug)
    data = [module["plugin_slug"], 
            module["plugin_name"],
            module["module_name"],
            module["module_slug"],
            module["description"],
            module["tags"],
            timestamp,
            module_size
    ]
    results.append(data)

final_result = {
    "headers": ["plugin_slug", "plugin_name", "module_name", "module_slug", "description", "tags", "timestamp", "size"],
    "data": results
}

with open("search_file.json", "w") as f:
    json.dump(final_result, f)
