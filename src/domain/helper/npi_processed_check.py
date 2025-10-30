import os,pandas as pd
from src.domain.path.project_paths import path_obj

class NPIMATCH:
    def __init__(self,check_type):
        if(check_type == 'client'): # when client npi is matched with the sheet data from npi api()
            self.result_path = path_obj.all_states_surgery_npi_result
            self.df = pd.read_excel(path_obj.all_states_surgery_npi_test)
            self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).tolist()
            self.col_type = "number"
        else:
            # when the npi that are not present in final sheet are sent to surgeon website for scrap
            self.result_path = path_obj.combined_chunks_file  
            self.df = pd.read_excel(path_obj.all_states_surgery_npi_result) 
            self.npi_list = self.df["number"].dropna().astype(str).tolist() 
            self.col_type = "National Provider Identifier"
        
        

    def npi_present_already(self):
        self.processed_npis = set()

        if os.path.exists(self.result_path):
            try:
                df_result = pd.read_excel(self.result_path, dtype={self.col_type: str})
                if self.col_type in df_result.columns:
                    self.processed_npis = set(df_result[self.col_type].dropna().astype(str)) # .dropna-removes (NaN) values.
                else:
                    print(f"Warning: {self.col_type} column not found in result file. Processing all NPIs.")
            except pd.errors.EmptyDataError:
                print("Warning: Result file is empty. Processing all NPIs.")
        else:
            print("No previous results found, processing all NPIs.")

        new_list = [] 
        for npi in self.npi_list:  
            if npi not in self.processed_npis:
                new_list.append(npi)

        return new_list
        
# npi_already_insheet = NPIMATCH()
