
import requests
import pandas as pd


def search_npi(first_name=None, last_name=None, organization_name=None, taxonomy=None, limit=10):
    url = "https://npiregistry.cms.hhs.gov/api/"
    params = {
        "version": "2.1",
        "limit": limit
    }

    if first_name:
        params["first_name"] = first_name
    if last_name:
        params["last_name"] = last_name
    if organization_name:
        params["organization_name"] = organization_name
    if taxonomy:
        params["taxonomy_description"] = taxonomy

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("API request failed!")
        return []

    data = response.json()
    return data.get("results", [])

def display_and_save(results, filename="npi_results.csv"):
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
            "Address": f"{addr.get('address_1', '')}, {addr.get('city', '')}, {addr.get('state', '')}, {addr.get('postal_code', '')}"
        }
        data_list.append(row)

    df = pd.DataFrame(data_list)
    df.to_csv(filename, index=False)
    print(f"\n Results saved to {filename}")
    print(df)


if __name__ == "__main__":
    print("=== NPI Search Tool ===")
    fname = input("Enter First Name (or press Enter to skip): ").strip()
    lname = input("Enter Last Name (or press Enter to skip): ").strip()
    org = input("Enter Organization Name (or press Enter to skip): ").strip()
    taxonomy = input("Enter Taxonomy Description (or press Enter to skip): ").strip()
    limit = input("How many results do you want? (default=50): ").strip()

    limit = int(limit) if limit.isdigit() else 50

    results = search_npi(first_name=fname, last_name=lname, organization_name=org, taxonomy=taxonomy, limit=limit)
    
    if results:
        display_and_save(results)
    else:
        print(" No results found.")


