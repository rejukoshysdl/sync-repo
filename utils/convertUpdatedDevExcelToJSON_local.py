import pandas as pd
import json
import os
import glob

# Function to exclude specific sheets
def exclude_sheet(sheet_name, excluded_sheets):
    """
    Check if the sheet name should be excluded based on a list of excluded sheets.
    
    :param sheet_name: Name of the sheet to check
    :param excluded_sheets: List of sheet names to exclude
    :return: Boolean, True if sheet is in the exclude list, False otherwise
    """
    return sheet_name in excluded_sheets

# Get the current working directory
current_dir = os.getcwd()

# Define the path to the `developer_export` folder
developer_export_dir = os.path.join(current_dir, '../developer_updated_matrixify_export')

# Find all .xlsx files in the developer_export directory
xlsx_files = glob.glob(os.path.join(developer_export_dir, '*.xlsx'))

# Check if there is exactly one .xlsx file in the directory
if len(xlsx_files) != 1:
    raise ValueError("There should be exactly one .xlsx file in the developer_updated_matrixify_export directory.")

# Use the found .xlsx file
file_path = xlsx_files[0]

# Load the Excel file with strict data types
xls = pd.ExcelFile(file_path)

# Get sheet names
sheet_names = xls.sheet_names

# Define sheets to exclude (e.g., Export Summary)
excluded_sheets = ["Export Summary"]

# Create a dictionary of JSON files (one for each sheet)
json_files = {}
for sheet in sheet_names:
    # Skip the sheets that are in the excluded_sheets list
    if exclude_sheet(sheet, excluded_sheets):
        continue
    
    # Read the sheet into a DataFrame
    df = pd.read_excel(xls, sheet_name=sheet, dtype=str)  # Read all columns as strings to avoid automatic type conversion
    
    # Replace NaN values with an empty string
    df = df.fillna("")
    
    # Iterate over each column to check if its data is a float or int and format if necessary
    for col in df.columns:
        # Check if the column contains 'TRUE'/'FALSE' as strings and convert them to booleans
        if df[col].dtype == 'object':
            df[col] = df[col].apply(lambda x: True if x == 'TRUE' else (False if x == 'FALSE' else x))
        
        # If the column contains numeric data, format with commas, but preserve as string
        elif pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x == int(x) else f"{x:,.2f}")
    
    # Convert each sheet to a list of dictionaries (JSON format)
    json_files[sheet] = df.to_dict(orient='records')

# Define the output directory for JSON files
output_dir = "../output_json"
os.makedirs(output_dir, exist_ok=True)

# Save each sheet's data as a separate JSON file
for sheet, json_data in json_files.items():
    output_file = os.path.join(output_dir, f"{sheet}.json")
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=4)

# Create the completed marker file
completed_file = os.path.join(output_dir, "convert.json.completed")
with open(completed_file, 'w') as f:
    f.write("Conversion complete.")

print(f"JSON files saved to {output_dir} and conversion marker created.")
