from flask import Blueprint, request, jsonify

bp = Blueprint('debug',__name__)


@bp.route('/test_get',methods=['GET'])
def return_get():
    full_path = request.full_path
    query_str = full_path[(full_path.index('?')+1):]
    return jsonify({"result": query_str})

@bp.route('/test_post',methods=['POST'])
def return_post():
    full_path = request.full_path
    param_str = full_path[(full_path.index('?')+1):]

    body = request.get_json()
    print(body)
    return jsonify({"param":param_str
                    ,"body":body})