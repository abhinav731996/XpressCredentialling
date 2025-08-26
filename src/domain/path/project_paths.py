from pathlib import Path

class PATHS:
    error_details_file = r"D:\Repositories\XpressCredentialling\src\log\error_details.txt"
    
    license_for_cms = r"D:\Repositories\XpressCredentialling\src\database\license_for_client_npi.xlsx"

    request_errors_log = r"D:\Repositories\XpressCredentialling\src\log\req_err_log.txt"
    npi_url = "https://npiregistry.cms.hhs.gov/api/" 
    npi_excel_file = r"D:\Repositories\XpressCredentialling\src\database\npi_data.xlsx"    

    xpress_input = r"D:\Repositories\XpressCredentialling\src\database\XpressCred_DataSample.xlsx"
    florida_med_board_url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

    temp_output_dir = Path("temp_outputs")
    email_sheet = r"D:\Repositories\XpressCredentialling\src\database\email_sheet.xlsx"

    # Arizona
    arizona_input_famprac = r"D:\Repositories\XpressCredentialling\src\database\arizona_famprac.xlsx"
    arizona_npi_license = r"D:\Repositories\XpressCredentialling\src\database\arizona_npi_license.xlsx"
    arizona_lookup_url = r"https://azbomv7prod.glsuite.us/GLSuiteWeb/Clients/AZBOM/public/WebVerificationSearch.aspx?q=azmd&t=20250816101430"
    arizona_test_npi = r"D:\Repositories\XpressCredentialling\src\database\test\arizona_test\rename_test_npi.xlsx"
    #test 
    improperstate_email_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_email_sheet_improperstate.xlsx"
    improperstate_npi_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_npi_improperstate.xlsx"
    
    normalstate_email_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_email_sheet.xlsx"
    normalstate_npi_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_npi.xlsx"

path_obj = PATHS()

