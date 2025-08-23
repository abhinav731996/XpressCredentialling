from src.domain.path.project_paths import path_obj
import pandas as pd
from abc import ABC, abstractmethod
import datetime,traceback,json,os

class FILEIO(ABC):
    
    @abstractmethod
    def write_file(self,*args,**kwargs):
        pass


class ERRORIO(FILEIO):
    def __init__(self):
        super().__init__()

    def write_file(self,file_data,path,mode="a"):
        with open(path,mode) as file:
            data = f"\n{file_data}" # error data - json
            file.write(data)  

    def get_errdetails(self,error):
        date = datetime.datetime.now()
        str_date = date.strftime("%Y-%m-%d %H:%M:%S")

        tb = traceback.extract_tb(error.__traceback__)[-1]
        module_name = os.path.basename(tb.filename)
        function_name = tb.name
        line_no = tb.lineno

        err_details = json.dumps({"module":module_name,"function":function_name,"error":str(error),"date":str_date,"line":line_no})
        return err_details  
        

class EXCELIO(FILEIO):
    def __init__(self):
        super().__init__()
    
    def write_file(self, sheet_name, df):
        with pd.ExcelWriter(path_obj.test_result, mode='w', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
file_io_obj = EXCELIO()
