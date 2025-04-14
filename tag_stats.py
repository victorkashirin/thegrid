import json
from collections import Counter

# Load the JSON file
with open('parsed_plugins.json', 'r') as f:
    plugins = json.load(f)

# Extract all tags
all_tags = []
for plugin in plugins:
    if 'tags' in plugin:
        all_tags.extend(plugin['tags'])

# Count tag occurrences
tag_counter = Counter(all_tags)

# Sort tags by count in descending order and print results
for tag, count in tag_counter.most_common():
    print(f"{tag}: {count}")
