import sys, os, time
sys.path.append(os.getcwd())
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.domain.path.project_paths import path_obj


class NPI_API:
    def __init__(self):
        print(" Reading input Excel file...")
        self.df = pd.read_excel(path_obj.client_az_sheet_npi)
        print(" File read complete")
        self.npi_list = self.df["National Provider Identifier"].dropna().astype(str).tolist()
        self.session = requests.Session()  # Reuse connections

    def get_npi(self, npi):
        url = path_obj.npi_url
        params = {
            "version": "2.1",
            "number": npi,
            "pretty": "true"
        }
        start = time.time()
        try:
            response = self.session.get(url, params=params, timeout=10)
            elapsed = time.time() - start
            print(f" NPI {npi} → Status: {response.status_code}, Time: {elapsed:.2f}s")

            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                return []
        except Exception as e:
            print(f" Exception for NPI {npi}: {e}")
            return []

    def api_fetch(self):
        all_results = []
        max_threads = 4  

        print(f" start process of {len(self.npi_list)} NPIs using {max_threads} threads...")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(self.get_npi, npi): npi for npi in self.npi_list}

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    all_results.extend(result)
                if (i + 1) % 10 == 0:
                    print(f"{i + 1} NPIs processed...")

        total_time = time.time() - start_time
        print(f" All NPIs processed in {total_time:.2f} seconds")

        if all_results:
            df = pd.json_normalize(all_results)
            df.to_excel(path_obj.az_npi_details_api, index=False) # update path before running
            print(" Records saved to Excel")
        else:
            print(" No results found")


