import sys, os, time
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from selenium.webdriver.common.by import By
from src.domain.file_io.io_file import ERRORIO
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from src.domain.helper.name_match import name_match_obj
from selenium.webdriver.common.keys import Keys

class Surgery:
    def __init__(self):
        pass

    def enter_details(self, driver, wait, **all_info):
        try:
            first_name = all_info.get("first_name", "")
            last_name = all_info.get("last_name", "")
            npi_number = all_info.get("npi_number", "") 

            driver.get(path_obj.american_board_surgeon)

            name_input = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "input.listing-filter-profile-search__search-textfield.js-search-term"
            )))
            name_input.clear()
            fullName = first_name + " " + last_name
            name_input.send_keys(fullName)
            name_input.send_keys(Keys.ENTER)

            try:
                cookie_banner = driver.find_element(By.CSS_SELECTOR, "div.osano-cm-dialog__content")
                accept_button = cookie_banner.find_element(By.CSS_SELECTOR, "button")
                accept_button.click()
                time.sleep(1)
            except:
                pass

            first_result = wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.listing__results.js-results-container h2"
            )))
            time.sleep(5)
            first_result.click()



            email_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.profile-info-card__contact-row a[href^='mailto:']"
                ))
            )

            email_href = email_link.get_attribute("href")  
            email_address = email_href.replace("mailto:", "")
            # print("Email address found:", email_address)


            data = {
                "npi": [npi_number],
                "name": [fullName],
                "email": [email_address],
            }

            result_df = pd.DataFrame(data)
            print("result_df")
            print(npi_number)
            print(fullName)
            print(email_address)

            return result_df

        except Exception as err:
            err_obj = ERRORIO()
            err_obj.write_file(err)
            return None

surgery_obj = Surgery()
