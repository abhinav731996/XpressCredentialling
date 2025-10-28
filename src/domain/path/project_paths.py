from pathlib import Path

class PATHS:
    # Main Sheets
    all_states_surgery_npi_test = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\all_states_surgery_npi_test.xlsx"
    all_states_surgery_npi_result = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\all_states_surgery_npi_result.xlsx"
    combined_chunks_file = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\combined_chunks_file.xlsx"
    
    # Nppes api
    npi_url = "https://npiregistry.cms.hhs.gov/api/" 

    # Minnesota
    minnesota_med_board_url = "https://bmp.hlb.state.mn.us/#/onlineEntitySearch"

    # Florida
    florida_med_board_url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

    # Arizona
    arizona_lookup_url = r"https://azbomv7prod.glsuite.us/GLSuiteWeb/Clients/AZBOM/public/WebVerificationSearch.aspx?q=azmd&t=20250816101430"

    # Log
    error_details_file = r"D:\Repositories\XpressCredentialling\src\log\error_details.txt"
    request_errors_log = r"D:\Repositories\XpressCredentialling\src\log\req_err_log.txt"
    
    # DataBase
    temp_output_dir = Path(r"D:\Repositories\XpressCredentialling\src\database\temp_outputs")

    # all states of "surgery" speciality
    american_board_surgeon = "https://www.facs.org/find-a-surgeon/"

path_obj = PATHS()

