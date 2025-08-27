import pandas as pd
import requests
import time
import re
from googlesearch import search
import urllib3
import random
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.124 Safari/537.36'
}


def get_npi_data(npi_number):
    api_url = f"https://npiregistry.cms.hhs.gov/api/?number={npi_number}&version=2.1"
    try:
        response = requests.get(api_url, timeout=15, verify=False)
        response.raise_for_status()
        data = response.json()
        if data.get('result_count', 0) > 0:
            result = data['results'][0]
            basic_info = result.get('basic', {})
            addresses = result.get('addresses', [])
            taxonomies = result.get('taxonomies', [])

            # Provider Name
            provider_name = basic_info.get('organization_name', '') or \
                f"{basic_info.get('first_name', '')} {basic_info.get('last_name', '')}".strip()

            # Address
            location = {}
            full_address = ""
            phone, fax = "", ""
            for addr in addresses:
                if addr.get('address_purpose') == 'LOCATION':
                    location['city'] = addr.get('city', '')
                    location['state'] = addr.get('state', '')
                    phone = addr.get('telephone_number', '')
                    fax = addr.get('fax_number', '')
                    full_address = f"{addr.get('address_1', '')}, {addr.get('city', '')}, " \
                                   f"{addr.get('state', '')} {addr.get('postal_code', '')}"
                    break

            # License(s)
            licenses = []
            for t in taxonomies:
                if t.get('license'):
                    licenses.append(t['license'])

            return {
                'name': provider_name,
                'location': location,
                'phone': phone,
                'fax': fax,
                'address': full_address,
                'licenses': ", ".join(licenses) if licenses else None,
                'institution': basic_info.get('organization_name', None) or None
            }
        else:
            return None
    except Exception as e:
        print(f"[ERROR] NPI API: {e}")
        return None


def find_provider_website(name, location, max_retries=5, base_backoff=1, max_backoff=60):
    query = f"{name} {location.get('city', '')} {location.get('state', '')} website"
    retries = 0
    while retries < max_retries:
        try:
            for url in search(query, num_results=1, lang='en', sleep_interval=random.uniform(5, 10)):
                return url
            return None
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    backoff_time = min(max_backoff, base_backoff * 2 ** retries)
                    wait_time = random.uniform(0, backoff_time)
                print(f"[WARN] Hit 429 rate limit. Backing off for {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                print(f"[ERROR] Google Search: {e}")
                return None
        except Exception as e:
            print(f"[ERROR] Google Search: {e}")
            return None
    print("[FAIL] Max retries reached. Could not get website due to rate limiting.")
    return None


def fetch_with_retries(url, retries=3, delay=5):
    for i in range(retries):
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=30, verify=False)
            response.raise_for_status()
            return response
        except:
            time.sleep(delay)
    return None


def extract_emails_from_page(html):
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_regex, html))
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        if href.startswith('mailto:'):
            email = a['href'][7:].split('?')[0]
            emails.add(email)
    return emails


def extract_contacts_from_url(url):
    if not url:
        return []
    pages_to_check = [url]
    common_paths = ['/contact', '/contact-us', '/about', '/about-us', '/contacts']

    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    for path in common_paths:
        pages_to_check.append(urljoin(base_url, path))

    all_emails = set()

    for page_url in pages_to_check:
        response = fetch_with_retries(page_url)
        if response:
            emails = extract_emails_from_page(response.text)
            if emails:
                print(f"[INFO] Found {len(emails)} emails on {page_url}")
            all_emails.update(emails)

    return list(all_emails)


def save_progress(data_rows, output_path):
    df_progress = pd.DataFrame(
        data_rows,
        columns=[
            'NPI Number',
            'Provider Name',
            'Website',
            'Emails',
            'Phone',
            'Fax',
            'License Number',
            'Address',
            'Institution Name',
            'University/School',
            'Program Name'
        ]
    )
    df_progress.to_excel(output_path, index=False)
    print(f"\n[INFO] Progress saved to {output_path}")


def main(input_path, output_path):
    df = pd.read_excel(input_path)
    if 'National Provider Identifier' not in df.columns:
        print("Error: Your input excel must have a column titled 'National Provider Identifier'.")
        return

    out_rows = []
    try:
        for idx, row in df.iterrows():
            npi_number = str(row['National Provider Identifier']).strip()
            print(f"Processing NPI: {npi_number} ({idx+1}/{len(df)})")
            pdata = get_npi_data(npi_number)
            if not pdata:
                out_rows.append([npi_number, None, None, None, None, None, None, None, None, None, None])
            else:
                website = find_provider_website(pdata['name'], pdata['location'])
                emails = extract_contacts_from_url(website) if website else []
                out_rows.append([
                    npi_number,
                    pdata['name'],
                    website if website else None,
                    ', '.join(emails) if emails else None,
                    pdata['phone'],
                    pdata['fax'],
                    pdata['licenses'],
                    pdata['address'],
                    pdata['institution'],
                    None,  # University (not available in API)
                    None   # Program Name (not available in API)
                ])
            sleep_time = random.uniform(10, 20)
            print(f"Sleeping for {sleep_time:.2f} seconds before next request...")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[INFO] Process interrupted by user. Saving progress...")
        save_progress(out_rows, output_path)
        sys.exit(0)

    save_progress(out_rows, output_path)
    print("[INFO] All done.")


if __name__ == "__main__":
    input_path = 'XpressCred_DataSample.xlsx'  # <-- Input file
    output_path = "F:/WebScrapping/XpressCredentialling/Job export/Phone_npi_result.xlsx"
    main(input_path, output_path)
