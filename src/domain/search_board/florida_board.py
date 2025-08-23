import sys, os
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC

class Florida:
    def __init__(self):
        pass

    def enter_details(self, driver, wait, **all_info):
        try:
            license_variants = all_info.get("license_variants", [])
            first_name = all_info.get("first_name", "")
            last_name = all_info.get("last_name", "")
            npi_number = all_info.get("npi_number", "")

            for lic in license_variants if license_variants else [all_info.get("license_number")]:
                try:
                    driver.get(path_obj.florida_med_board_url)

                    if lic:
                        license_input = wait.until(EC.presence_of_element_located((By.ID, "SearchDto_LicenseNumber")))
                        license_input.clear()
                        license_input.send_keys(lic)
                    else: 
                        first_name_input = wait.until(EC.presence_of_element_located((By.ID, "SearchDto_FirstName")))
                        last_name_input = driver.find_element(By.ID, "SearchDto_LastName")
                        zip_input = driver.find_element(By.ID, "SearchDto_ZipCode")
                        city_input = driver.find_element(By.ID, "SearchDto_City")

                        first_name_input.clear()
                        first_name_input.send_keys(first_name)
                        last_name_input.clear()
                        last_name_input.send_keys(last_name)
                        zip_input.clear()
                        zip_input.send_keys(all_info.get("zip_code", ""))
                        city_input.clear()
                        city_input.send_keys(all_info.get("city_name", ""))

                    search_button = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "fieldset.form-horizontal p.text-center input.btn.btn-primary")))
                    search_button.click()

                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div#content div.p-h-md.p-v.pos-rlt h3:nth-of-type(2)")))
                    license_number_found = driver.find_element(
                        By.CSS_SELECTOR, "div#content div.p-h-md.p-v.pos-rlt h3:nth-of-type(2)").text.strip()

                    fourth_tab = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-tabs.col-md-12 li:nth-child(4) a")
                    fourth_tab.click()

                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-content div.tab-pane.active")))
                    to_upper_divs = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane.active div.toUpper")

                    if len(to_upper_divs) >= 5:
                        name = to_upper_divs[0].text.strip()
                        primary_address = " ".join([d.text.strip() for d in to_upper_divs[1:5]])
                    else:
                        name = ""
                        primary_address = ""

                    xyz_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#General > div")))

                    email_p = None
                    for p in xyz_div.find_elements(By.TAG_NAME, "p"):
                        if "Please contact at:" in p.text:
                            email_p = p
                            break

                    email = email_p.find_element(By.TAG_NAME, "strong").text.strip() if email_p else ""

                    data = {
                        "npi": npi_number,
                        "license_number": [license_number_found],
                        "primary_address": [primary_address],
                        "name": [name],
                        "email": [email]
                    }

                    return pd.DataFrame(data) 

                except Exception:
                    continue

            return None 

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(file_data=err_obj.get_errdetails(err), path=path_obj.error_details_file, mode="a")
            return None


fl_obj = Florida()
