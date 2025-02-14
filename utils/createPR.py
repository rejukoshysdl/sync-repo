import json
import os
import glob
import shutil  # This will be used for file copying

# Paths to the output and repo directories
output_json_dir = '../output_json'  # Directory containing the JSON files generated from the script
repo_json_dir = '../repo-shopify-data'  # Source of truth directory

# Get all JSON files in the output directory
output_json_files = glob.glob(os.path.join(output_json_dir, '*.json'))

# Process each JSON file
for output_json_path in output_json_files:
    # Derive the corresponding repo file path from the output path
    file_name = os.path.basename(output_json_path)
    repo_json_path = os.path.join(repo_json_dir, file_name)

    # Copy the file from the output_json directory to the repo_json directory.
    try:
        shutil.copy(output_json_path, repo_json_path)  # This will copy the file to the destination
        print(f"Successfully copied {file_name} to {repo_json_path}")
    except Exception as e:
        print(f"Error copying {file_name} to {repo_json_path}: {e}")
