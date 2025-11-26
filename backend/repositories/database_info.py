
get_database_pwd = {
    'root': 'root'
}
def authority_check():
    user_name = 'root'
    return user_name, get_database_pwd[user_name]

def get_database4accounts():
    return 'user'
tabel4log = 'accounts'
columns4log = {
    'username': 'username',
    'password': 'password',
    'id': 'id'
}

def get_database4src(path):
    return 'spider'

columns4wordstatistic = {
    'baidutopsearch': ('title','abstract'),
    'doubantopmovies': ('info','title_CN')
}

def get_word_statistic_columns(name):
    use_key = None
    for col in columns4wordstatistic.keys():
        if name.startswith(col): # refer to table names created by spiders
            use_key = col
            break
    return columns4wordstatistic.get(use_key, ('*',))