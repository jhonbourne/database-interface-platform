import requests
from backend.utils.mysqlhelper import MySqlHelper

class Settings(object):
    HEADERS = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'

    }

    LOGNAME = ''

class SpiderRequest(object):
    def __init__(self, url, method, **kwargs):
        self.url = url
        self.method = method
        self.kwargs = kwargs

    def put_request(self):
        if self.method == 'get':
            res =  requests.get(url=self.url, params=self.kwargs, headers=Settings.HEADERS)
        elif self.method == 'post':
            res =  requests.post(url=self.url, data=self.kwargs, headers=Settings.HEADERS)
        else:
            raise ValueError("Please use valid name of request method.")
        
        res.encoding = 'utf-8'
        return res

    @classmethod
    def Put_Request(cls, url, method, headers=Settings.HEADERS, **kwargs):
        if method == 'get':
            res =  requests.get(url=url, params=kwargs, headers=headers)
        elif method == 'post':
            res =  requests.post(url=url, data=kwargs, headers=headers)
        else:
            raise ValueError("Please use valid name of request method.")
        
        res.encoding = 'utf-8'
        return res

class SqlPipeline(object):
    def __init__(self, host='localhost', port=3306, user='root', password='root', database='spider'):
        self.dial = MySqlHelper(user=user, password=password, host=host, port=port)
        self.dial.create_database(database)
        self.dial.use_database(database)

    def create_table(self, table_name, column_names=None,
                     type_list=None, column_setting=None, **kwargs):
        """Create a table in the database.
        
        Args:
            table_name: str
                The name of the table to be created.
            column_names: list of str
                Not used when 'column_setting' is a dict, of which the keys would be
                regarded as the names of columns.
            type_list: list of (str or type class)
                Each element should correspond to the columns of the table. Elements 
                could be str (written as MySQL command) or python data type (will be
                converted to the corresponding data type command in MySQL). Please 
                refer to MySqlHelper.create_table and MySqlHelper.Type_Transform
            column_setting: (list of str) or dict
                Each element should correspond to the columns of the table. Elements 
                could be a full command of data type description of one column (should
                be written in SQL gramma) or appeding description after a MySQL data 
                type of one column. Please refer to MySqlHelper.create_table and 
                MySqlHelper.Type_Transform
            **kwargs:
                Other key and values available in MySqlHelper.create_table
        """
        if isinstance(column_setting, dict):
            # 'column_setting' should be list-like in 'Type_Transform'
            column_names = list(column_setting.keys())
            column_setting = list(column_setting.values())
        else:
            if not column_names:
                raise ValueError("Names of the table columns are needed.")
            
        if (not type_list) and (not column_setting):
            raise ValueError("Requires more input about data types.")
        elif type_list != None:
            column_setting = MySqlHelper.Type_Transform(type_list, column_setting)

        # Transform column information to a dict
        settings = {}
        for i in range(len(column_names)):
            settings[column_names[i]] = column_setting[i]
        self.dial.create_table(table_name, settings, **kwargs)

    def write_data(self, table_name, column_names, values):
        """Write data to a specific table. If the table is not exist,
          it will be created according to the type of data to be written."""
        tbls = self.dial.show_tables()
        if not (table_name.lower() in [t[0] for t in tbls]): # lower case: MySQL charater
            self.create_table(table_name, map(type, values[0]))
        
        self.dial.append(table_name, column_names=column_names, values=values)        

    def __del__(self):
        self.dial.close()

if __name__ == '__main__':
    # Something to test
    pass