from repositories.database_info import *
from utils.mysqlhelper import MySqlHelper

def get_menu(path):
    user, pwd = authority_check()
    with MySqlHelper(user=user, password=pwd,
                        database=get_database4src(path)) as dial:
        return [t[0] for t in dial.show_tables()]