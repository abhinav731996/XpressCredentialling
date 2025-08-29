from src.domain.scraper.run_parallel_scraper import SCRAPPER
from src.domain.get_npi.fetch_npi import NPI_API


NPI_API().api_fetch() # first, details for client npi are fetched
scraper_obj = SCRAPPER()
scraper_obj.create_instances()  # second, details are navigated to respective state board lookups
scraper_obj.merge_outputs() 