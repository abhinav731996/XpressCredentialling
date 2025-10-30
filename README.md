## UPDATE PATHS BEFORE RUNNING SCRIPTS
1. path_obj.all_states_surgery_npi_test
2. path_obj.all_states_surgery_npi_result
3. path_obj.combined_chunks_file


## FLOW: 
main.py -> fetch_npi(domain->get_npi) -> create_instance(domain->scraper) -> export_final_excel(domain->scraper)
-> enter_info(domain->search_board->main_select->state_select) ->After this routed to respective website(seach_board)  -> data fetched & saved in Sqlite DB(realtime_save_in_db()).     

## STEPS
STEP 1: Details of given NPIs (Recieved in Excel format) are fetched through NPPES API and stored in Separate Excel.
        Threadpool used

        Below are the columns of saved NPIS

        number	addresses	practiceLocations	taxonomies	identifiers	endpoints	other_names	basic.first_name	basic.last_name	basiccredential	basic.sole_proprietor	basic.sex	basic.enumeration_date	basic.last_updated	basic.status	basic.name_prefix	basic.name_suffix	
        basic.certification_date	basic.middle_name

STEP 2: run_parellel_scraper.py will run that divides total rows in two chunks(each chunk runs in seperate tab),
        details(license no., first and last name for primary state from "taxonomies"[list object]) is taken 
        processpool used.

STEP 3: Navigation to state website is redirected according to Primary state code [currently: FL, MN - Except previous two states all states are routed to Surgery Website.]

STEP 4: Validation of license number pattern for both state is managed. [FL ACCEPTS like ME1234 OR OS123, MN accepts only number, and Surgery (as of now)only takes names]

STEP 5: Through selenium it fetches details from the respective website and saved it in SQlite DB file and saves for each NPI and at last it is converted to Excel.

# this step is disabled for now 
STEP 6: IF details are not found through state lookup, navigation fallbacks to search api.
        Finds the link directly of the practioner profile(Currently working for FL only).

MISC: 1. Some NPIs numbers recieved are deactivated , to check use check_disabled_npi.py (src->domain->helper).
      2. DB file and Final are in (src->database->temp_outputs).
      3. UPDATE PATHS accordingly before running any script.

