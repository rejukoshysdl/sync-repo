import re
import os

# Paths
diff_file_path = "../changes/git-diff/changes.diff"  # Path to the diff file
output_folder = "../changes/id-output"  # Destination folder
output_file_path = os.path.join(output_folder, "changed_ids.txt")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Dictionary to store extracted IDs grouped by section (Pages, Redirects, etc.)
changed_ids = {}

# Regular expressions
section_pattern = re.compile(r'^diff --git a/repo-shopify-data/([\w-]+)\.json')
id_pattern = re.compile(r'"ID":\s*"((?:gid://shopify/[\w/]+/)?\d+)"')
change_block_pattern = re.compile(r'^@@')

# Initialize variables
current_section = None
inside_change_block = False

# Read and process the diff file
with open(diff_file_path, "r", encoding="utf-8") as file:
    for line in file:
        # Detect section (e.g., Pages.json, Redirects.json)
        section_match = section_pattern.search(line)
        if section_match:
            current_section = section_match.group(1)
            if current_section not in changed_ids:
                changed_ids[current_section] = set()
            inside_change_block = False  # Reset when a new section starts

        # Detect start of a change block
        if change_block_pattern.search(line):
            inside_change_block = True  # Mark that we're inside a change block

        # Extract **all** IDs within a change block
        if inside_change_block:
            id_matches = id_pattern.findall(line)  # Find all IDs in the current line
            if id_matches:
                changed_ids[current_section].update(id_matches)  # Add all found IDs

# Remove empty sections
changed_ids = {section: sorted(list(ids)) for section, ids in changed_ids.items() if ids}

# Write the IDs to a file
with open(output_file_path, "w", encoding="utf-8") as output_file:
    for section, ids in changed_ids.items():
        output_file.write(f"{section} -> {', '.join(ids)}\n")

print(f"✅ Extracted IDs written to {output_file_path}")
