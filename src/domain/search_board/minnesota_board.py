import sys, os, time
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
            license_no = all_info.get("license_number", "")
            first_name = all_info.get("first_name", "")
            last_name = all_info.get("last_name", "")
            npi_number = all_info.get("npi_number", "")
            email_value = None

            try:
                driver.get(path_obj.minnesota_med_board_url)

                if license_no:
                    license_input = wait.until(EC.presence_of_element_located((By.ID, "LicenseNumber")))
                    license_input.clear()
                    license_input.send_keys(license_no)
                else:
                    first_name_input = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
                    last_name_input = driver.find_element(By.ID, "lastName")
                    first_name_input.clear()
                    first_name_input.send_keys(first_name)
                    last_name_input.clear()
                    last_name_input.send_keys(last_name)

                search_button = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "body > reach-app-root > div.layout-wrapper.reach-layout-wrapper.p-input-filled "
                    "> div.layout-content.reach-layout-content > online-entity-search > div:nth-child(3) "
                    "> div > div > div.p-ml-2 > button"
                )))
                search_button.click()

                rows = [r for r in driver.find_elements(
                    By.CSS_SELECTOR, "online-entity-search-results table tbody tr"
                ) if r.is_displayed()]

                if len(rows) >= 2:
                    matched_row = None
                    for idx, row in enumerate(rows, start=1):
                        try:
                            name_text = row.find_element(
                                By.CSS_SELECTOR, "td:nth-child(2) div div.ng-star-inserted"
                            ).text.strip()
                            if name_match_obj.is_name_match(first_name, last_name, name_text):
                                matched_row = idx
                                break
                        except Exception:
                            print("Could not read name")

                    if matched_row:
                        try:
                            row_selector = (
                                f"online-entity-search-results table tbody tr:nth-child({matched_row}) "
                                "td:nth-child(2) div div.ng-star-inserted"
                            )
                            row_elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, row_selector)))
                            driver.execute_script("arguments[0].click();", row_elem)
                            print(f"Expanded record for {first_name} {last_name}")
                        except Exception:
                            print(f"Matched Name Not clicked")
                    else:
                        print("No matching name found")

                try:
                    details_section = wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "#printKey reach-container licensee-list"
                    )))
                    email_label = details_section.find_element(
                        By.XPATH, ".//span[contains(normalize-space(.), 'Email')]"
                    )
                    email_value_span = email_label.find_element(
                        By.XPATH, "./following-sibling::span[contains(@class, 'p-col')]"
                    )
                    email_value = email_value_span.text.strip()
                    print(f"Extracted Email: {email_value}")
                except Exception as e:
                    print(f"Email not found or extracted for {license_no}: {e}")
                    email_value = None

                data = {
                    "National Provider Identifier": [npi_number],
                    "Name": [f"{first_name} {last_name}"],
                    "Email": [email_value],
                }

                if not email_value or email_value.strip() in ["", "-", "N/A", "None", "NA"]:
                    return None

                return pd.DataFrame(data)

            except Exception as inner_err:
                ERRORIO().write_file(inner_err)
                return None

        except Exception as err:
            ERRORIO().write_file(err)
            return None


mn_obj = Minnesota()
