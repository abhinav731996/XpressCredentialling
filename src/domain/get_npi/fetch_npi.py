import sys, os, time, json
sys.path.append(os.getcwd())
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.domain.path.project_paths import path_obj

class NPI_API:
    def __init__(self):
        self.df = pd.read_excel(path_obj.client_data)
        self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).tolist()

        # Filter out already processed NPIs and sets column name if its not present
        result_path = path_obj.client_data_result
        processed_npis = set()

        if os.path.exists(result_path):
            try:
                df_result = pd.read_excel(result_path, dtype={"number": str})
                if "number" in df_result.columns:
                    processed_npis = set(df_result["number"].dropna().astype(str))
                else:
                    print("Warning: 'number' column not found in result file. Processing all NPIs.")
            except pd.errors.EmptyDataError:
                print("Warning: Result file is empty. Processing all NPIs.")
        else:
            print("No previous results found, processing all NPIs.")

        before_count = len(self.npi_list)
        self.npi_list = [npi for npi in self.npi_list if npi not in processed_npis]
        print(f"Skipping {before_count - len(self.npi_list)} already processed NPIs.")
        print(f"Total NPIs to process: {len(self.npi_list)}")



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
            futures = {executor.submit(self.get_npi, npi): npi for npi in self.npi_list}

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    all_results.extend(result)
                if (i + 1) % 10 == 0:
                    print(f"{i + 1} NPIs processed...")
        
        # npi result is saved 
        if all_results:
            df = pd.json_normalize(all_results)
            result_path = path_obj.client_data_result

            if os.path.exists(result_path):
                try:
                    df_existing = pd.read_excel(result_path, dtype={"number": str})
                    if "number" in df_existing.columns:
                        df_combined = pd.concat([df_existing, df], ignore_index=True)
                        df_combined.drop_duplicates(subset=["number"], keep="first", inplace=True)
                    else:
                        df_combined = df
                except pd.errors.EmptyDataError:
                    df_combined = df
            else:
                df_combined = df

            df_combined.to_excel(result_path, index=False)
            print(f"Records saved to Excel ({len(df_combined)} total).")
        else:
            print("No results found")

# test_obj = NPI_API()
# test_obj.api_fetch()
