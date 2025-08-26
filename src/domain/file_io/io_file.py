import sys,os
sys.path.append(os.getcwd())
from src.domain.path.project_paths import path_obj
import pandas as pd
from abc import ABC, abstractmethod
import os
import logging
from pythonjsonlogger import jsonlogger

class FILEIO(ABC):
    
    @abstractmethod
    def write_file(self,*args,**kwargs):
        pass

class ERRORIO(FILEIO):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("error_logger")
        self.logger.setLevel(logging.ERROR)

        if not self.logger.hasHandlers():
            handler = logging.FileHandler(path_obj.error_details_file, mode="a")
            formatter = jsonlogger.JsonFormatter(
                fmt="%(module)s %(funcName)s %(message)s %(asctime)s %(lineno)d %(levelname)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def write_file(self, error: Exception):
        self.logger.error(error, stacklevel=2)


class REQUESTIO(FILEIO):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.ERROR)

        if not self.logger.hasHandlers():
            handler = logging.FileHandler(path_obj.request_errors_log, mode="a")
            formatter = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(levelname)s %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def write_file(self, message: str):
        self.logger.error(message, stacklevel=2)

      
error_io_obj = ERRORIO()
