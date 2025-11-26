from flask import Flask, Blueprint, request, session, g
from .messageformat import Message
from ..services import user_service

bp = Blueprint('user', __name__, url_prefix='/user')

account_attrs = ('username', 'password')

def get_status_code(status, is_success):
    if status == "Registration successful":
        return 201
    elif status == "Login successful":
        return 200
    elif status == "Logout successful":
        return 200
    elif "Username and password are required" in status:
        return 400
    elif "Invalid username or password" in status:
        return 403
    elif "Access denied. Please log in first." in status:
        return 401
    elif "Username already exists" in status:
        return 402
    elif is_success is False:
        return 406
    else:
        return 200

def deal_service_info(message, is_success):
    print(f"Service info: {message}, Success: {is_success}")
    msg = Message()
    msg.success = is_success
    if not is_success:
        msg.status = message.get("error", "")
        status_code = get_status_code(message.get("error", ""), is_success)
    else:
        msg.status = message.get("status", "")
        status_code = get_status_code(message.get("status", ""), is_success)
    msg.status_code = status_code
    return msg.get_msg(), status_code

# Define custom exception, convienient for raising errors in anywhere
class UserException(Exception):
    def __init__(self, mesage):
        super().__init__(mesage)
        self.formatted_mesage = {"error": mesage}
# # IMPORTANT: Handle UserException globally (@app)
# @app.errorhandler(UserException)
# def handle_user_exception(error):
#     print(f"UserException: {error.formatted_mesage}")
#     return deal_service_info(error.formatted_mesage, False)

# Deal with account info from request
def get_account_info():
    data = request.get_json()
    account_info = {}
    for attr in account_attrs:
        try:
            account_info[attr] = data.get(attr)
        except KeyError:            
            raise UserException("Username and password are required")

    return account_info


@bp.route('/register', methods=['POST'])
def register():
    account_info = get_account_info()
    msg, success = user_service.deal_regist_user(account_info)

    return deal_service_info(msg, success)

@bp.route('/login', methods=['POST'])
def login():
    account_info = get_account_info()
    msg, success = user_service.deal_login(account_info)

    return deal_service_info(msg, success)

@bp.route('/logout')
def logout():
    msg, success = user_service.deal_logout()

    return deal_service_info(msg, success)

@bp.before_app_request
def get_logged_info():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_service.check_user_by_id(user_id)

# Define a decorator to check whether user is logged in before accessing certain views
def check_login(view):
    from functools import wraps

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            raise UserException("Access denied. Please log in first.")
        return view(**kwargs)

    return wrapped_view