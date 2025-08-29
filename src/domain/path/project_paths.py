from pathlib import Path

class PATHS:
    # npi
    npi_url = "https://npiregistry.cms.hhs.gov/api/" 

    # FL
    florida_med_board_url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

    # Arizona
    client_az_sheet_npi = r"D:\Repositories\XpressCredentialling\src\database\client_az_sheet_npi.xlsx"
    az_npi_details_api = r"D:\Repositories\XpressCredentialling\src\database\az_npi_details_api.xlsx"
    arizona_lookup_url = r"https://azbomv7prod.glsuite.us/GLSuiteWeb/Clients/AZBOM/public/WebVerificationSearch.aspx?q=azmd&t=20250816101430"

    # Log
    error_details_file = r"D:\Repositories\XpressCredentialling\src\log\error_details.txt"
    request_errors_log = r"D:\Repositories\XpressCredentialling\src\log\req_err_log.txt"
    
    # DataBase
    temp_output_dir = Path(r"D:\Repositories\XpressCredentialling\src\database\temp_outputs")

path_obj = PATHS()

