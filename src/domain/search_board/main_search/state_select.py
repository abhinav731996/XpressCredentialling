import pandas as pd
import os, sys, ast
import time, random,re
sys.path.append(os.getcwd())
from src.domain.search_board.florida_board import fl_obj
from src.domain.file_io.io_file import ERRORIO
from src.domain.path.project_paths import path_obj
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

class Med_info:
    def __init__(self):
        pass

    def clean_license(self, df, state):
        if state in ["TX", "FL"] and "license_number" in df.columns:
            df["license_number"] = df["license_number"].astype(str).str.replace("License Number:", "").str.strip()
        return df

    def write_file(self, select_state, state_df_result, chunk_id):
        try:
            df = self.clean_license(state_df_result.copy(), select_state)

            output_dir = Path(path_obj.temp_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / f"{select_state}_chunk_{chunk_id}.xlsx"
            df.to_excel(output_file, index=False)
            print(f"[{os.getpid()}] Wrote chunk to {output_file}")
        except Exception as e:
            ERRORIO().write_file(file_data=ERRORIO().get_errdetails(e), path=path_obj.error_details_file)

    def normalize_license(self,license_number: str) -> list[str]:
        try:
            if not license_number:
                return []

            variants = set()
            lic = license_number.strip()

            variants.add(lic)
            variants.add(lic.replace(" ", ""))
            variants.add(re.sub(r"([A-Za-z]+)(\d+)", r"\1 \2", lic.replace(" ", "")))
            variants.add(lic.replace("-", ""))

            return list(variants)
        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(file_data=err_obj.get_errdetails(err), path=path_obj.error_details_file, mode="a")


    def enter_info(self, npi_df: pd.DataFrame, state_code: str, chunk_id: int):
        try:
            options = Options()
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 15)

            results = []

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

                fl_primary_taxonomy = None
                fl_any_taxonomy = None

                for taxo in taxonomies:
                    if not isinstance(taxo, dict):
                        continue

                    state = (taxo.get("state") or "").strip().upper()
                    is_primary = taxo.get("primary", False)

                    if state == "FL" and is_primary:
                        fl_primary_taxonomy = taxo
                        break  
                    elif state == "FL" and not fl_any_taxonomy:
                        fl_any_taxonomy = taxo 

                selected_taxonomy = fl_primary_taxonomy or fl_any_taxonomy

                if selected_taxonomy:
                    license_number = (selected_taxonomy.get("license") or "").strip()
                    taxonomy_state = "FL"

                    if re.fullmatch(r"\d+", license_number):
                        license_variants = [f"MS{license_number}", f"OS{license_number}"]
                    else:
                        license_variants = self.normalize_license(license_number)
                else:
                    license_number = ""
                    taxonomy_state = state_code
                    license_variants = []

                all_info = {
                    "npi_number": npi_number,
                    "license_number": license_number,
                    "license_variants": license_variants, 
                    "first_name": first_name,
                    "last_name": last_name,
                    "state_code": taxonomy_state
                }

                print(f"[{os.getpid()}] Searching NPI: {npi_number}... with license variants {license_variants}")

                try:
                    if taxonomy_state == "FL":
                        state_df_result = fl_obj.enter_details(driver, wait, **all_info)
                        if state_df_result is not None and not state_df_result.empty:
                            results.append(state_df_result)
                    else:
                        print(f"Unsupported state: {taxonomy_state}")
                        continue
                except Exception as err:
                    ERRORIO().write_file(file_data=ERRORIO().get_errdetails(err), path=path_obj.error_details_file)

                time.sleep(random.uniform(1, 2))

            if results:
                final_df = pd.concat(results, ignore_index=True)
                self.write_file(state_code, final_df, chunk_id)

            driver.quit()

        except Exception as err:
            ERRORIO().write_file(file_data=ERRORIO().get_errdetails(err), path=path_obj.error_details_file)
