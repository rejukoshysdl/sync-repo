import os
import re
import json
import subprocess

# Detect if running in GitHub Actions
GITHUB_WORKSPACE = os.getenv("GITHUB_WORKSPACE", os.getcwd())

# Paths for input and output files
changed_ids_file = os.path.join(GITHUB_WORKSPACE, "changes/id-output/changed_ids.txt")
output_dir = os.path.join(GITHUB_WORKSPACE, "changes/change-only-jsons")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Dictionary to store repository file paths
original_files = {}
repo_dir = os.path.join(GITHUB_WORKSPACE, "repo-shopify-data")

# Collect all JSON files under repo-shopify-data
for json_file in os.listdir(repo_dir):
    if json_file.endswith(".json"):
        section_name = os.path.splitext(json_file)[0]
        original_files[section_name] = os.path.join(repo_dir, json_file)

# Function to load JSON data from a file
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as f:
            return json.load(f)
    return []

# Function to write JSON data to a file
def write_json(file_path, data):
    with open(file_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Function to read changed IDs from changed_ids.txt
def read_changed_ids(changed_ids_file):
    changed_ids = {}
    if not os.path.exists(changed_ids_file):
        print(f"⚠️ No changed IDs file found at {changed_ids_file}. Skipping extraction.")
        return changed_ids
    
    with open(changed_ids_file, "r", encoding="utf-8") as file:
        for line in file:
            match = re.match(r'(\w+) -> (.+)', line.strip())  
            if match:
                section = match.group(1)
                ids = match.group(2).split(", ")
                changed_ids[section] = ids
    return changed_ids

# Read changed IDs
changed_ids = read_changed_ids(changed_ids_file)

print(f"✅ Extracted IDs: {changed_ids}")

# Dictionary to store extracted data
output_data = {}

# Process each file and extract relevant JSON blocks
for section, ids in changed_ids.items():
    if section in original_files:
        file_path = original_files[section]
        data = load_json(file_path)

        # Extract only blocks that match the changed IDs
        relevant_blocks = [block for block in data if str(block.get('ID')) in ids]

        if relevant_blocks:
            output_data[section] = relevant_blocks
            output_file_path = os.path.join(output_dir, f"{section}.json")
            write_json(output_file_path, relevant_blocks)
            print(f"✅ Extracted {len(relevant_blocks)} blocks for {section} and saved to {output_file_path}")

# Ensure at least one file was extracted
if not output_data:
    print("✅ No relevant JSON changes extracted.")
else:
    print("✅ Extraction process completed.")

# ** Ensure Git Tracks the Extracted JSON Changes **
try:
    subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)

    # ** Fetch latest branch to avoid non-fast-forward issues **
    subprocess.run(["git", "fetch", "origin", "int"], check=True)
    subprocess.run(["git", "checkout", "int"], check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "int"], check=True)

    # ** Add extracted JSON changes and push to remote repository **
    subprocess.run(["git", "add", output_dir], check=True)
    subprocess.run(["git", "status"], check=True)

    # ** Prevent empty commits **
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        print("✅ No new JSON changes detected. Skipping commit.")
    else:
        subprocess.run(["git", "commit", "-m", "Update extracted JSON changes"], check=True)
        
        # ** Attempt push, retry with force if needed **
        if subprocess.run(["git", "push", "origin", "int"]).returncode != 0:
            print("⚠️ Warning: Push failed. Retrying with force...")
            subprocess.run(["git", "push", "origin", "int", "--force"], check=True)

    print("✅ Extracted JSON changes pushed to GitHub successfully.")

except subprocess.CalledProcessError as e:
    print(f"❌ Error during Git operations: {e}")
