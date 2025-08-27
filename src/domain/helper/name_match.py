import re

class NAMEMATCH:
    def __init__(self):
        pass

    def normalize_name(self,name):
        name = name.lower()
        name = re.sub(r'[^\w\s]', '', name)
        return name.split()

    def is_name_match(self, first_name, last_name, site_name, require_all=False):
        site_name_parts = self.normalize_name(site_name)
        npi_name_parts = self.normalize_name(f"{first_name} {last_name}")
        
        if require_all:
            return all(part in site_name_parts for part in npi_name_parts) # strict check
        else:
            return any(part in site_name_parts for part in npi_name_parts) # loose check


name_match_obj = NAMEMATCH()
