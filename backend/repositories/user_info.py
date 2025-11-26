from utils.mysqlhelper import MySqlHelper
from .database_info import authority_check, get_database4accounts, tabel4log, columns4log
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
# To simplify context management, define a decorator for database operations
# TODO?: Hand over the context management to Flask or ORM
def with_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db_name = get_database4accounts()
        sql_name, sql_pwd = authority_check()
        with MySqlHelper(user=sql_name, password=sql_pwd, 
                         database=db_name) as conn:
            return func(conn, *args, **kwargs)
    return wrapper

@with_db_connection
def add_user(conn, username, password):
    hashed_password = generate_password_hash(password)

    columns_in_sql = [columns4log[nam] for nam in ('username', 'password')]
    try:
        # insert user registration info into database table
        conn.append(tabel4log, column_names=columns_in_sql,
                values = (username, hashed_password) )
    except Exception as e:
        if 'Duplicate entry' in str(e):
            raise Exception("Username already exists.")
        else:
            raise Exception(f"Failed to add user: {str(e)}")
            
@with_db_connection
def verify_user(conn, username, password):
    columns_in_sql = [columns4log[nam] for nam in ('username', 'password', 'id')]
    try:
        # select user by username (parameterized)
        user_info, column_names = conn.select(
            tabel4log,
            column_names=columns_in_sql,
            where=f"{columns4log['username']}=%s",
            where_params=(username,)
        )

        print(user_info)

        if not user_info:
            raise Exception("User not found.")

        # get the first (and expected only) row
        first_row = user_info[0]

        # find password column index and check hash against the value in the row
        pwd_idx = column_names.index(columns4log['password'])
        if not check_password_hash(first_row[pwd_idx], password):
            raise Exception("Incorrect password.")

        return {
            'id': first_row[column_names.index(columns4log['id'])],
            'username': first_row[column_names.index(columns4log['username'])]
        }
    except Exception as e:
        raise Exception(f"Failed to verify user: {str(e)}")
        
@with_db_connection
def get_user_by_id(conn, user_id):
    user_info, column_names = conn.select(tabel4log, 
                                    where=f"{columns4log['id']}={user_id}")
    return user_info
        
def code_db_name_trans():
    # TODO: (replace 'column_names') convert variables names in code to database column names
    # return dict: code variable name -> column index of 'user_info'
    pass