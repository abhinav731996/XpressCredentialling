import sys, os, traceback, logging
sys.path.append(os.getcwd())
from pythonjsonlogger import jsonlogger
from src.domain.path.project_paths import path_obj
from abc import ABC, abstractmethod


class FILEIO(ABC):
    @abstractmethod
    def write_file(self, *args, **kwargs):
        pass


class ERRORIO(FILEIO):
    _seen_errors = set()  # track already logged messages

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
        try:
            # Handle both Exception objects and raw strings
            if isinstance(error, Exception):
                msg = f"{type(error).__name__}: {str(error)[:300]}"  # trim long messages
                tb_lines = traceback.format_tb(error.__traceback__)
                short_tb = "".join(tb_lines[-2:])
            else:
                msg = str(error)[:300]  # limit string length
                short_tb = ""

            # Avoid duplicates
            if msg not in self._seen_errors:
                simple_msg = f"{msg} | Traceback(last 2 lines): {short_tb.strip()}"
                self.logger.error(simple_msg, stacklevel=2)
                self._seen_errors.add(msg)

        except Exception as log_err:
            print(f"Logging error failed: {log_err}")


class REQUESTIO(FILEIO):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.ERROR)

        if not self.logger.hasHandlers():
            handler = logging.FileHandler(path_obj.request_errors_log, mode="a")
            formatter = jsonlogger.JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def write_file(self, message: str):
        self.logger.error(message[:300], stacklevel=2)  # also trimmed


error_io_obj = ERRORIO()
