from flask import Blueprint, request, jsonify
from .services.word_statistic import WordStatistic
from .services.get_menu import get_menu

bp = Blueprint('debug',__name__)


class Message(object):
    def __init__(self):
        self.success = True
        self.status = "With access authority."
        self.data = []
        self.columns = tuple()

    def get_msg(self):
        return jsonify(self.__dict__)

@bp.route('/data')
def get_menu_options():
    msg = Message()
    msg.data = get_menu(request.path)
    print(msg.get_msg())
    return msg.get_msg()

@bp.route('/data/<string:tablename>')
def get_table_data(tablename):
    msg = Message()
    try:
        ws = WordStatistic(name=tablename, path=request.path)
        ws.word_cut()
        tmp_data = ws.word_count()
        msg.data = [{'name':k,'value': v} for k, v in tmp_data.items()]
        msg.columns = ('word_freq',)
    except Exception as e:
        msg.success = False
        msg.status = str(e)    
    
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