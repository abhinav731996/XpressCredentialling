from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.domain.path.project_paths import path_obj
from src.domain.file_io.io_file import ERRORIO
# from src.domain.search_board.arizona_board import az_obj
from src.domain.search_board.florida_board import fl_obj
from src.domain.search_board.all_states_surgery.speciality_surgery import surgery_obj
from src.domain.search_board.minnesota_board import mn_obj
from src.domain.helper.save_db import save_db_obj
import pandas as pd
import os
import sys
import ast
import time
import random
import re

sys.path.append(os.getcwd())


class Med_info:
    def __init__(self):
        pass

    def clean_license(self, df, state):
        if state in ["AZ", "FL"] and "license_number" in df.columns:
            df["license_number"] = (
                df["license_number"].astype(str)
                .str.replace("License Number:", "")
                .str.strip()
            )
        return df

    def normalize_license(self, license_number: str) -> list[str]:
        try:
            if not license_number:
                return []

            variants = set()
            lic = license_number.strip()
            variants.add(lic)
            variants.add(lic.replace(" ", ""))
            variants.add(lic.replace("-", ""))

            return list(variants)
        except Exception as err:
            print("Check err log")
            err_obj = ERRORIO()
            err_obj.write_file(err)

    def enter_info(self, npi_df: pd.DataFrame, chunk_id: int):
        try:
            db_path = path_obj.combined_chunks_file.replace(".xlsx", ".db")

            options = Options()
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--headless=new")
            # options.add_argument("--start-maximized")
            options.add_argument("--silent")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])

            service = Service(ChromeDriverManager().install())
            orig_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            driver = webdriver.Chrome(service=service, options=options)
            sys.stderr.close()
            sys.stderr = orig_stderr
            wait = WebDriverWait(driver, 30)

            selected_state = {
                "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
                "DC", "AS", "GU", "MP", "PR", "VI",
            }

            test_df = pd.read_excel(path_obj.all_states_surgery_npi_test, dtype=str)

            for _, record in npi_df.iterrows():
                npi_number = str(record["number"]).strip()
                first_name = record.get("basic.first_name", "")
                last_name = record.get("basic.last_name", "")

                row_taxonomies = record.get("taxonomies", []) # [] or "[]"
                if isinstance(row_taxonomies, str): 
                    try:
                        taxonomies = ast.literal_eval(row_taxonomies) # converts string into actual py obj(json loads can also be used but be sure json property is in double qoutes and not single)
                    except Exception:
                        pass
                        
                else:
                    taxonomies = row_taxonomies

                enrollment_state = ""
                match_row = test_df.loc[test_df["National Provider Identifier"].astype(str) == npi_number]
                if not match_row.empty:
                    enrollment_state = (str(match_row.iloc[0]["Enrollment State Code"]).strip().upper())

                selected_taxonomy = None
                license_number = ""
                taxonomy_state = enrollment_state or ""

                if taxonomy_state:
                    for taxo in taxonomies:
                        if not isinstance(taxo, dict):
                            continue

                        taxo_state = (taxo.get("state") or "").strip().upper()
                        if taxo_state == taxonomy_state:
                            selected_taxonomy = taxo
                            license_number = (taxo.get("license") or "").strip()
                            break

                    if not selected_taxonomy:
                        print(f"No taxonomy match for state {taxonomy_state} in NPI {npi_number}. Skipping this NPI.")
                        continue  
                else:
                    print(f"No enrollment state found for NPI {npi_number}. Skipping.")
                    continue

                if re.fullmatch(r"\d+", license_number) and taxonomy_state == "FL":
                    license_variants = [f"ME{license_number}", f"OS{license_number}"]
                    
                elif taxonomy_state == "MN":

                    license_variants = license_number
                else:

                    license_variants = self.normalize_license(license_number)

                if not taxonomy_state or taxonomy_state not in selected_state:
                    continue

                all_info = {
                    "npi_number": npi_number,
                    "license_number": license_number,
                    "license_variants": license_variants,
                    "first_name": first_name,
                    "last_name": last_name,
                    "state_code": taxonomy_state,
                }

                print(f"Searching NPI: {npi_number}  State: {taxonomy_state} | License: {license_number} | Name: {first_name} {last_name}")

                try:
                    if taxonomy_state == "MN":
                        state_df_result = mn_obj.enter_details(driver, wait, **all_info)
                    elif taxonomy_state == "FL":
                        state_df_result = fl_obj.enter_details(driver, wait, **all_info)
                    else:
                        desc = (selected_taxonomy.get("desc") or "")
                        if "surgery" in desc.lower():
                            state_df_result = surgery_obj.enter_details(driver, wait, **all_info)
                        else:
                            continue

                    if (state_df_result is None or not isinstance(state_df_result, pd.DataFrame) or state_df_result.empty):
                        continue
                    print(state_df_result)
                    save_db_obj.realtime_save_in_db(state_df_result)

                except Exception as err:
                    print("Check err log")
                    err_obj = ERRORIO()
                    err_obj.write_file(err)

                time.sleep(random.uniform(1, 2))

            driver.quit()

        except Exception as err:
            print("Check err log")
            err_obj = ERRORIO()
            err_obj.write_file(err)
