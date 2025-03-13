Step 1 : Git pull from staging


Step 2: Run python3.13 convertRepoJSONToExcel_local.py
        This will read repo json files from repo-shopify-data  
        and convert to matrixify excel and deposits in lcocal-matirixify-export folder.
        This will be the inital manual load to your enviornment to make sure your enviornment is in sync
        with staging repository

Step 3: Make changes to any of the product 

Step 4 : Export your changes using matirixify and deposit inside developer_updated_matrixify_export.

Step 5 : Execute python3.13 convertUpdatedDevExcelToJSON_local.py which will generate JSON files and deposit inside outut_json folder

Step 6 :  python3.13 createPR.py 



Capture changes

1.  python3.13 extractIdByPage_dev_triage.py
2.  python3.13 extract-changes-dev-triage.py
3. 