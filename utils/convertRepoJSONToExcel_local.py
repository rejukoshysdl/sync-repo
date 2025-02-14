import pandas as pd
import json
import os
import glob
from datetime import datetime

# Function to convert JSON files from a directory into an Excel file
def json_to_excel(json_dir, output_folder):
    """
    Convert JSON files from a directory into an Excel file with each JSON file as a separate sheet.

    :param json_dir: Directory containing the JSON files
    :param output_folder: Folder where the Excel file will be saved
    """
    json_files = glob.glob(os.path.join(json_dir, '*.json'))  # Get all JSON files in the directory

    if not json_files:
        print(f"Skipping {json_dir} (No JSON files found).")
        return
    
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Get the current timestamp for the output file
    current_time = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_excel_file = os.path.join(output_folder, f'Export_{current_time}.xlsx')

    # Create an Excel writer object
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for json_file in json_files:
            # Extract the sheet name from the JSON file name
            sheet_name = os.path.splitext(os.path.basename(json_file))[0][:31]  # Excel sheet names max length = 31

            # Load JSON data
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            # Convert JSON data to a DataFrame
            df = pd.DataFrame(json_data)

            # Convert True/False to 'TRUE'/'FALSE'
            for col in df.columns:
                if pd.api.types.is_bool_dtype(df[col]):
                    df[col] = df[col].replace({True: 'TRUE', False: 'FALSE'})
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and x == int(x) else f"{x:,.2f}")

            # Write DataFrame to the corresponding sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"✅ Excel file created: {output_excel_file}")

# Define multiple JSON directories and corresponding output folders
folder_mappings = {
    "../repo-shopify-data": "../local-matrixify-export",
    "../changes/change-only-jsons": "../changes/change-only-excel"
} 

# Process each JSON directory
for json_dir, output_dir in folder_mappings.items():
    print(f"Processing {json_dir}...")
    json_to_excel(json_dir, output_dir)

print("✅ All conversions completed!")
