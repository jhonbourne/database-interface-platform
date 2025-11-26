from flask import session
from repositories import user_info

def deal_regist_user(account_info):
    try:
        user_info.add_user(account_info['username'], account_info['password'])
        return {"status": "Registration successful"}, True
    except Exception as e:
        return {"error": str(e)}, False
    
def deal_login(account_info):
    try:
        user = user_info.verify_user(account_info['username'], account_info['password'])
        if user:
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['username']
            return {"status": "Login successful"}, True
        else:
            return {"error": "Invalid username or password"}, False
    except Exception as e:
        return {"error": str(e)}, False
    
def deal_logout():
    session.clear()
    return {"status": "Logout successful"}, True

def check_user_by_id(user_id):
    try:
        user = user_info.get_user_by_id(user_id)
        if not user:
            user = None
        return user
    except Exception as e:
        return None