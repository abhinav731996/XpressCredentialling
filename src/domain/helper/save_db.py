import sqlite3, time
from src.domain.path.project_paths import path_obj


class DBSAVE:
    def __init__(self):
        self.db_path = path_obj.combined_chunks_file.replace(".xlsx", ".db")

    def realtime_save_in_db(self,df):
        
        # retry logic for SQLite lock
        for attempt in range(3):
            try:
                with sqlite3.connect(self.db_path, timeout=30) as conn:
                    df.to_sql("npi_data", conn, if_exists="append", index=False)
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    time.sleep(1)
                else:
                    raise   

save_db_obj = DBSAVE()