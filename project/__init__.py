from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_mail import Mail
from prometheus_flask_exporter import PrometheusMetrics

from extensions import socketio
from project.config import settings, mail_config
from project.application.routes import all_routes
from project.domain.authorization.auth_dal import AuthDal

mail = Mail()

main_blueprint = Blueprint('main', __name__)
main_blueprint.register_blueprint(all_routes)


def create_app():
    app = Flask(__name__)
    metrics = PrometheusMetrics(app,path='/api/metrics/system')
    app.config.from_object(mail_config)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES)
    mail.init_app(app)
    jwt = JWTManager(app)
    socketio.init_app(app)


    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        user_id = jwt_payload["sub"]
        jti = jwt_payload["jti"]
        data_state = AuthDal.has_token(user_id, jti)
        if not data_state:
            return True

        return not data_state.data

    app.register_blueprint(main_blueprint)

    return app

