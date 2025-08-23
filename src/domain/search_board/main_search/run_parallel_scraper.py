import os,sys
sys.path.append(os.getcwd())
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from src.domain.search_board.main_search.state_select import Med_info
from src.domain.path.project_paths import path_obj
from src.domain.file_io.io_file import ERRORIO
import glob

class SCRAPPER:
    def __init__(self):
        self.state_code = "FL"
        self.df = pd.read_excel(path_obj.npi_excel_file, sheet_name=self.state_code)
        self.chunks = np.array_split(self.df, 2)

    @staticmethod
    def process_chunk(chunk_df, state_code, chunk_id):
        try:
            print(f"[Process {chunk_id}] Starting with {len(chunk_df)} NPIs")
            scraper = Med_info()
            scraper.enter_info(chunk_df, state_code,chunk_id)
            print(f"[Worker {chunk_id}] Done")
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(file_data=err_obj.get_errdetails(err), path=path_obj.error_details_file, mode="a")

    def merge_outputs(self):
        try:
            os.makedirs(path_obj.temp_output_dir, exist_ok=True)

            chunk_files = glob.glob(os.path.join(path_obj.temp_output_dir, f"{self.state_code}_chunk_*.xlsx"))
            all_dfs = []

            for file in chunk_files:
                try:
                    df = pd.read_excel(file)
                    all_dfs.append(df)
                except Exception as e:
                    ERRORIO().write_file(file_data=ERRORIO().get_errdetails(e), path=path_obj.error_details_file)

            if all_dfs:
                final_df = pd.concat(all_dfs, ignore_index=True)
                final_df.to_excel(path_obj.email_sheet, sheet_name=self.state_code, index=False)
                print(f"[Merge] Saved final result to {path_obj.email_sheet}")
            else:
                print("[Merge] No data collected to merge.")
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(file_data=err_obj.get_errdetails(err), path=path_obj.error_details_file, mode="a")

    def create_instances(self):
        try:
            with ProcessPoolExecutor(max_workers=2) as executor:
                futures = []
                for i, chunk_df in enumerate(self.chunks):
                    futures.append(executor.submit(self.process_chunk, chunk_df, self.state_code, i))

                for future in futures:
                    future.result()
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(file_data=err_obj.get_errdetails(err), path=path_obj.error_details_file, mode="a")



if __name__ == '__main__':
    from src.domain.search_board.main_search.run_parallel_scraper import SCRAPPER 

    scraper_obj = SCRAPPER()
    scraper_obj.create_instances()
    scraper_obj.merge_outputs() 

