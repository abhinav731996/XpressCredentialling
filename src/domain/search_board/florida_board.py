import sys, os,re
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.domain.helper.name_match import name_match_obj

class Florida:
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

                    # wait.until(EC.presence_of_element_located(
                    #     (By.CSS_SELECTOR, "div#content div.p-h-md.p-v.pos-rlt h3:nth-of-type(2)")))
                    # license_number_found = driver.find_element(
                    #     By.CSS_SELECTOR, "div#content div.p-h-md.p-v.pos-rlt h3:nth-of-type(2)").text.strip()

                    practitioner_profile_tab = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class,'nav-tabs')]//a[text()='Practitioner Profile']"))
                    )
                    practitioner_profile_tab.click()

                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-content div.tab-pane.active")))

                    to_upper_divs = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane.active div.toUpper")
                    if len(to_upper_divs) >= 5:
                        site_name = to_upper_divs[0].text.strip()
                        
                        # function that check names(Loosely) Nppes & Specific website  
                        is_matched = name_match_obj.is_name_match(first_name, last_name, site_name)
                        
                        if not is_matched:
                            continue
                        address_parts = []
                        for div in to_upper_divs[1:5]:
                            address_parts.append(div.text.strip())
                        primary_address = " ".join(address_parts)    
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

                    # edu_tab = wait.until(EC.element_to_be_clickable(
                    #     (By.CSS_SELECTOR, "#content > div > div:nth-child(8) > ul > li:nth-child(2) > a")
                    # ))
                    # edu_tab.click()

    
                    # wait.until(EC.presence_of_element_located((By.ID, "EducationAndTraining")))

                    # education_data = []
                    # indices = [3, 6, 9]

                    # for idx in indices:
                    #     try:
                    #         selector = f"#EducationAndTraining > table:nth-child({idx}) > tbody > tr > td:nth-child(1)"
                    #         edu_td = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    #         education_data.append(edu_td.text.strip())
                    #     except:
                    #         education_data.append("")

                    # education_data = (education_data + ["", "", ""])[:3]
                    full_name = f"{first_name} {last_name}"
                    data = {
                        "National Provider Identifier": npi_number,
                        "Name": [full_name],
                        "Email": [email],
                        # "License": [license_number_found],
                        # "primary_address": [primary_address],

                        # "institution_name": [education_data[0]],
                        # "university_school": [education_data[1]],
                        # "program_name": [education_data[2]]
                    }
                    result_df = pd.DataFrame(data)
                    
                    return result_df

                except Exception as err:
                    err_obj = ERRORIO()
                    err_obj.write_file(err)
                    continue

            return None 

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)
            return None

fl_obj = Florida()
