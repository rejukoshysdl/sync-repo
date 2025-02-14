#!/bin/bash 

# Wait for the completion marker file to be created
OUTPUT_DIR="../output_json"  # The directory where the completed file will be located
COMPLETED_FILE="$OUTPUT_DIR/convert.json.completed"  # Path to the completion file
 
# Delete the directory if it exists
if [ -d "$OUTPUT_DIR" ]; then
    echo "Deleting the directory: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"  # Remove the directory and its contents
else
    echo "Directory $OUTPUT_DIR does not exist, skipping deletion."
fi

# Execute the first Python script
echo "Executing convertUpdatedDevExcelToJSON_local.py..."
python3.13 convertUpdatedDevExcelToJSON_local.py


echo "Waiting for conversion to complete..."

# Wait until the completion file exists
while [ ! -f "$COMPLETED_FILE" ]; do
    sleep 1  # Check every 1 second if the file exists
done

echo "Conversion completed! Proceeding with createPR.py..."

# Execute the second Python script to create a PR
python3.13 createPR.py

echo "Script execution completed."
