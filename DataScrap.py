import requests
from bs4 import BeautifulSoup
import re
import time
import csv
from googlesearch import search
from urllib.parse import urlparse
import urllib3

# Disable SSL warnings when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# User-Agent to avoid being blocked
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36'
}

CSV_FILE = "npi_results.csv"

# Create CSV file with headers if it doesn't exist
with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if f.tell() == 0:  # file is empty
        writer.writerow(["NPI Number", "Provider Name", "Website", "Emails"])


def get_npi_data(npi_number):
    """Fetch provider data from the NPPES NPI Registry API."""
    print(f"\n[INFO] Querying NPI Registry for NPI: {npi_number}...")
    api_url = f"https://npiregistry.cms.hhs.gov/api/?number={npi_number}&version=2.1"

    try:
        response = requests.get(api_url, timeout=15, verify=False)
        response.raise_for_status()
        data = response.json()

        if data.get('result_count', 0) > 0:
            result = data['results'][0]
            basic_info = result.get('basic', {})
            addresses = result.get('addresses', [])

            provider_name = basic_info.get('organization_name', '') or \
                            f"{basic_info.get('first_name', '')} {basic_info.get('last_name', '')}".strip()

            location = {}
            for addr in addresses:
                if addr.get('address_purpose') == 'LOCATION':
                    location['city'] = addr.get('city', '')
                    location['state'] = addr.get('state', '')
                    break

            if provider_name and location:
                print(f"[SUCCESS] Found Provider: {provider_name} in {location.get('city')}, {location.get('state')}")
                return {'name': provider_name, 'location': location}

        print(f"[WARN] No results found in NPI Registry for {npi_number}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not query NPI API for {npi_number}: {e}")
        return None
    except ValueError as e:
        print(f"[ERROR] Failed to parse JSON response for {npi_number}: {e}")
        return None


def find_provider_website(provider_name, location):
    """Uses Google search to find the most likely website for a provider."""
    query = f"{provider_name} {location.get('city')} {location.get('state')} website"
    print(f"[INFO] Searching the web for: '{query}'")

    try:
        search_results = search(query, num_results=1, lang="en", sleep_interval=1)
        first_result = next(search_results, None)

        if first_result:
            print(f"[SUCCESS] Found potential website: {first_result}")
            return first_result
        else:
            print(f"[WARN] No website found from search for {provider_name}.")
            return None
    except Exception as e:
        print(f"[ERROR] An error occurred during web search: {e}")
        print("[HINT] If you see a 429 error, you have been temporarily rate-limited.")
        return None


def fetch_with_retries(url, retries=3, delay=5):
    """Helper: retry logic for slow websites."""
    for i in range(retries):
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=30, verify=False)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            print(f"[WARN] Timeout fetching {url}, retry {i+1}/{retries}...")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed fetching {url}: {e}")
            break
    return None


def extract_contacts_from_url(url):
    """Scrapes a single URL for email addresses and keeps the full website URL."""
    if not url:
        return [], []

    print(f"[INFO] Scraping {url} for contacts...")
    response = fetch_with_retries(url)
    if not response:
        return [], []

    # Find all email addresses on the page
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_regex, response.text))

    print(f"[SUCCESS] Found {len(emails)} emails.")
    # Return full URL instead of truncating to domain
    return list(emails), [url]


def save_to_csv(npi, name, websites, emails):
    """Save results into CSV file"""
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            npi,
            name,
            websites[0] if websites else "None",
            ", ".join(emails) if emails else "None"
        ])


def process_single_npi(npi_number):
    """Orchestrates the entire process for a single NPI number."""
    provider_data = get_npi_data(npi_number)

    if not provider_data:
        print(f"\n[FAIL] No information found for NPI {npi_number}.")
        return

    website_url = find_provider_website(provider_data['name'], provider_data['location'])

    if website_url:
        emails, websites = extract_contacts_from_url(website_url)
        print_results(npi_number, provider_data['name'], websites, emails)
        save_to_csv(npi_number, provider_data['name'], websites, emails)
    else:
        print("\n[FAIL] Could not automatically find a website to scrape.")
        print_results(npi_number, provider_data['name'], websites=[], emails=[])
        save_to_csv(npi_number, provider_data['name'], [], [])


def print_results(npi, name, websites, emails):
    """Formats and prints the final results."""
    print("\n" + "="*20 + " FINAL REPORT " + "="*20)
    print(f"  NPI Number:     {npi}")
    print(f"  Provider Name:  {name}")
    print(f"  Website Found:  {websites[0] if websites else 'None'}")
    print(f"  Emails Found:   {', '.join(emails) if emails else 'None'}")
    print("="*54 + "\n")


if __name__ == "__main__":
    while True:
        user_input = input("Enter a 10-digit NPI number (or type 'q' to quit): ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("Exiting program. Goodbye!")
            break

        if len(user_input) != 10 or not user_input.isdigit():
            print("[ERROR] Invalid input. An NPI must be exactly 10 numbers.")
            continue

        process_single_npi(user_input)
