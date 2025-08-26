import sys,os
sys.path.append(os.getcwd())
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from src.domain.path.project_paths import path_obj


class NPI_API:
    def __init__(self):
        self.df = pd.read_excel(path_obj.arizona_input_famprac) 
        self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).tolist()

    def get_npi(self, npi):
        params = {
            "version": "2.1",
            "number": npi,
            "pretty": "true"
        }
        try:
            response = requests.get(path_obj.npi_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                print(f"Failed for NPI {npi} with status {response.status_code}")
                return []
        except Exception as e:
            print(f"Exception for NPI {npi}: {e}")
            return []

    def api_fetch(self):
        batch_size=10
        all_results = []

        for i in range(0, len(self.npi_list), batch_size):
            batch = self.npi_list[i:i+batch_size]
            futures = []

            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                for npi in batch:
                    futures.append(executor.submit(self.get_npi, npi))

                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        all_results.extend(result)

            print(f"Batch {i // batch_size + 1} processed, delay 1 sec")
            time.sleep(1)

        if all_results:
            df = pd.json_normalize(all_results)
            df.to_excel(path_obj.arizona_npi_license, index=False)
            print("Records saved")
        else:
            print("No results found")

fetcher = NPI_API()
fetcher.api_fetch()
