import os,sys,glob
sys.path.append(os.getcwd())
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from src.domain.search_board.main_search.state_select import Med_info
from src.domain.path.project_paths import path_obj
from src.domain.file_io.io_file import ERRORIO
import glob
import traceback

class SCRAPPER:
    def __init__(self):
        try:
            # self.df = pd.read_excel(r"D:\Repositories\XpressCredentialling\test_surg_exl.xlsx")
            self.df = pd.read_excel(path_obj.all_states_surgery_npi_result)
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
            print("err caught from run_parellel_scrapper mod /process_chunk()")
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
                    try:
                        result = future.result() 
                    except Exception as err:
                        print(f"[ERROR] Future failed: {err}")
                        err_obj = ERRORIO()
                        err_obj.write_file(traceback.format_exc())

        except KeyboardInterrupt:
            print("\n handling manual key interupt by mistake")
            executor.shutdown(wait=False, cancel_futures=True)
            raise
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(traceback.format_exc())
   
    def export_final_excel(self):
        import sqlite3
        db_path = path_obj.combined_chunks_file.replace(".xlsx", ".db")
        output_path = path_obj.combined_chunks_file

        # Ensure table exists before reading
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS npi_data (
                    npi_number TEXT,
                    license_number TEXT,
                    license_variants TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    state_code TEXT
                )
            """)
            df = pd.read_sql("SELECT * FROM npi_data", conn)

        df.to_excel(output_path, index=False)
        print(f"[Export] Final Excel saved to {output_path}")




