from flask import Flask, jsonify
from flask_cors import CORS
from .controller.user import UserException, deal_service_info

def create_app():
    app = Flask(__name__)
    CORS(app,
         # TODO when deploying, change this to the actual frontend address
         origins=['http://localhost:3000'],
         supports_credentials=True)

    app.config.from_mapping(
        SECRET_KEY='dev'#,
        # # Ensure cookies are usable in https:
        # SESSION_COOKIE_SAMESITE=None,
        # SESSION_COOKIE_SECURE=True,
    )

    # IMPORTANT: Handle UserException globally, 
    # because this function is called in more than one blueprint
    @app.errorhandler(UserException)
    def handle_user_exception(error):
        # app.logger.error(f"Catch UserException: {str(error)}")  # 一定会打印
        return deal_service_info(error.formatted_mesage, False)

    from .controller import data, user, figure
    app.register_blueprint(user.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(figure.bp)

    return app