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

    def merge_outputs(self):
        try: 
            os.makedirs(path_obj.temp_output_dir, exist_ok=True)

            # Read all chunk files
            chunk_files = glob.glob(os.path.join(path_obj.temp_output_dir, "*.xlsx"))
            all_dfs = []

            for file in chunk_files:
                try:
                    df = pd.read_excel(file)
                    if df is not None and not df.empty:
                        df.columns = df.columns.astype(str).str.strip()
                        all_dfs.append(df)
                    else:
                        print(f"[Merge] Skipping empty file: {file}")
                except Exception as e:
                    ERRORIO().write_file(e)

            if not all_dfs:
                print("[Merge] No data collected to merge.")
                return

            # Combine all chunks
            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df.columns = combined_df.columns.astype(str).str.strip()

            # Check if a previous master file exists
            output_path = path_obj.combined_chunks_file
            if os.path.exists(output_path):
                try:
                    master_df = pd.read_excel(output_path)
                    if master_df is None or master_df.empty:
                        master_df = pd.DataFrame()
                    else:
                        master_df.columns = master_df.columns.astype(str).str.strip()
                except Exception as e:
                    ERRORIO().write_file(e)
                    master_df = pd.DataFrame()
            else:
                master_df = pd.DataFrame()

            # Merge data if master_df exists
            if not master_df.empty:
                key_col = "National Provider Identifier"
                if key_col not in master_df.columns or key_col not in combined_df.columns:
                    print(f"[Merge] Key column '{key_col}' missing. Skipping merge.")
                    final_df = pd.concat([master_df, combined_df], ignore_index=True)
                else:
                    master_df.set_index(key_col, inplace=True)
                    combined_df.set_index(key_col, inplace=True)

                    for col in combined_df.columns:
                        master_df[col] = combined_df[col].combine_first(master_df.get(col))

                    master_df.reset_index(inplace=True)
                    final_df = master_df
            else:
                final_df = combined_df

            # Remove any leftover 'index' column
            if 'index' in final_df.columns:
                final_df = final_df.drop(columns=['index'])

            # Save final file
            final_df.to_excel(output_path, index=False)
            print(f"[Merge] Saved final merged result to {output_path}")

        except Exception as err:
            print("Check err log")
            ERRORIO().write_file(err)


    # def merge_outputs(self):
    #     try: 
    #         os.makedirs(path_obj.temp_output_dir, exist_ok=True)

    #         # Read all chunk files
    #         chunk_files = glob.glob(os.path.join(path_obj.temp_output_dir, "*.xlsx"))
    #         all_dfs = []

    #         for file in chunk_files:
    #             try:
    #                 df = pd.read_excel(file)
    #                 df.columns = df.columns.astype(str).str.strip()
    #                 all_dfs.append(df)
    #             except Exception as e:
    #                 ERRORIO().write_file(e)

    #         if not all_dfs:
    #             print("[Merge] No data collected to merge.")
    #             return

    #         # Combine all chunks
    #         combined_df = pd.concat(all_dfs, ignore_index=True)
    #         combined_df.columns = combined_df.columns.astype(str).str.strip()

    #         # If there's a previous master file, merge new data into it
    #         output_path = path_obj.combined_chunks_file
    #         if os.path.exists(output_path):
    #             master_df = pd.read_excel(output_path)
    #             master_df.columns = master_df.columns.astype(str).str.strip()

    #             # Merge on National Provider Identifier
    #             key_col = "National Provider Identifier"
    #             master_df.set_index(key_col, inplace=True)
    #             combined_df.set_index(key_col, inplace=True)

    #             for col in combined_df.columns:
    #                 master_df[col] = combined_df[col].combine_first(master_df.get(col))

    #             master_df.reset_index(inplace=True)
    #         else:
    #             master_df = combined_df.reset_index(drop=True)

    #         if 'index' in master_df.columns:
    #             master_df = master_df.drop(columns=['index'])

    #         master_df.to_excel(output_path, index=False)
    #         print(f"[Merge] Saved final merged result to {output_path}")

    #     except Exception as err:
    #         print("Check err log")
    #         ERRORIO().write_file(err)



    # def merge_outputs(self):
    #     try: 
    #         os.makedirs(path_obj.temp_output_dir, exist_ok=True)

    #         chunk_files = glob.glob(os.path.join(path_obj.temp_output_dir, "*.xlsx"))
    #         all_dfs = []

    #         for file in chunk_files:
    #             try:
    #                 df = pd.read_excel(file)
    #                 df.columns = df.columns.astype(str).str.strip()
    #                 all_dfs.append(df)
    #             except Exception as e:
    #                 ERRORIO().write_file(e)

    #         if not all_dfs:
    #             print("[Merge] No data collected to merge.")
    #             return

    #         new_data = pd.concat(all_dfs, ignore_index=True)
    #         new_data.columns = new_data.columns.astype(str).str.strip()

    #         output_path = path_obj.combined_chunks_file
    #         if os.path.exists(output_path):
    #             master_df = pd.read_excel(output_path)
    #             master_df.columns = master_df.columns.astype(str).str.strip()
    #         else:
    #             master_df = pd.DataFrame()

    #         if not master_df.empty:
    #             key_col = "National Provider Identifier"

    #             updated_df = master_df.copy()

    #             if "npi" in new_data.columns and "National Provider Identifier" not in new_data.columns:
    #                 new_data.rename(columns={"npi": "National Provider Identifier"}, inplace=True)

    #             master_df.set_index(key_col, inplace=True)
    #             new_data.set_index(key_col, inplace=True)

    #             for col in new_data.columns:
    #                 master_df[col] = new_data[col].combine_first(master_df.get(col))

    #             master_df.reset_index(inplace=True)
    #         else:
    #             master_df = new_data.reset_index()

    #         master_df.to_excel(output_path, index=False)
    #         print(f"[Merge] Saved final merged result to {output_path}")

    #     except Exception as err:
    #         print("Check err log")
    #         err_obj = ERRORIO()
    #         err_obj.write_file(err)

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

merge_obj = SCRAPPER()
merge_obj.merge_outputs()


