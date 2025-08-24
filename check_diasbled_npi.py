import pandas as pd

my_sheet = r"D:\Repositories\XpressCredentialling\src\database\npi_data.xlsx"
client_sheet = r"D:\Repositories\XpressCredentialling\src\database\XpressCred_DataSample.xlsx"

df_fetch = pd.read_excel(my_sheet)
df_client = pd.read_excel(client_sheet)

df_fetch.columns = df_fetch.columns.str.strip()
df_client.columns = df_client.columns.str.strip()

npi_fetch_set = set(df_fetch['number'].dropna().astype(str).str.strip())
npi_client_set = set(df_client['National Provider Identifier'].dropna().astype(str).str.strip())

only_in_fetch = npi_fetch_set - npi_client_set
only_in_client = npi_client_set - npi_fetch_set
in_both = npi_fetch_set & npi_client_set

print(f"Total in my_sheet: {len(npi_fetch_set)}")
print(f"Total in client_sheet: {len(npi_client_set)}")
print(f"Common NPIs: {len(in_both)}")
print(f"NPIs only in my_sheet : {only_in_fetch}")
print(f"NPIs only in client_sheet : {only_in_client}")
