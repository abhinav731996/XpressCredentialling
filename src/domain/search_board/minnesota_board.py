import sys, os
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from src.domain.helper.name_match import name_match_obj

class Minnesota:
    def __init__(self):
        pass

    def enter_details(self, driver, wait, **all_info):
        try:
            license_variants = all_info.get("license_variants", [])
            first_name = all_info.get("first_name", "")
            last_name = all_info.get("last_name", "")
            npi_number = all_info.get("npi_number", "")

            if license_variants:
                licenses_to_check = license_variants
            else:
                licenses_to_check = [all_info.get("license_number")]

            for lic in licenses_to_check:
                email_value = None
                try:
                    driver.get(path_obj.minnesota_med_board_url)

                    if lic:
                        license_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "LicenseNumber"))
                        )
                        license_input.clear()
                        license_input.send_keys(lic)
                    else:
                        first_name_input = wait.until(
                            EC.presence_of_element_located((By.ID, "firstName"))
                        )
                        last_name_input = driver.find_element(By.ID, "lastName")
                        # zip_input = driver.find_element(By.ID, "SearchDto_ZipCode")
                        # city_input = driver.find_element(By.ID, "SearchDto_City")

                        first_name_input.clear()
                        first_name_input.send_keys(first_name)
                        last_name_input.clear()
                        last_name_input.send_keys(last_name)


                    search_button = wait.until(
                        EC.element_to_be_clickable((
                            By.XPATH,
                            "//span[@class='p-button-label' and text()='Search']"
                        ))
                    )
                    search_button.click()

                    wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "online-entity-search-results table"
                    )))

                    rows = driver.find_elements(
                        By.CSS_SELECTOR,
                        "online-entity-search-results table tbody tr"
                    )

                    if len(rows) >= 2:
                        matched_row = None
                        for idx, row in enumerate(rows, start=1):
                            try:
                                name_element = row.find_element(
                                    By.CSS_SELECTOR,
                                    "td:nth-child(2) div div.ng-star-inserted"
                                )
                                name_text = name_element.text.strip()

                                if name_match_obj.is_name_match(first_name, last_name, name_text):
                                    matched_row = idx
                                    break
                            except Exception as e:
                                print(f"Could not read name from row {idx}: {e}")

                        if matched_row:
                            try:
                                row_name_selector = (
                                    f"online-entity-search-results table tbody tr:nth-child({matched_row}) "
                                    "td:nth-child(2) div div.ng-star-inserted"
                                )
                                row_name_element = wait.until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, row_name_selector))
                                )
                                row_name_element.click()
                                print(f"Expanded record for {first_name} {last_name}")
                            except Exception as e:
                                print(f"Matched Name Not clicked")
                        else:
                            print("No matching name found")
                    else:
                        print("Single result auto. opens no need to click")

                    try:
                        email_element = wait.until(EC.presence_of_element_located((
                            By.CSS_SELECTOR,
                            "#printKey > div:nth-child(2) > reach-container > licensee-list "
                            "> div > div.ng-star-inserted > div > div:nth-child(5) > span.p-col"
                        )))
                        email_value = email_element.text.strip()
                    except Exception as e:
                        email_value = None
                        print(f"Email not Found or Extarcted")

                    data = {
                        "National Provider Identifier": [npi_number],
                        "Name": [f"{first_name} {last_name}"],
                        "Email": [email_value],
                    }

                    if not email_value or email_value.strip() in ["", "-", "N/A", "None", "NA"]:
                        return None

                    result_df = pd.DataFrame(data)
                    return result_df
                    
                except Exception as inner_err:
                    err_obj = ERRORIO()
                    err_obj.write_file(inner_err)
                    continue

            return None

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)
            return None


mn_obj = Minnesota()