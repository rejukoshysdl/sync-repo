import json
import os
import glob
import pandas as pd
from datetime import datetime

# Function to convert JSON files from a directory into an Excel file
def json_to_excel(json_dir, output_folder):
    print(f"🔍 Searching for JSON files in: {os.path.abspath(json_dir)}")

    # Get all JSON files recursively
    json_files = glob.glob(os.path.join(json_dir, '**', '*.json'), recursive=True)

    if not json_files:
        print(f"🚫 Skipping {json_dir} (No JSON files found).")
        return None

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Generate unique Excel file name
    current_time = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_excel_file = os.path.join(output_folder, f'Export_{current_time}.xlsx')

    print(f"📄 Processing {len(json_files)} JSON files in {json_dir}...")

    # Create an Excel writer object
    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for json_file in json_files:
            sheet_name = os.path.splitext(os.path.basename(json_file))[0][:31]

            with open(json_file, 'r') as f:
                json_data = json.load(f)

            print(f"✅ Processing file: {json_file}")

            df = pd.DataFrame(json_data)

            for col in df.columns:
                if pd.api.types.is_bool_dtype(df[col]):
                    df[col] = df[col].replace({True: 'TRUE', False: 'FALSE'})
                elif pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and x == int(x) else f"{x:,.2f}")

            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"🎉 Excel file created: {output_excel_file}")

    return output_excel_file  # Return the file path for GitHub workflow commit

# Define JSON directories and corresponding Excel export folders
folder_mappings = {
    "repo-shopify-data": "final-matrixify-export",
    "changes/change-only-jsons": "changes/change-only-excel"
}

# Generate Excel files
generated_files = []
for json_dir, output_dir in folder_mappings.items():
    print(f"\n🚀 Processing directory: {json_dir} → {output_dir}")
    excel_file = json_to_excel(json_dir, output_dir)
    if excel_file:
        generated_files.append(excel_file)

# ✅ Print generated file paths for workflow use
if generated_files:
    print("\n📂 Generated Excel files:")
    for file in generated_files:
        print(f" - {file}")

print("\n🎯 JSON to Excel conversion completed successfully!")
