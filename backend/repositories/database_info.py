
get_database_pwd = {
    'root': 'root'
}
def authority_check():
    user_name = 'root'
    return user_name, get_database_pwd[user_name]

def get_database4src(path):
    return 'spider'

columns4use = {
    'baidutopsearch': ('title','abstract'),
    'doubantopmovies': ('info','title_CN')
}

def get_word_statistic_columns(name):
    use_key = None
    for col in columns4use.keys():
        if name.startswith(col):
            use_key = col
            break
    return columns4use.get(use_key, ('*',))