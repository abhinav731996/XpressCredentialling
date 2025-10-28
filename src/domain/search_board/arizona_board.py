import sys, os,re,json,time
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.domain.helper.name_match import name_match_obj
import traceback


class ARIZONA:
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

            for lc_no in licenses_to_check:
                try:
                    driver.get(path_obj.arizona_lookup_url)

                    if lc_no:
                        license_input = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtLicNum")))
                        license_input.clear()
                        license_input.send_keys(lc_no)
                    else:
                        first_name_input = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtFirstName")))
                        last_name_input = driver.find_element(By.ID, "ContentPlaceHolder1_txtFirstName")

                        first_name_input.clear()
                        first_name_input.send_keys(first_name)
                        last_name_input.clear()
                        last_name_input.send_keys(last_name)

                    driver.find_element(By.ID, "ContentPlaceHolder1_rbLicense1").click()

                    license_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ContentPlaceHolder1_btnLicense")))
                    license_button.click()

                    name_cell = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((
                            By.CSS_SELECTOR,
                            "#ContentPlaceHolder1_dtgList > tbody > tr.headerBlue.Verdana10Center > td:nth-child(2)"
                        ))
                    )

                    name_text = name_cell.text.strip()

                    if "Specialty" in name_text:
                        name_only = name_text.split("Specialty")[0].strip()
                    else:
                        name_only = name_text

                    if name_match_obj.is_name_match(first_name, last_name,name_only):
                        result_link = wait.until(EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            "#ContentPlaceHolder1_dtgList > tbody > tr.headerBlue.Verdana10Center > td:nth-child(1) > a > u"
                        )))
                        result_link.click()
                    else:
                        print(f"Details dont match for {lc_no}...Checking next License Number")
                        continue

                    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
                    driver.switch_to.window(driver.window_handles[-1])

                    
                    name_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral_lblLeftColumnEntName_0 > b")
                    ))
                    doctor_name = name_element.text.strip()
                                        
                    clinic_info_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral_lblLeftColumnPracAddr_0")
                    ))
                    clinic_raw_html = clinic_info_element.get_attribute('innerHTML')
                    
                    lines = [line.strip() for line in re.split(r'<br\s*/?>', clinic_raw_html) if line.strip()]

                    if lines:
                        if re.match(r'^\d+', lines[0]):
                            clinic_name = ""
                            clinic_address = "\n".join(lines[0:2]) if len(lines) >= 2 else lines[0]
                        else:
                            clinic_name = lines[0]
                            clinic_address = "\n".join(lines[1:3]) if len(lines) >= 3 else ""
                    else:
                        clinic_name = ""
                        clinic_address = ""

                    clinic_phone = ""

                    for line in lines:
                        if "phone:" in line.lower():
                            raw_phone_line = line.strip()
                            phone_label_removed = re.sub(r'(?i)phone:\s*', '', raw_phone_line)
                            clinic_phone = phone_label_removed.strip()
                            break

                    license_info_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral > tbody > tr > td:nth-child(2)")
                    ))
                    license_info_text = license_info_element.text

                    match = re.search(r"License Number:\s*(\d+)", license_info_text)
                    license_number = match.group(1) if match else "Not Found"


                    data = [{
                        "National Provider Identifier": npi_number,
                        # "License": license_number,
                        "primary_address": clinic_address,
                        "Name": doctor_name,
                        "clinic_name": clinic_name,
                        "clinic_phone": clinic_phone
                    }]

                    result_df = pd.DataFrame(data)
                    return result_df

                except Exception as err:
                    print(f"Check err log for {npi_number} in Except block")
                    err_obj = ERRORIO()
                    err_obj.write_file(traceback.format_exc())
                    continue

                finally:
                    try:
                        if driver.session_id:
                            handles = driver.window_handles
                            if len(handles) > 1:
                                current_handle = driver.current_window_handle
                                original_handle = handles[0]
                                if current_handle != original_handle:
                                    driver.close()
                                    if original_handle in driver.window_handles:
                                        driver.switch_to.window(original_handle)
                    except Exception:
                        print(f"Check err log for {npi_number} caught in fianlly block")
                        # print("Check err log in finally block")
                        err_obj = ERRORIO()
                        err_obj.write_file(traceback.format_exc())


            return None 

        except Exception as err:
            print("Check err log")
            err_obj = ERRORIO()
            err_obj.write_file(err)
            return None

az_obj = ARIZONA()
