import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Florida scraping class ---
class FloridaEmailScraper:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # background mode
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def scrape_emails(self):
        df = pd.read_excel(self.input_file)

        # Ensure 'email' column exists
        if "email" not in df.columns:
            df["email"] = ""

        for idx, row in df.iterrows():
            license_number = str(row["license_number"]).strip()

            if not license_number or license_number.lower() == "nan":
                continue

            try:
                print(f"Searching for license: {license_number}")
                self.driver.get(self.url)

                # Fill license number
                lic_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "SearchDto_LicenseNumber"))
                )
                lic_input.clear()
                lic_input.send_keys(license_number)

                # Click search
                search_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "fieldset.form-horizontal p.text-center input.btn.btn-primary")
                ))
                search_btn.click()

                # Wait for result
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div#content")
                ))

                email_found = ""

                # --- Search inside General Information and other tabs ---
                tabs = self.driver.find_elements(By.CSS_SELECTOR, "ul.nav.nav-tabs li a")
                for tab in tabs:
                    tab.click()
                    time.sleep(1)

                    active_tab = self.driver.find_element(By.CSS_SELECTOR, "div.tab-content div.tab-pane.active")
                    texts = active_tab.text.split("\n")

                    for t in texts:
                        if "@" in t:   # detect email
                            email_found = t.strip()
                            break

                    if email_found:
                        break

                # Save email in DataFrame
                df.at[idx, "email"] = email_found
                print(f"✔ {license_number} → {email_found}")

            except Exception as e:
                print(f"❌ Error for license {license_number}: {e}")
                continue

        # Save updated file
        df.to_excel(self.output_file, index=False)
        self.driver.quit()
        print("✅ Scraping completed. Emails saved to:", self.output_file)


# --- Run Example ---
if __name__ == "__main__":
    input_file = r"C:\Users\jai seya ram\OneDrive\Documents\rnd project\xpresscredentialling\license.xlsx"   # yaha us file ka naam daal jha license or npi number rkhe hai 
    output_file = r"C:\users\jai seya ram\OneDrive\Documents\rnd project\with_email2.xlsx"

    scraper = FloridaEmailScraper(input_file, output_file)
    scraper.scrape_emails()
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Florida scraping class ---
class FloridaEmailScraper:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # background mode
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def scrape_emails(self):
        df = pd.read_excel(self.input_file)

        # Ensure 'email' column exists
        if "email" not in df.columns:
            df["email"] = ""

        for idx, row in df.iterrows():
            license_number = str(row["license_number"]).strip()

            if not license_number or license_number.lower() == "nan":
                continue

            try:
                print(f"Searching for license: {license_number}")
                self.driver.get(self.url)

                # Fill license number
                lic_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "SearchDto_LicenseNumber"))
                )
                lic_input.clear()
                lic_input.send_keys(license_number)

                # Click search
                search_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "fieldset.form-horizontal p.text-center input.btn.btn-primary")
                ))
                search_btn.click()

                # Wait for result
                self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div#content")
                ))

                email_found = ""

                # --- Search inside General Information and other tabs ---
                tabs = self.driver.find_elements(By.CSS_SELECTOR, "ul.nav.nav-tabs li a")
                for tab in tabs:
                    tab.click()
                    time.sleep(1)

                    active_tab = self.driver.find_element(By.CSS_SELECTOR, "div.tab-content div.tab-pane.active")
                    texts = active_tab.text.split("\n")

                    for t in texts:
                        if "@" in t:   # detect email
                            email_found = t.strip()
                            break

                    if email_found:
                        break

                # Save email in DataFrame
                df.at[idx, "email"] = email_found
                print(f"✔ {license_number} → {email_found}")

            except Exception as e:
                print(f"❌ Error for license {license_number}: {e}")
                continue

        # Save updated file
        df.to_excel(self.output_file, index=False)
        self.driver.quit()
        print("✅ Scraping completed. Emails saved to:", self.output_file)


# --- Run Example ---
if __name__ == "__main__":
    input_file = r"C:\Users\jai seya ram\OneDrive\Documents\rnd project\xpresscredentialling\license.xlsx"   # yaha us file ka naam daal jha license or npi number rkhe hai 
    output_file = r"C:\users\jai seya ram\OneDrive\Documents\rnd project\with_email2.xlsx"

    scraper = FloridaEmailScraper(input_file, output_file)
    scraper.scrape_emails()


# link with new try file 
