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

    # all states of "surgery" speciality
    american_board_surgeon = "https://www.facs.org/find-a-surgeon/"
    surgery_test_npi = r"D:\Repositories\XpressCredentialling\src\database\npi_test_surgery.xlsx" 

    # 24 Test
    all_states_surgery_npi_test = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\all_states_surgery_npi_test.xlsx"
    all_states_surgery_npi_result = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\all_states_surgery_npi_result.xlsx"


    # data saving test
    client_data = r"D:\Repositories\XpressCredentialling\src\database\client_data.xlsx"
    client_data_result = r"D:\Repositories\XpressCredentialling\src\database\client_data_result.xlsx"
    combined_chunks_file = r"D:\Repositories\XpressCredentialling\src\database\temp_outputs\combined_chunks_file.xlsx"
path_obj = PATHS()

