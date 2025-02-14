#!/bin/bash

# Load configuration from the property file
CONFIG_FILE="../config.properties"

if [ -f "$CONFIG_FILE" ]; then
    echo "Loading configuration from $CONFIG_FILE"
    while IFS='=' read -r key value; do
        if [[ ! "$key" =~ ^# && -n "$key" ]]; then
            value=$(echo "$value" | sed 's/^ *//g' | sed 's/ *$//g')  # Trim spaces
            eval "$key=\"$value\""
        fi
    done < "$CONFIG_FILE"
else
    echo "Error: Configuration file $CONFIG_FILE not found!"
    exit 1
fi

# Function to clear a directory
clear_directory() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo "Clearing directory: $dir"
        rm -rf "$dir"/*
    else
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
}

# Clear all required directories
clear_directory "$FINAL_OUTPUT_DIR"
clear_directory "$GIT_DIFF_DIR"
clear_directory "$ID_OUTPUT_DIR"

# Convert REPO_FILES comma-separated values into an array
IFS=',' read -r -a files <<< "$REPO_FILES"

# Trim spaces and handle file paths correctly
for i in "${!files[@]}"; do
    files[$i]=$(echo "${files[$i]}" | sed 's/^ *//g' | sed 's/ *$//g' | sed 's/\\ / /g')  # Remove escape chars
done

# Debugging: Print processed file paths
echo "Processed Repo Files: ${files[@]}"

# Initialize an empty string to hold the file list for git diff
file_list=""
for file in "${files[@]}"; do
    file_list+=" \"$file\""
done

# Debugging: Print git diff command
echo "Running: git diff $file_list > \"$DIFF_FILE\""

# Run git diff on the specified files
eval git diff $file_list > "$DIFF_FILE"

# Execute the Python scripts
python3.13 extractIdByPage_dev_triage.py
python3.13 extract-changes-dev-triage.py

echo "Script execution completed."
