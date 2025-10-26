import os,sys
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import os, pandas as pd

class NPIMATCH_SURGEON:
    def __init__(self):
        self.result_path = path_obj.combined_chunks_file  # <-- use this instead
        self.df = pd.read_excel(path_obj.all_states_surgery_npi_result)  # or wherever your NPIs are coming from
        self.npi_list = self.df["number"].dropna().astype(str).tolist()  # or the column with NPIs

    def npi_present_already(self):
        surgery_alreadyprocessed_npis = set()

        if os.path.exists(self.result_path):
            try:
                df_result = pd.read_excel(self.result_path, dtype={"National Provider Identifier": str})
                if "National Provider Identifier" in df_result.columns:  # adjust column name if needed
                    surgery_alreadyprocessed_npis = set(df_result["National Provider Identifier"].dropna().astype(str))
                else:
                    print("Warning: 'npi_number' column not found. Processing all NPIs.")
            except pd.errors.EmptyDataError:
                print("Result file empty. Processing all NPIs.")
        else:
            print("No previous results found, processing all NPIs.")

        # Return only NPIs that are not already in surgeon website results
        # new_list = [npi for npi in self.npi_list if npi not in surgery_alreadyprocessed_npis]
        
        print(f"Totals NPIs: {len(self.npi_list)}")
        print(f"Surgeons NPIs already present in Final sheet: {len(surgery_alreadyprocessed_npis)}")
        new_list = []
        for npi in self.npi_list:
            if npi not in surgery_alreadyprocessed_npis:
                new_list.append(npi)
        # return new_list
        print(f"NPIs result not present in Final Sheet: {len(new_list)}")
        # print(new_list)
    
testobj =  NPIMATCH_SURGEON()
testobj.npi_present_already()


