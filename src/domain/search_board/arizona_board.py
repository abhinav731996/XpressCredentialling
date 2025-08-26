import sys, os,re,json
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ARIZONA:
    def __init__(self):
        pass

    def normalize_name(self,name):
        name = name.lower()
        name = re.sub(r'[^\w\s]', '', name)
        return name.split()

    def names_have_overlap(self,input_first, input_last, florida_name_raw):
        input_parts = self.normalize_name(f"{input_first} {input_last}")
        florida_parts = self.normalize_name(florida_name_raw)

        common = set(input_parts) & set(florida_parts)
        return len(common) > 0

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
                    driver.get(path_obj.arizona_lookup_url)

                    if lic:
                        license_input = wait.until(EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_txtLicNum")))
                        license_input.clear()
                        license_input.send_keys(lic)
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

                    result_link = wait.until(EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "#ContentPlaceHolder1_dtgList > tbody > tr.headerBlue.Verdana10Center > td:nth-child(1) > a > u"
                    )))
                    result_link.click()

                    WebDriverWait(driver, 7).until(lambda d: len(d.window_handles) > 1)
                    
                    driver.switch_to.window(driver.window_handles[-1])

                    
                    name_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral_lblLeftColumnEntName_0 > b")
                    ))
                    doctor_name = name_element.text.strip()
                    print("Doctor's Name:", doctor_name)

                    
                    clinic_info_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral_lblLeftColumnPracAddr_0")
                    ))
                    clinic_raw_html = clinic_info_element.get_attribute('innerHTML')

                    
                    lines = [line.strip() for line in re.split(r'<br\s*/?>', clinic_raw_html) if line.strip()]

                    clinic_name = lines[0] if len(lines) > 0 else ""
                    clinic_address = "\n".join(lines[1:3]) if len(lines) >= 3 else ""
                    clinic_phone = next((line for line in lines if "Phone:" in line), "")

                    print("Clinic Name:", clinic_name)
                    print("Clinic Address:", clinic_address)
                    print("Clinic Phone:", clinic_phone)

                    license_info_element = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#ContentPlaceHolder1_dtgGeneral > tbody > tr > td:nth-child(2)")
                    ))
                    license_info_text = license_info_element.text

                    match = re.search(r"License Number:\s*(\d+)", license_info_text)
                    license_number = match.group(1) if match else "Not Found"

                    print("License Number:", license_number)

                    data = [{
                        "npi": npi_number,
                        "license_number": license_number,
                        "primary_address": clinic_address,
                        "name": doctor_name,
                        "clinic_name": clinic_name,
                        "clinic_phone": clinic_phone
                    }]

                    print(json.dumps(data,indent=3))
                    result_df = pd.DataFrame(data)
                    print(result_df)
                    return result_df

                except Exception:
                    continue

            return None 

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)
            return None

az_obj = ARIZONA()
