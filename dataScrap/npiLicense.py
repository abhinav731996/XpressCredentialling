import pandas as pd
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---- CONFIG ----
input_file = r"C:\Users\jai seya ram\OneDrive\Documents\rnd project\XpressCredentialling\npi.xlsx"         # Input file path
output_file = r"C:\Users\jai seya ram\OneDrive\Documents\rnd project\XpressCredentialling\license.xlsx"    # Output file path
MAX_RETRIES = 3
DELAY_RANGE = (1.0, 2.5)         # random polite delay
THREADS = 10                      # number of concurrent threads
SAVE_INTERVAL = 50                # save every 50 NPI processed

# ---- FUNCTION TO GET LICENSE ----
def get_license_from_npi(npi_number):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            url = f"https://npiregistry.cms.hhs.gov/api/?number={npi_number}&version=2.1"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                time.sleep(random.uniform(*DELAY_RANGE))
                continue
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                licenses = data["results"][0].get("taxonomies", [])
                if licenses:
                    return licenses[0].get("license", "")
            return ""
        except Exception:
            time.sleep(random.uniform(*DELAY_RANGE))
    return ""

# ---- WRAPPER FUNCTION FOR THREAD ----
def process_npi(row):
    idx, npi = row
    npi_str = str(npi)
    license_number = get_license_from_npi(npi_str)
    time.sleep(random.uniform(*DELAY_RANGE))
    return idx, license_number

# ---- MAIN SCRIPT ----
def main():
    df = pd.read_excel(input_file, engine="openpyxl")

    if "npi_number" not in df.columns:
        raise ValueError("❌ File me 'npi_number' column hona chahiye")

    # create column if not exists
    if "license_number" not in df.columns:
        df["license_number"] = ""

    # build list of NPIs to process (skip already done)
    npi_list = [(idx, npi) for idx, npi in enumerate(df["npi_number"]) if not df.at[idx, "license_number"]]

    total = len(npi_list)
    print(f"Total NPIs to process: {total}")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(process_npi, row): row for row in npi_list}
        completed_count = 0

        for future in as_completed(futures):
            idx, license_number = future.result()
            df.at[idx, "license_number"] = license_number
            completed_count += 1
            print(f"{completed_count}/{total} → NPI: {df.at[idx,'npi_number']} -> License: {license_number}")

            # save intermediate every SAVE_INTERVAL
            if completed_count % SAVE_INTERVAL == 0:
                df.to_excel(output_file, index=False)
                print(f"💾 Progress saved at {completed_count} NPIs")

    # final save
    df.to_excel(output_file, index=False)
    print(f"\n✅ Completed! File saved at: {output_file}")


if __name__ == "__main__":
    main()