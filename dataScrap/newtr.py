import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

API_URL = 'https://npiregistry.cms.hhs.gov/api/'

def fetch_providers_by_state(state, limit=100, batch=50):
    providers = []
    skip = 0
    while len(providers) < limit:
        params = {'version': '2.1', 'state': state, 'limit': batch, 'skip': skip}
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        res = resp.json().get('results', [])
        if not res:
            break
        providers.extend(res)
        skip += batch
        time.sleep(0.5)  # gentle rate limit
    return providers

def parse_provider(p):
    addr = p.get('addresses', [{}])[0]
    return {
        'npi': p.get('number'),
        'name': p.get('basic', {}).get('name'),
        'address': addr.get('address_1', ''),
        'city': addr.get('city', ''),
        'state': addr.get('state', ''),
        'postal_code': addr.get('postal_code', ''),
        'occupation': p.get('taxonomies', [{}])[0].get('desc', '')
    }

def lookup_license(license_no):
    url = f'https://example.com/?license={license_no}'
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    return {
        'email': soup.find('a', href=lambda h: h and 'mailto:' in h).text.strip() if soup.find('a', href=lambda h: h and 'mailto:' in h) else '',
        'phone': soup.find('span', class_='phone').text.strip() if soup.find('span', class_='phone') else '',
        'fax': soup.find('span', class_='fax').text.strip() if soup.find('span', class_='fax') else '',
        'address_full': soup.find('div', class_='address').text.strip() if soup.find('div', class_='address') else ''
    }

def main(states, per_state=100):
    records = []
    for st in states:
        print(f"Fetching providers in {st}...")
        provs = fetch_providers_by_state(st, limit=per_state)
        for p in provs:
            rec = parse_provider(p)
            rec.update(lookup_license(rec['npi']))
            records.append(rec)
            time.sleep(1)
    df = pd.DataFrame(records)
    df.to_excel('providers_by_state.xlsx', index=False)
    print("Saved to Excel.")

if __name__ == '__main__':
    main(['CA', 'NY', 'TX'], per_state=200)

