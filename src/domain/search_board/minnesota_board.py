import sys, os, time
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from src.domain.helper.name_match import name_match_obj
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException


class Minnesota:
    def __init__(self):
        pass

    def wait_for_overlay(self, wait):
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".reach-blockui-transparent")))
        except Exception:
            pass
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".reach-blockui-transparent")))
        except Exception:
            pass

    def safe_click(self, driver, element):
        try:
            driver.execute_script("arguments[0].click();", element)
        except (ElementClickInterceptedException, ElementNotInteractableException):
            element.click()

    def enter_details(self, driver, wait, **all_info):
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

            
            search_btn_element = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "body > reach-app-root > div.layout-wrapper.reach-layout-wrapper.p-input-filled "
                "> div.layout-content.reach-layout-content > online-entity-search > div:nth-child(3) "
                "> div > div > div.p-ml-2 > button"
            )))
            self.safe_click(driver, search_btn_element)
            self.wait_for_overlay(wait)

            wait.until(lambda d: len([r for r in d.find_elements(
                By.CSS_SELECTOR, "online-entity-search-results table tbody tr"
            ) if r.is_displayed()]) >= 1)

            rows = [r for r in driver.find_elements(
                By.CSS_SELECTOR, "online-entity-search-results table tbody tr:not(.ng-star-inserted-hidden)"
            ) if r.is_displayed()]

            matched_row_elem = None
            for row in rows:
                try:
                    name_text = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) div div.ng-star-inserted").text.strip()
                    if name_match_obj.is_name_match(first_name, last_name, name_text):
                        matched_row_elem = row
                        break
                except NoSuchElementException:
                    continue

            if not matched_row_elem:
                print("No matching row found.")
                return None

            driver.execute_script("arguments[0].scrollIntoView(true);", matched_row_elem)

            try:
                next_row = matched_row_elem.find_element(By.XPATH, "following-sibling::tr[1]")
                email_span = next_row.find_element(By.XPATH, ".//span[contains(text(), '@')]")
                email_value = email_span.text.strip()
            except NoSuchElementException:
                self.safe_click(driver, matched_row_elem)
                self.wait_for_overlay(wait)
                details_section = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "licensee-details-section")
                ))
                email_label = details_section.find_element(By.XPATH, ".//span[contains(text(), 'Email')]")
                email_value_span = email_label.find_element("./following-sibling::span")
                email_value = email_value_span.text.strip()

            if not email_value or email_value.strip() in ["", "-", "N/A", "None", "NA"]:
                return None

            data = {
                "National Provider Identifier": [npi_number],
                "Name": [f"{first_name} {last_name}"],
                "Email": [email_value],
            }

            return pd.DataFrame(data)

        except Exception as err:
            ERRORIO().write_file(err)
            return None


mn_obj = Minnesota()
