STEP 1: Details of given NPIs (Recieved in Excel format) are fetched through NPPES API and stored in Separate Excel.
        Threadpool used

        Below are the columns of saved NPIS

        number	addresses	practiceLocations	taxonomies	identifiers	endpoints	other_names	basic.first_name	basic.last_name	basiccredential	basic.sole_proprietor	basic.sex	basic.enumeration_date	basic.last_updated	basic.status	basic.name_prefix	basic.name_suffix	
        basic.certification_date	basic.middle_name

STEP 2: run_parellel_scraper.py will run that divides total rows in two chunks(each chunk runs in seperate tab),
        details(license no., first and last name for primary state from "taxonomies"[list object]) is taken 
        processpool used.

STEP 3: Navigation to state website is redirected according to Primary state code [currently: FL, AZ ]

STEP 4: Validation of license number pattern for both state is managed. [FL ACCEPTS like ME1234 OR OS123, AZ accepts only number]

STEP 5: Through selenium it fetches details from the respective website and saved it in temp excel files[Data is only accepted if NPI & state names match].

STEP 6: IF details are not found through state lookup, navigation fallbacks to search api.
        Finds the link directly of the practioner profile(Currently working for FL only).

MISC: 1. Some NPIs numbers recieved are deactivated , to check use check_disabled_npi.py
      2. Temp excel are stored in temp_outputs folder
      3. UPDATE paths accordingly before running any script

FLOW: Run fetch_npi() sep or call in run_parellel_scrapper()
      state_select() --> florida_board()/arizona_board()
