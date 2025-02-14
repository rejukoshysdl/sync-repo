import os
import json
import glob
import subprocess
import shutil
import pandas as pd
from datetime import datetime

# Function to load properties from config.properties
def load_properties(filepath):
    properties = {}
    if not os.path.exists(filepath):
        print(f"❌ Error: Configuration file {filepath} not found!")
        exit(1)
    
    with open(filepath, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=", 1)
                properties[key.strip()] = value.strip()
    return properties

# Load configuration
CONFIG_FILE = "../config.properties"
config = load_properties(CONFIG_FILE)

# Extract config values
FINAL_OUTPUT_DIR = config["FINAL_OUTPUT_DIR"]
GIT_DIFF_DIR = config["GIT_DIFF_DIR"]
ID_OUTPUT_DIR = config["ID_OUTPUT_DIR"]
CHANGED_IDS_FILE = config["CHANGED_IDS_FILE"]
DIFF_FILE = config["DIFF_FILE"]

# Convert comma-separated repo files into a list and handle spaces correctly
REPO_FILES = [file.strip() for file in config["REPO_FILES"].split(",")]

# Function to clear or create directories
def clear_directory(dir_path):
    if os.path.exists(dir_path):
        print(f"🧹 Clearing directory: {dir_path}")
        shutil.rmtree(dir_path)
    print(f"📂 Creating directory: {dir_path}")
    os.makedirs(dir_path, exist_ok=True)

# Clear required directories
clear_directory(FINAL_OUTPUT_DIR)
clear_directory(GIT_DIFF_DIR)
clear_directory(ID_OUTPUT_DIR)

# Run git diff on the specified files and save output
print(f"📄 Running: git diff on {len(REPO_FILES)} files...")
git_diff_command = ["git", "diff"] + REPO_FILES
with open(DIFF_FILE, "w") as diff_output:
    subprocess.run(git_diff_command, stdout=diff_output, check=True)

print(f"✅ Git diff output saved to {DIFF_FILE}")

# Run extractIdByPage.py
print("🔍 Running extractIdByPage.py...")
subprocess.run(["python3.13", "extractIdByPage.py"], check=True)

# Run extract-changes-only.py
print("🔍 Running extract-changes-only.py...")
subprocess.run(["python3.13", "extract-changes-only.py"], check=True)

print("🎉 Script execution completed successfully!")
