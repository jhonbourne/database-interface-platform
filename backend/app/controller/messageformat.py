from flask import jsonify

class Message(object):
    def __init__(self, return_json=True):
        # When return status code together in response, do not jsonify
        self._return_json = return_json

        self.success = True
        self.status = "With access authority."
        self.data = []
        self.columns = tuple()
        self.status_code = 200

    def get_msg(self):
        msg_dict =  {key: value for key, value in self.__dict__.items()
                 if not key.startswith('_')}
        if self._return_json:
            return jsonify(msg_dict)
        else:
            return msg_dict