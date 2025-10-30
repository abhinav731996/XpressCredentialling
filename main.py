import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support() 

    from src.domain.get_npi.fetch_npi import NPI_API
    from src.domain.scraper.run_parallel_scraper import SCRAPPER

    NPI_API().api_fetch()

    scraper_obj = SCRAPPER()
    scraper_obj.create_instances()

    scraper_obj.export_final_excel()
