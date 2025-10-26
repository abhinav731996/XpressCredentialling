import os,pandas as pd
from src.domain.path.project_paths import path_obj

class NPIMATCH:
    def __init__(self):
        self.result_path = path_obj.all_states_surgery_npi_result
        self.df = pd.read_excel(path_obj.all_states_surgery_npi_test)
        self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).tolist()

    def npi_present_already(self):
        self.processed_npis = set()

        if os.path.exists(self.result_path):
            try:
                df_result = pd.read_excel(self.result_path, dtype={"number": str})
                if "number" in df_result.columns:
                    self.processed_npis = set(df_result["number"].dropna().astype(str)) # .dropna-removes (NaN) values.
                else:
                    print("Warning: 'number' column not found in result file. Processing all NPIs.")
            except pd.errors.EmptyDataError:
                print("Warning: Result file is empty. Processing all NPIs.")
        else:
            print("No previous results found, processing all NPIs.")

        new_list = [] 
        for npi in self.npi_list:  
            if npi not in self.processed_npis:
                new_list.append(npi)

        return new_list

npi_already_insheet = NPIMATCH()


