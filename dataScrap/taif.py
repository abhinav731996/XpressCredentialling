import requests
import pandas as pd
import string
import time


def search_npi(state=None, last_name=None, taxonomy=None, limit=200):
    """
    Query NPI Registry API with filters.
    """
    url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "limit": limit
    }

    if state:
        params["state"] = state
    if last_name:
        params["last_name"] = last_name
    if taxonomy:
        params["taxonomy_description"] = taxonomy

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"API request failed: {response.status_code}")
        return []

    data = response.json()
    return data.get("results", [])


def display_and_save(results, filename="npi_state.csv"):
    """
    Save API results to CSV and print summary.
    """
    data_list = []

    for r in results:
        basic = r.get("basic", {})
        addresses = r.get("addresses", [{}])
        addr = addresses[0] if addresses else {}

        row = {
            "NPI": r.get("number"),
            "Name": f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip(),
            "Org Name": basic.get("organization_name", ""),
            "Gender": basic.get("gender", ""),
            "Credential": basic.get("credential", ""),
            "Enumeration Date": basic.get("enumeration_date", ""),
            "Address": f"{addr.get('address_1', '')}, {addr.get('city', '')}, {addr.get('state', '')}, {addr.get('postal_code', '')}",
            "Phone": addr.get("telephone_number", ""),
            "Fax": addr.get("fax_number", "")
        }
        data_list.append(row)

    df = pd.DataFrame(data_list)
    df.to_csv(filename, index=False)
    print(f"\n✅ Results saved to {filename} (Total {len(df)} records)")
    print(df.head())


def scrape_state(state_code, taxonomy=None):
    """
    Scrape all NPIs from a state by looping through A–Z last names.
    """
    all_results = []

    for letter in string.ascii_uppercase:
        print(f"🔎 Fetching NPI data for {state_code}, Last Name starts with '{letter}'...")
        results = search_npi(state=state_code, last_name=letter, taxonomy=taxonomy, limit=200)

        if results:
            all_results.extend(results)
            print(f"   📊 Found {len(results)} records for '{letter}'")
        else:
            print(f"   ❌ No results for '{letter}'")

        # prevent hammering the API
        time.sleep(1)

    # Save final combined results
    if all_results:
        filename = f"npi_{state_code}.csv"
        display_and_save(all_results, filename)
    else:
        print(f"⚠️ No records found for {state_code}!")


# === MAIN ===
if __name__ == "__main__":
    state_code = input("Enter State Code (e.g., FL, NY, CA): ").strip().upper()
    taxonomy = input("Enter Taxonomy (optional, e.g., Internal Medicine): ").strip()

    taxonomy = taxonomy if taxonomy else None
    scrape_state(state_code, taxonomy)
