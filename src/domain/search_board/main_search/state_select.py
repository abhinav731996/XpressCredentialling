from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.domain.path.project_paths import path_obj
from src.domain.file_io.io_file import ERRORIO
from src.domain.search_board.arizona_board import az_obj
from src.domain.search_board.florida_board import fl_obj
from src.domain.search_board.all_states_surgery.speciality_surgery import surgery_obj
import pandas as pd
import os
import sys
import ast
import time
import random
import re
import sqlite3
sys.path.append(os.getcwd())
# import tempfile
# import shutil

# from src.domain.search_board.google_api import GOOGLESEARCAPI


class Med_info:
    def __init__(self):
        pass

    def clean_license(self, df, state):
        if state in ["AZ", "FL"] and "license_number" in df.columns:
            df["license_number"] = df["license_number"].astype(
                str).str.replace("License Number:", "").str.strip()
        return df

    # def write_file(self, select_state, state_df_result, chunk_id):
    #     try:
    #         df = self.clean_license(state_df_result.copy(), select_state)

    #         output_dir = Path(path_obj.temp_output_dir)
    #         output_dir.mkdir(parents=True, exist_ok=True)

    #         output_file = output_dir / f"chunk_{chunk_id}.xlsx"
    #         df.to_excel(output_file, index=False)
    #         print(f"[{os.getpid()}] Wrote chunk to {output_file}")
    #         # print(df)
    #     except Exception as err:
    #         print("Check err log")
    #         err_obj = ERRORIO()
    #         err_obj.write_file(err)

    def normalize_license(self, license_number: str) -> list[str]:
        try:
            if not license_number:
                return []

            variants = set()
            lic = license_number.strip()

            variants.add(lic)
            variants.add(lic.replace(" ", ""))
            variants.add(re.sub(r"([A-Za-z]+)(\d+)",
                         r"\1 \2", lic.replace(" ", "")))
            variants.add(lic.replace("-", ""))

            return list(variants)
        except Exception as err:
            print("Check err log")
            err_obj = ERRORIO()
            err_obj.write_file(err)

    def enter_info(self, npi_df: pd.DataFrame,  chunk_id: int):
        try:
            print(chunk_id)
            db_path = path_obj.combined_chunks_file.replace(".xlsx", ".db")
            options = Options()
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--headless=new")
            # options.add_argument('--start-maximized')
            options.add_argument("--log-level=0")  # 0 = ALL, 3 = SEVERE
            options.add_experimental_option(
                "excludeSwitches", ["enable-logging"])
            # options.add_argument("--no-sandbox")




            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(driver, 10)

            results = []
            selected_state = {
                "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
                "DC", "AS", "GU", "MP", "PR", "VI"
            }

            for _, record in npi_df.iterrows():
                npi_number = str(record["number"]).strip()
                first_name = record.get("basic.first_name", "")
                last_name = record.get("basic.last_name", "")

                row_taxonomies = record.get("taxonomies", [])
                if isinstance(row_taxonomies, str):
                    try:
                        taxonomies = ast.literal_eval(row_taxonomies)
                    except Exception:
                        taxonomies = []
                else:
                    taxonomies = row_taxonomies

                state_primary_taxonomy = None
                state_any_taxonomy = None

                for taxo in taxonomies:
                    if not isinstance(taxo, dict):
                        continue

                    state = (taxo.get("state") or "").strip().upper()
                    is_primary = taxo.get("primary", False)

                    if state in selected_state and is_primary:
                        state_primary_taxonomy = taxo
                        break
                    elif state in selected_state and not state_any_taxonomy:
                        state_any_taxonomy = taxo

                selected_taxonomy = state_primary_taxonomy or state_any_taxonomy

                if selected_taxonomy:
                    license_number = (selected_taxonomy.get(
                        "license") or "").strip()
                    taxonomy_state = (selected_taxonomy.get(
                        "state") or "").strip().upper()

                    if re.fullmatch(r"\d+", license_number) and taxonomy_state == "FL":
                        license_variants = [
                            f"ME{license_number}", f"OS{license_number}"]

                    elif taxonomy_state == "AZ":
                        match = re.fullmatch(
                            r"(az)?(\d+)", license_number, re.IGNORECASE)
                        if match:
                            license_variants = [match.group(2)]
                        # license_variants = [license_number]
                    else:
                        license_variants = self.normalize_license(license_number)
                else:
                    print(
                        f"[{os.getpid()}] No results found for chunk {chunk_id}")
                    license_number = ""
                    taxonomy_state = ""
                    license_variants = ""

                all_info = {
                    "npi_number": npi_number,
                    "license_number": license_number,
                    "license_variants": license_variants,
                    "first_name": first_name,
                    "last_name": last_name,
                    "state_code": taxonomy_state
                }

                # print(
                #     f"[{os.getpid()}] Searching NPI: {npi_number}... with license variants {license_variants}")
                
                try:
                    if taxonomy_state:
                        state_df_result = surgery_obj.enter_details(driver, wait, **all_info)

                        if state_df_result is None or not isinstance(state_df_result, pd.DataFrame) or state_df_result.empty:
                            continue
                        # retry logic for SQLite lock
                        for attempt in range(3):
                            try:
                                with sqlite3.connect(db_path, timeout=30) as conn:
                                    state_df_result.to_sql("npi_data", conn, if_exists="append", index=False)
                                break
                            except sqlite3.OperationalError as e:
                                if "database is locked" in str(e).lower():
                                    time.sleep(1)
                                else:
                                    raise    

                    # if taxonomy_state == "FL":
                    #     state_df_result = fl_obj.enter_details(driver, wait, **all_info)
                    #     if state_df_result is not None and not state_df_result.empty:
                    #         results.append(state_df_result)
                    #     else:
                    #         print("Try with search api")
                    #         # search_api_obj = GOOGLESEARCAPI()
                    #         # fallback_data = search_api_obj.get_details_searchapi(all_info["first_name"], all_info["last_name"],all_info["npi_number"])

                    #         # if fallback_data:
                    #         #     fallback_df = pd.DataFrame(fallback_data)
                    #         #     results.append(fallback_df)

                    #         # else:
                    #         #     print("Fallback also failed. No data found.")
                    # elif taxonomy_state == "AZ":
                    #     state_df_result = az_obj.enter_details(driver, wait, **all_info)
                    #     if state_df_result is not None and not state_df_result.empty:
                    #         results.append(state_df_result)
                    # else:
                    #     state_df_result = surgery_obj.enter_details(driver, wait, **all_info)

                    #     if state_df_result is None or not isinstance(state_df_result, pd.DataFrame) or state_df_result.empty:
                    #         continue
                    #     # retry logic for SQLite lock
                    #     for attempt in range(3):
                    #         try:
                    #             with sqlite3.connect(db_path, timeout=30) as conn:
                    #                 state_df_result.to_sql("npi_data", conn, if_exists="append", index=False)
                    #             break
                    #         except sqlite3.OperationalError as e:
                    #             if "database is locked" in str(e).lower():
                    #                 time.sleep(1)
                    #             else:
                    #                 raise    
                        # else:
                        #     results.append(state_df_result)

                except Exception as err:
                    print("Check err log")
                    err_obj = ERRORIO()
                    err_obj.write_file(err)

                time.sleep(random.uniform(1, 2))

            # if results:
            #     final_df = pd.concat(results, ignore_index=True)
            #     self.write_file(taxonomy_state, final_df, chunk_id)
            driver.quit()

        except Exception as err:
            print("Check err log")
            err_obj = ERRORIO()
            err_obj.write_file(err)
