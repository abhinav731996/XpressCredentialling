import os,sys,glob
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
        try:
            self.df = pd.read_excel(path_obj.arizona_npi_license_two)
            print(f"[DEBUG] Loading file from: {path_obj.arizona_npi_license_two}")
            print(f"[DEBUG] Shape of loaded file: {self.df.shape}")
            print(self.df.head())

            self.chunks = np.array_split(self.df, 2)
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)

    @staticmethod
    def process_chunk(chunk_df, chunk_id):
        try:
            print(f"[Process {chunk_id}] Starting with {len(chunk_df)} NPIs")
            scraper = Med_info()
            scraper.enter_info(chunk_df,chunk_id)
            print(f"[Process {chunk_id}] Done")
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)


    def merge_outputs(self):
        try:
            os.makedirs(path_obj.temp_output_dir, exist_ok=True)

            chunk_files = glob.glob(os.path.join(path_obj.temp_output_dir, "*.xlsx"))
            all_dfs = []

            for file in chunk_files:
                try:
                    df = pd.read_excel(file)
                    df.columns = df.columns.str.strip()
                    all_dfs.append(df)
                except Exception as e:
                    ERRORIO().write_file(e)

            if not all_dfs:
                print("[Merge] No data collected to merge.")
                return

            new_data = pd.concat(all_dfs, ignore_index=True)
            new_data.columns = new_data.columns.str.strip()

            output_path = r"D:\Repositories\XpressCredentialling\src\database\test\arizona_famprac.xlsx"
            if os.path.exists(output_path):
                master_df = pd.read_excel(output_path)
                master_df.columns = master_df.columns.str.strip()
            else:
                master_df = pd.DataFrame()

            if not master_df.empty:
                key_col = "National Provider Identifier"

                updated_df = master_df.copy()

                if "npi" in new_data.columns and "National Provider Identifier" not in new_data.columns:
                    new_data.rename(columns={"npi": "National Provider Identifier"}, inplace=True)

                master_df.set_index(key_col, inplace=True)
                new_data.set_index(key_col, inplace=True)

                for col in new_data.columns:
                    master_df[col] = new_data[col].combine_first(master_df.get(col))

                master_df.reset_index(inplace=True)
            else:
                master_df = new_data.reset_index()

            master_df.to_excel(output_path, index=False)
            print(f"[Merge] Saved final merged result to {output_path}")

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)

    def create_instances(self):
        try:
            with ProcessPoolExecutor(max_workers=2) as executor:
                futures = []
                for i, chunk_df in enumerate(self.chunks):
                    print(f"[DEBUG] Chunk {i} shape: {chunk_df.shape}")
                    futures.append(executor.submit(self.process_chunk, chunk_df, i))

                for future in futures:
                    future.result()
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)

if __name__ == '__main__':
    scraper_obj = SCRAPPER()
    scraper_obj.create_instances()
    scraper_obj.merge_outputs() 

