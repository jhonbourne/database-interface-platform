from flask import Blueprint, request, jsonify
from mapper.mysqlhelper import MySqlHelper

bp = Blueprint('debug',__name__)

get_database_pwd = {
    'root': 'root'
}
def authority_check():
    user_name = 'root'
    return user_name, get_database_pwd[user_name]

def get_database4src(path):
    return 'spider'

class Message(object):
    def __init__(self):
        self.success = True
        self.status = "With access authority."
        self.data = []
        self.columns = tuple()

    def get_msg(self):
        return jsonify(self.__dict__)

@bp.route('/data')
def get_tables():
    user, pwd = authority_check()
    msg = Message()
    with MySqlHelper(user=user, password=pwd,
                     database=get_database4src(request.path)) as dial:
        msg.data = [t[0] for t in dial.show_tables()]
        print(msg.get_msg())
    return msg.get_msg()

@bp.route('/data/<string:tablename>')
def get_table_data(tablename):
    user, pwd = authority_check()
    msg = Message()
    with MySqlHelper(user=user, password=pwd,
                     database=get_database4src(request.path)) as dial:
        try:
            msg.data, msg.columns = dial.select(tablename)
        except Exception as e:
            msg.success = False
            msg.status = str(e)
        print(msg.get_msg())
    return msg.get_msg()

@bp.route('/test_get',methods=['GET'])
def return_get():
    full_path = request.full_path
    query_str = full_path[(full_path.index('?')+1):]
    return jsonify({"result": query_str})

@bp.route('/test_post',methods=['POST'])
def return_post():
    param_dict = request.args.to_dict()

    body = request.get_json()
    print(body)
    return jsonify({"param":param_dict
                    ,"body":body})