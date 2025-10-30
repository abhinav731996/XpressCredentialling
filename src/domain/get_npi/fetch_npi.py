
import sys, os, time, json
sys.path.append(os.getcwd())
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.domain.path.project_paths import path_obj
from src.domain.helper.npi_processed_check import NPIMATCH

class NPI_API:
    def __init__(self):
        npi_checker = NPIMATCH(check_type='client')
        self.df = pd.read_excel(path_obj.all_states_surgery_npi_test)
        self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).unique().tolist()
        self.npi_to_process  = npi_checker.npi_present_already()
        
        before_count = len(self.npi_list)
        self.npi_list = [npi for npi in self.npi_list if npi not in npi_checker.processed_npis]
        print(f"{before_count - len(self.npi_list)} Npis already in nppes data sheet")
        print(f"NPIs to send to Nppes api: {len(self.npi_list)}")

        self.session = requests.Session()


    # npi not present in result sheet are sent to npi api
    def get_npi(self, npi):
        url = path_obj.npi_url
        params = {
            "version": "2.1",
            "number": npi,
            "pretty": "true"
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                return []
        except Exception as e:
            print(f"Exception for NPI {npi}: {e}")
            return []

    # client data npi are divided in 4 threads
    def api_fetch(self):
        all_results = []
        max_threads = 4

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {}  # create an empty dictionary

            for npi in self.npi_to_process:                # go through each NPI
                future = executor.submit(self.get_npi, npi)  # submit the API call to run in a thread
                futures[future] = npi                        # store it in the dictionary with future as key

            # futures = {executor.submit(self.get_npi, npi): npi for npi in self.npi_to_process}
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    all_results.extend(result)
                if (i + 1) % 10 == 0:
                    print(f"{i + 1} NPIs processed...")
        
        # npi result is saved 
        if all_results:
            df = pd.json_normalize(all_results)
            
            if os.path.exists(path_obj.all_states_surgery_npi_result):
                try:
                    df_existing = pd.read_excel(path_obj.all_states_surgery_npi_result, dtype={"number": str})
                    if "number" in df_existing.columns:
                        df_combined = pd.concat([df_existing, df], ignore_index=True)
                        df_combined.drop_duplicates(subset=["number"], keep="first", inplace=True)
                    else:
                        df_combined = df
                except pd.errors.EmptyDataError:
                    df_combined = df
            else:
                df_combined = df

            df_combined.to_excel(path_obj.all_states_surgery_npi_result, index=False)
            print(f"Records saved to Excel ({len(df_combined)} total).")
        else:
            print("No results found")
