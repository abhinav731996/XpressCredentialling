from pathlib import Path

class PATHS:
    error_details_file = r"D:\Repositories\XpressCredentialling\src\log\error_details.txt"
    
    npi_url = "https://npiregistry.cms.hhs.gov/api/" 
    npi_excel_file = r"D:\Repositories\XpressCredentialling\src\database\npi_data.xlsx"    

    xpress_input = r"D:\Repositories\XpressCredentialling\src\database\XpressCred_DataSample.xlsx"
    florida_med_board_url = "https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders"

    temp_output_dir = Path("temp_outputs")
    email_sheet = r"D:\Repositories\XpressCredentialling\src\database\email_sheet.xlsx"

    #test 
    improperstate_email_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_email_sheet_improperstate.xlsx"
    improperstate_npi_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_npi_improperstate.xlsx"
    
    normalstate_email_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_email_sheet.xlsx"
    normalstate_npi_ex_sheet = r"D:\Repositories\XpressCredentialling\src\database\test\test_npi.xlsx"

path_obj = PATHS()

