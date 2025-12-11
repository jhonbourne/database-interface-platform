from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from .messageformat import Message
from .user import check_login
from ..services.digit_classify import classify_digit_in_image

bp = Blueprint('figure', __name__, url_prefix='/recognition')

# Don't restrict 'method' param, in order to trigger @check_login
@bp.route('/digit', methods=['GET','POST'])
@check_login
def get_handwrite_number():
    msg = Message()
    if request.method == 'POST':
        print(request.files)
        if 'image' not in request.files:
            msg.success = False
            msg.status = "No file part in request."
            return msg.get_msg(), 400

        img_file = request.files['image']

        if img_file:
            digit = classify_digit_in_image(img_file)
            msg.data = digit
            return msg.get_msg(), 200
        
        msg.success = False; msg.status = "File upload failed"
        return msg.get_msg(), 500
    else:
        return msg.get_msg(), 204

