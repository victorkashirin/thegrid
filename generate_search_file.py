import json
from PIL import Image
import os
import math

from config import (
    MANIFESTS_CACHE_FILE,
    PARSED_PLUGINS_FILE,
    SEARCH_FILE,
    CACHE_DIR,
    PIXELS_PER_HP,
    SEARCH_HEADERS
)
from logger import get_logger, log_operation_start, log_operation_complete, log_error
from exceptions import FileProcessingError, ImageProcessingError

def get_module_size(plugin_slug, module_slug):
    logger = get_logger()
    try:
        image_path = CACHE_DIR / plugin_slug / f"{module_slug}.webp"
        if image_path.exists():
            with Image.open(image_path) as img:
                width = img.width
                return math.ceil(width / PIXELS_PER_HP)
    except Exception as e:
        log_error(f"Error processing image for {plugin_slug}/{module_slug}", e, logger)
    return None

if __name__ == "__main__":
    logger = get_logger()
    log_operation_start("Generating search file", logger)
    
    try:
        with open(MANIFESTS_CACHE_FILE, 'r') as f:
            manifests = json.load(f)
    except FileNotFoundError as e:
        log_error(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}", e, logger)
        raise FileProcessingError(f"Manifest cache file not found: {MANIFESTS_CACHE_FILE}")
    except json.JSONDecodeError as e:
        log_error(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}", e, logger)
        raise FileProcessingError(f"Error decoding manifest cache file: {MANIFESTS_CACHE_FILE}")
    
    try:
        with open(PARSED_PLUGINS_FILE, "r") as f:
            modules = json.load(f)
    except FileNotFoundError as e:
        log_error(f"Parsed plugins file not found: {PARSED_PLUGINS_FILE}", e, logger)
        raise FileProcessingError(f"Parsed plugins file not found: {PARSED_PLUGINS_FILE}")
    except json.JSONDecodeError as e:
        log_error(f"Error decoding parsed plugins file: {PARSED_PLUGINS_FILE}", e, logger)
        raise FileProcessingError(f"Error decoding parsed plugins file: {PARSED_PLUGINS_FILE}")

    results = []
    processed_count = 0

    for module in modules:
        plugin_slug = module["plugin_slug"]
        module_slug = module["module_slug"]
        
        try:
            timestamp = manifests[plugin_slug]["modules"][module_slug]["creationTimestamp"]
        except KeyError:
            log_error(f"Missing timestamp for {plugin_slug}/{module_slug}", logger=logger)
            timestamp = None
        
        module_size = get_module_size(plugin_slug, module_slug)
        
        data = [
            module["plugin_slug"], 
            module["plugin_name"],
            module["module_name"],
            module["module_slug"],
            module["description"],
            module["tags"],
            timestamp,
            module_size
        ]
        results.append(data)
        processed_count += 1
        
        if processed_count % 100 == 0:
            logger.info(f"Processed {processed_count}/{len(modules)} modules")

    final_result = {
        "headers": SEARCH_HEADERS,
        "data": results
    }

    with open(SEARCH_FILE, "w") as f:
        json.dump(final_result, f)
    
    log_operation_complete(f"Generated search file with {len(results)} modules", logger)
