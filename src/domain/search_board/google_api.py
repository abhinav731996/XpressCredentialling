import sys,os
sys.path.append(os.getcwd())
import requests, json,time,re, pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from src.domain.search_board.florida_board import fl_obj
API_KEY = ""

# update with your own search eng id
CX = "93b1ebc87c2ee42a3"


class GOOGLESEARCAPI:
    def __init__(self):
        self.google_api = "https://www.googleapis.com/customsearch/v1"

    def get_details_searchapi(self,first_name,last_name,npi_no):
        query = f"{first_name} {last_name} fl doh practitioner profile"
        params = {
            "key": API_KEY,
            "cx": CX,
            "q": query
        }

        response = requests.get(self.google_api, params=params)
        response.raise_for_status()

        found_link = None
        data = response.json()
        for item in data.get("items", []):
            if "FL DOH MQA Search Portal" in item["title"]:
                found_link = item["link"]
                break

        if not found_link:
            print("No Florida DOH link found.")

        if found_link:
            options = Options()
            # options.add_argument("--headless=new")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 15)

            driver.get(found_link)
    
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.tab-content div.tab-pane.active")))

            elmnt_for_license = driver.find_element(By.XPATH, "//h3[contains(text(), 'License Number')]")
            # elmnt_for_license = driver.find_element(By.CSS_SELECTOR, "div#content div.p-h-md.p-v.pos-rlt h3:nth-of-type(2)")
            only_license_no = elmnt_for_license.text.strip().replace("License Number: ", "").strip()


            to_upper_divs = driver.find_elements(By.CSS_SELECTOR, "div.tab-pane.active div.toUpper")
            if len(to_upper_divs) >= 5:
                name = to_upper_divs[0].text.strip()
                if not fl_obj.names_have_overlap(first_name, last_name, name):
                    print(f"Final fallback search api failed {npi_no}")
                    return None
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

            if email_p:
                email = email_p.find_element(By.TAG_NAME, "strong").text.strip() 
            else:
                email = ""

            
            data = [{
                "npi": npi_no,
                "license_number": only_license_no,
                "primary_address": primary_address,
                "name": name,
                "email": email
            }]

            print(json.dumps(data,indent=3))
            result_df = pd.DataFrame(data)
            print(result_df)
            return result_df
            
        
        time.sleep(1)
        driver.quit()


